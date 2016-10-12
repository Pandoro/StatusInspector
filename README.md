# Config file
* base info
* machine names
* mongo db info
* polling frequency 10 mins?

# Running
Every n minutes
ssh to all machines
Parse all info and store in db

# To store
* nvidia driver
* GPU Model
* ubuntu version
* max Ram usage
* max Swap usage
* max GPU ram usage for each user if supported
* max GPU processing usage if available
* max CPU usage

# To think of
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* All calls at once?
* What about multi GPU?
