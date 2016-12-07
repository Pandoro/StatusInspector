# Multi Machine Network Status Collector
This is a little tool I wrote some time back to keep track of what everyone in our lab is doing with their machines and to log this info to a MongoDB. This information can then be visualized and used for whatever purpose you can think of. In my case, I wanted to check the GPU load on the other machines. That is why this tool is mainly geared towards keeping track of NVIDIA GPUs and it requires nvidia-smi and proper drivers to be installed. The other important prerequisite is that you can SSH to all machines without entering a password.

## Getting Started
First of all set some paths and a list of machines in the config file. An example is given in the `example_config.json`. You should specify a path for the mongodb to be stored to, a path for a custom log file to be written to and a list of machine you want to keep track of. You can also specify logging intervals (in minutes). Detailed information should (can) be parsed more often, general machine info like OS and hardware can be logged less frequently since it will not change as often.

Start the collector by running:
```bash
python status_collector.py -c config.json
```

This process will run the mongodb for you and create one if it is the first time you run it. Keep this process alive since it does all the bookkeeping and triggers the other machines to report data back. If you want to stop further logging, just press `Ctrl+c` and give it some time to cleanly finish everything.

## How does it work?
The status collector will time an event for every machine you are logging info for. Once a logging event is triggered, the machine running the collector will ssh to the machine from which data should be gathered at this point and tell it to run the `local_stat_parser.py` script. If this is not present, the remote machine is prompted to fetch it from the current folder via scp. This script runs for several minutes and averages some statistics over time. These are then serialized into a json string and returned via the ssh connection. The status collector then writes this info to the MongoDB. Using the provided Jupyter Notebook you can see an example of how to visualize the data, but you can read out the data from the MongoDB in whatever way you like. Clearly all of this only works on linux machines. I tested it on a mix of Ubuntu 14.04 and 12.04 systems.

##TODO
This was a little hobby project, mainly intended to get some experience with the different required parts. There are some major TODOs. However, it is functional as it is. It might not be optimal, but it ran for about a month fetching data from over 30 machines, without anybody detecting an increased system load, or detecting the whole system at all for that matter.

### Fetching the data
The script currently runs several shell commands and parses their output with regular expressions. Since I use zsh these might not even work in bash. Most of the required information should be retrievable via reading out system files or for the GPU stats there is [pyNVML](https://developer.nvidia.com/nvidia-management-library-nvml). This should also be a little nicer on the remote system load.

### Triggering the fetching of data
Currently the main process tells the machines to log the data over an ssh connection. It would clearly be better to run a daemon on every machine that either logs the data by itself and directly connects to the MongoDB. An alternative is to keep the timing control in the main process, but to use a daemon on all machines with an open socket to which the main process can connect to trigger the data collection. In both cases the SSH connection is avoided completely.

### Data aggregation in the MongoDB
While my MongoDB didn't explode during my one month trial, it did grow and on the long run, it will become an issue. I'm planning to have an automatic data aggregation scheme, where data at some point is summarized. Data older than a month could for example be reduced to an hourly summary, data older than a year could be summarized to complete days, etc.

### Better visualization
Currently for my purposes I had a little notebook showing me what I wanted to know. For anything further a neat little web based representation could be nice, but that is a far future todo.

### Additional minor TODOS
* Make calls time out and store no info. If the machine is down or full this will otherwise block further execution.
* Allow for partial parsing of data if some components fail.
* Try-catch around decode for json!
* Extend with some further parsing.

## But all of this exists!
Yes I know, there are super professional tools for this. From what I saw none of them did exactly what I wanted. What I like about this solution, is that if you have unlimited ssh access, you can install pymongo and MongoDB on your machine and all other machines just need very basic python packages which are likely installed anyway (the biggest problem might be json). I can store this data in exactly the representation and interval I want and I don't need to install anything special. Clone this repo and you are pretty much good to go! And as I said before, it was also a fun little project for me, that hopefully I can pursue a little further in the near future.

## License
The MIT License (MIT)

Copyright (c) 2016 Alexander Hermans

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
