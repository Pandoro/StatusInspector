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

# To think of
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* Switch nvidia-smi parsing to xml. way more elegant ^^:
* use free -m for memory stats instead of meminfo
* prevent threads from being killed when somebody is writing to the database probably overwrite the ctrl-c and have it aquire a lock before being killed.
* Log mongodb output to a file.