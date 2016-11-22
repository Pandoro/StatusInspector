# For niceness on pc load
* Parse stuff without opening processes. Possible except for nvidia-smi, this will just have to loop which is possible. That should then translate to a single call.
* Switch nvidia-smi parsing to xml. way more elegant ^^:

#Robustness
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* Allow for partial parsing of data if some components fail.
* Try-catch around decode for json!