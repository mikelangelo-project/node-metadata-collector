CollectMetadata.py collects interesting informations about one node.

- env -> environment
- packages -> installed packages and there version
- processes -> running processes and there pid
- time -> time of the collection
- cpu -> informations about the cpu
- mpi -> self build mpi version and path to mpirun
- hostname -> the network hostname of the node

the root of the JSON is
```
{nodename: {env: {}, packages: {} .......}}
```
Example:
```
./collectMetadata.py [directory to write the file]  
the file name will be [directory to write the file]/[nodename].JSON
```

If you have no mpi or don't want to collect a metric, delete the line.  
collectMetadata.py -> 86 or -> 87

Packages to install (with pip):
- cpuinfo
- platform
- psutil
- sh

mergeMetadata.py if more then one node should be merged into one file

Example:
```
mergeMetadata.py [json_dirctory] [job_id] [out_path]
        JSON_dirctory = the path to the directory containing the JSON files
        job_id = the id of the job (you can choos this free)
        out_path = the file where the merged JSON gets written to
```
The resulting JSON will look like:
```
{jobid: {nodename1: {env: {}, packages: {} .......}, nodename2: {env: {}, packages: {} .......}}}
```

## License

node-metadata-collector is distributed under the Apache License 2.0 license.

## Acknowledgements

This project  has been conducted within the RIA [MIKELANGELO
project](https://www.mikelangelo-project.eu) (no.  645402), started in January
2015, and co-funded by the European Commission under the H2020-ICT- 07-2014:
Advanced Cloud Infrastructures and Services programme.
