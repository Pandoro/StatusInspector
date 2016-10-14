#!/usr/bin/env python

from optparse import OptionParser
import sys
import os
import json
import time
import threading
import subprocess
import getpass
import pymongo


#As shown here: http://stackoverflow.com/questions/2398661/schedule-a-repeating-event-in-python-3
#Extended to run the task directly at the start once (execute_at_start=True).
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self, execute_at_start=True):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.setDaemon(True)
            if execute_at_start:
                self.function(*self.args, **self.kwargs)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class InfoFetcher(object):
    def __init__(self, machine_list, detailed_minute_interval, general_minute_interval, script_destionation, script_location):
        self.machine_list = machine_list
        self.detailed_minute_interval = detailed_minute_interval
        self.general_minute_interval = general_minute_interval
        self.script_destionation = script_destionation
        self.script_location = script_location
        self.local_machine = os.uname()[1]

        self.lock = threading.Lock()
        self.detailed_scheduler = RepeatedTimer(60*detailed_minute_interval, self.get_all_machine_info, self.machine_list)
        self.general_scheduler = RepeatedTimer(60*general_minute_interval, self.get_all_machine_info, self.machine_list, only_general_info=True)


    def get_single_machine_info(self, machine, only_general_info=False):
        #The command checks if the script is in place. If it is missing it will fetch it again and execute it.
        command = ('ssh -o StrictHostKeyChecking=no {} \''.format(machine) +
                            '[ ! -f {} ] && '.format(self.script_destionation) +
                                'scp {}:{} {}; '.format(self.local_machine, self.script_location, self.script_destionation) +
                            'python {}{}\''.format(self.script_destionation, ' -g' if only_general_info else ''))
        info_raw = subprocess.check_output(command, shell=True).decode('UTF-8')

        #Decode the json string.
        info = json.loads(info_raw)

        #Write it to the MongoDB
        self.lock.acquire()
        #TODO
        print(machine, info)
        self.lock.release()


    def get_all_machine_info(self, machine_list, only_general_info=False):
        #Spawn a thread for each machine and run the ssh query
        thread_list = []

        for m in machine_list:
            thread_list.append(threading.Thread(target=self.get_single_machine_info, args=(m,), kwargs={'only_general_info' : only_general_info}))
            thread_list[-1].setDaemon(True)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()


def main(argv):
    #Get all options
    parser = OptionParser()
    parser.add_option('-c','--config', action='store', dest='config_file',
                      help='The config file specifying polling times, db location and machine list. This should be a json file.')
    parser.add_option('-o','--overwrite', action='store_true', dest='overwrite_config_file',
                      help='If this is set, the local stat parsing script is pushed to all machines at the start. Normally it would only be fetched if it was missing.')
    parser.add_option('-p','--passwd', action='store', dest='passwd',
                  help='If provided this password is used instead of querying the password at runtime.')
    (options, args) = parser.parse_args(argv)

    #Force the parameter file "option" ^^;
    if options.config_file is None:
        parser.error("No Config file was provided.")

    #Load the params
    with open(options.config_file, 'r') as config_file:
        config = json.load(config_file)
    machine_list = config['machine_list']
    detailed_minute_interval = config['general']['detailed_minute_interval']
    general_minute_interval = config['general']['general_minute_interval']
    local_script_destination = config['general']['local_script_destination']
    script_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),'local_stat_parser.py')
    script_destionation = os.path.join(local_script_destination,'local_stat_parser.py')
    mongodb_path = config['mongo_db']['database_path']
    mongodb_port = config['mongo_db']['port']
    connection_retries = config['mongo_db']['connection_retries']
    connection_waits = config['mongo_db']['connection_waits']

    #Check if the mongodb path exists.
    if not os.path.exists(mongodb_path):
        os.makedirs(mongodb_path)

    #Check if a mongo is running on our port already. If that is the case, the user needs to stop that first.
    running = False
    try:
        mongo_client = pymongo.MongoClient(host='localhost', port=mongodb_port)
        running = True
    except pymongo.errors.ConnectionFailure:
        pass
    if running:
        print('A MongoDB is running on port {}. We always start our own. Choose a different port or kill the other MongoDB.'.format(mongodb_port))
        exit()

    #Start the actual MongoDB server
    mongod = subprocess.Popen(['mongod', '--port', str(mongodb_port), '--dbpath', mongodb_path, '--auth'], stdout=subprocess.PIPE)

    #We allow for some extra waiting time and try connecting several times
    tries = 1
    connected = False
    while tries <= connection_retries:
        print('Connecting to MongoDB[:{}], try {}/{}...'.format(mongodb_port,tries,connection_retries)),
        sys.stdout.flush()
        time.sleep(connection_waits)
        try:
            mongo_client = pymongo.MongoClient(host='localhost', port=mongodb_port)
        except pymongo.errors.ConnectionFailure:
            tries +=1
            print('failed')
            continue
        print('succeeded')
        connected = True
        break
    if not connected:
        mongod.terminate()
        print('Failed to connect to database. Exiting!')
        exit()

    #Now we have to find out if this was a new MongoDB or if it is an old one.
    #If we can access it without a password, this was freshly setup.
    pwd_protected = True
    try:
        mongo_client['admin'].collection_names()
        pwd_protected = False
    except pymongo.errors.OperationFailure:
        pass

    if not pwd_protected:
        #Let's set a password.
        match = False
        while not match:
            new_mongo_password = getpass.getpass('Created a new MongoDB. Please enter a password: ')
            new_mongo_password2 = getpass.getpass('Please re-enter the password: ')
            match = (new_mongo_password == new_mongo_password2)
            if not match:
                print('Passwords didn\'t match.')

        mongo_client['admin'].add_user('admin', new_mongo_password)
        print('Password set, reconnecting now.')
        mongo_client.close()
        mongo_client = pymongo.MongoClient(host='localhost', port=mongodb_port)


    #Get the mongo password one way or the other
    if options.passwd is None:
        mongo_password = getpass.getpass('Please enter the MongoDB password: ')
    else:
        mongo_password = options.passwd

    #Authenticate.
    try:
        mongo_client['admin'].authenticate('admin',mongo_password)
        print('Password correct, connected to the MongoDB.')
    except pymongo.errors.OperationFailure:
        print('Apparently that was the wrong password! Exiting!')
        mongod.terminate()
        exit()

    #Mainly here so we can quickly overwrite all the scripts if it needs to be redeployed.
    if options.overwrite_config_file:
        print('Pushing fresh script to all machines... '),
        sys.stdout.flush()
        for m in machine_list:
            subprocess.check_output('scp -o StrictHostKeyChecking=no {} {}:{}'.format(script_location, m, script_destionation), shell=True)
        print('Done')

    #Create an info fetcher that does all the work
    fetcher = InfoFetcher(machine_list, detailed_minute_interval, general_minute_interval, script_destionation, script_location)

    #Loop. What would be a good value here?
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1:])