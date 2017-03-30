# Node-Metadata-Collector
Tool to collect and explore meta data collected on Linux nodes.

This project is used as part of [MIKELANGELO](http://mikelangelo-project.eu)
and can be used to collect and document performance experiments.

## Table of contents

* [Getting Started](#getting-started)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Example](#example)
  * [Collect New Data](collect-new-data)
  * [Getting Information](getting-information)
  * [Merging Data](merging-data)
* [License](#license)
* [Acknowledgements](#acknowledgements)

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development and testing purposes.

### Prerequisites

The project is written in Python and needs a Python installation on your local
machine. Further, packages form PIP are required. Please install both to have
the environment you need to develop / test / run this project.

```
For Ubuntu 16.10

sudo apt install python2.7
sudo apt install python-pip
```

### Installing

First, clone or fork the project:

```
git clone https://github.com/mikelangelo-project/node-metadata-collector.git
```

Second, install the dependency:


```
# Global for all users:
sudo -H pip install -r requirements.txt
```

```
# One user:
pip install -r requirements.txt
```

Alternately you can use a virtual environment to install the required packages.

## Example

There are two scenarios where you can use this tool.
* You are on a single machine and only want to document the state of the node. In this case you run the script local and explore the data later.
* You want to collect data from multiple machines. Then you trigger the script via ssh (or cron or with other scripts) write the output `-o [File name]` to a central file system and merge the data to have a complete overview over multiple machines.

This example will show you how you can collect meta data form the node you are
on and how to explore the meta data after the collection.  
At any point you can get help form the included help text inside the program.

```
./inventory.py -h
Usage: inventory.py [OPTIONS]

  Tool to explore meta data files.

Options:
  -H, --host TEXT      Name of the host that should be printed
  -d, --dbfile PATH    Use non default db file
  -l, --list_keys      List all stored keys
  -s, --show TEXT      Show content of key
  -c, --collect        Collect Information about this host
  -m, --merge PATH     Merge multiple JSON files in PATH into one inventory
  -o, --out_path TEXT  Path to output file.
  -h, --help           Show this message and exit.
```

### Collect New Data

If you collect the first set of data, you will end up with a data collection
of the node you are at that point. To collect the data you simply call. If you
do not use the `-o [File name]` parameter to specify a output file. The tool will also add
a additional object `structure` to the JSON file. This object can be used as
a template. If this is not needed, use the `-o [File name]` to collect data.

```
./inventory.py -c
2017-03-30 10:11:43,216 - database - WARNING - No database file found please check path: data/servers.json
2017-03-30 10:11:43,216 - database - WARNING - Parent directory [some path]/node-metadata-collector/data dose not exist.
2017-03-30 10:11:43,216 - database - INFO - creating [some path]/node-metadata-collector/data
2017-03-30 10:11:43,216 - database - INFO - creating new db file: data/servers.json
2017-03-30 10:11:43,217 - collectMetadata - INFO - getting the host name.
2017-03-30 10:11:43,218 - collectMetadata - INFO - getting network info.
2017-03-30 10:11:43,223 - collectMetadata - INFO - getting vm(s) info.
2017-03-30 10:11:43,245 - collectMetadata - INFO - getting user info.
2017-03-30 10:11:43,245 - collectMetadata - INFO - getting mounts.
2017-03-30 10:11:43,267 - collectMetadata - INFO - getting the time.
```

The inventory warns you in case there is no database at the default path, which
is `./data/servers.json`. This file is created automatically for you if it
doesn't exist yet (and the parent directory if needed) and filled with the
default information of this host.

You can specify to which file the output should go with the `-o` option like this:
```
./inventory.py -c -o test.json
2017-03-30 10:16:58,282 - collectMetadata - INFO - getting the host name.
2017-03-30 10:16:58,284 - collectMetadata - INFO - getting network info.
2017-03-30 10:16:58,286 - collectMetadata - INFO - getting vm(s) info.
2017-03-30 10:16:58,306 - collectMetadata - INFO - getting user info.
2017-03-30 10:16:58,306 - collectMetadata - INFO - getting mounts.
2017-03-30 10:16:58,327 - collectMetadata - INFO - getting the time.
```
This will give you and scripts the possibility to write the files for example
to a shared file system or in a place where you can easily retrieve
the informations.

#### `-c` vs `-c -o [path]`

* `-c`
  * writes the node information into the database
  * creates the database at the default location `./data/servers.json`
  * adds a `structure` object without any data into the database

* `-c -o path`
  * writes the node information into the database
  * creates the database to the given `[path]`

### Getting Information

First to see which hosts stored information in the data base, you can easily
list all host inside the database by using the `-l` option.

```
./inventory.py -l
Host list:
[host name]
structure
```

To see which default structure is available you can look into the `structure`
object.

```
./inventory.py -H structure
Data for structure:
{
    "collection_time": "",
    "comment": "",
    "mounts": [],
    "network": {},
    "storage": {
        "get_info": []
    },
    "users": [],
    "vms": []
}

```

To get a list of all keys inside a host you can restive the information as well.
```
./inventory.py -H structure -l
Available keys:
collection_time
comment
mounts
network
storage
users
vms
```

And if you only need a single key of a host use the
`-H [host name] -s [key name]` option.

```
./inventory.py -H structure -s storage
Data for structure storage:
{
    "get_info": []
}
```

Another valid request would be, getting a single key for all stored hosts. This
would help to find all users that can log into machines.

```
./inventory.py -l -s storage
Host: host1 Key: storage
{
    "get_info": []
}
Host: structure Key: storage
{
    "get_info": []
}
Hosts without the key: []

```

### Merging Data

You collected form multiple hosts collections with
`./inventory.py -c -o collect/[hostname].json` or something similar and would
like to merge them into a single JSON document. This would give you the
advantage that you only deal with a single file, can easily compare hosts and
it is a valid JSON object you can use it for other programs or push it
to a central database.

```
tree collect/
collect
├── host1.json
├── host2.json
└── host3.json

./inventory.py -m collect/ -o collect/merge_object.json
2017-03-30 12:03:09,877 - mergeMetadata - INFO - Reading host1.json
2017-03-30 12:03:09,877 - mergeMetadata - INFO - Reading host3.json
2017-03-30 12:03:09,877 - mergeMetadata - INFO - Reading host2.json
```

The merge is done successful and you can explore the new structure with the
`-d` option. (`-d, --dbfile PATH    Use non default db file`)

```
./inventory.py -d collect/merge_object.json -l
Host list:
host1
host2
host3
```

## License

node-metadata-collector is distributed under the Apache License 2.0 license.

## Acknowledgements

This project has been conducted within the RIA [MIKELANGELO
project](https://www.mikelangelo-project.eu) (no.  645402), started in January
2015, and co-funded by the European Commission under the H2020-ICT- 07-2014:
Advanced Cloud Infrastructures and Services programme.
