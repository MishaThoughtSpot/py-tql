# PythonTQL

This package contains data to make working with ThoughtSpot Query Langague (TQL) easier when writing scripts that 
interact with TQL.

This package includes both the Python APIs that you can use in programs and a script for running 
TQL from a remote machine.

## Setup

PythonTQL is installed with the same process as other TS Python tools.

You can install using `pip install --upgrade git+https://github.com/thoughtspot/py-tql`

See the general [documentation](https://github.com/thoughtspot/tree/master/python_tools) on setting 
up your environment and installing using `pip`.

## Scripts

### rtql

`rtql` is a script that allows you to interact with TQL on a remote cluster.  It provides an interface similar to the 
TQL interface you find on the cluster.  You can either stream command or run interactively.  Type "exit" to leave the
interactive mode.

NOTE:  This script is not currently tested on Windows and may not work.

~~~
usage: rtql.py [-h] [--username USERNAME] [--password PASSWORD] hostname

positional arguments:
  hostname             IP or host name for ThoughtSpot

optional arguments:
  -h, --help           show this help message and exit
  --username USERNAME  username for accessing ThoughtSpot from CLI
  --password PASSWORD  password for accessing ThoughtSpot from CLI
~~~
