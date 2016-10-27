# For niceness on pc load
* Parse stuff without opening processes. Possible except for nvidia-smi, this will just have to loop which is possible. That should then translate to a single call.
* Switch nvidia-smi parsing to xml. way more elegant ^^:

#Robustness
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* Allow for partial parsing of data if some components fail.
* Try-catch around decode for json!

#Todo general
* Possibly augment the machine_list / user_list with other useful data. The machine list is fine I guess, for users the machines they have been logged into could be interesting?
* Parse hard disk info. How much free on work/fastwork etc.?
* Create a plotting notebook
    * Input is time start and time end
    * Fetch all relevant
    * Plot, over time: cpu_load, gpu_loads, mem_load(max in legend), swap_load(max in legend)
    * Plot, over time: gpu_mem per user (max somewhere)
    * Make the above a function so it can easily be done for several machines
    * Think about changes max etc could change!
    * Change report across time!