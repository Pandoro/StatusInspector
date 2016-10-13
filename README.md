# Config file
* base info
* machine names
* mongo db info
* polling frequency 10 mins?
* scp the script to a specific location.

# Running
Every n minutes
ssh to all machines
Parse all info and store in db

# To store
* nvidia driver
* GPU Model (nvidia-smi -q | grep 'Product Name'
* ubuntu version
* max Ram usage
* max Swap usage
* max GPU ram usage for each user if supported
* max GPU processing usage if available
* max CPU usage
* Temperature

# Setup script
* Create the mongo.


# To think of
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* All calls at once?
* What about multi GPU?
* Put everything into a script that it copied over once at the start.
* Switch nvidia smi parsing to xml. way more elegant ^^:
