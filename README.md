# Python-TQL

This package contains data to make working with ThoughtSpot Query Langague (TQL) easier when writing scripts that 
interact with TQL.

Currently it only consists of libraries that can be used by other 

## Setup

This section will walk you through how to set up the environment to get started with the Python TQL.

### Environment

These tools have all been written in Python 3.7 and expect to be run in a 3.6 environment at a minimum.

You can either install directly into an existing Python environment, but it's better to run in an virtual environment 
to avoid conflicts with dependencies.  py-tql relies on other packages to run.  Note that this installation 
process requires external access to install packages and get the py-tql code from GitHub.

To create a virtual environment, you can run the following from the command prompt:

`$ virtualenv -p python3 ./venv`

Note that the `venv` folder can be whatever name and location you like (preferably external to a code repository).

Next, you need to activate the environment with the command: 

`$ source ./venv/bin/activate`

Note that you will need to reactivate the environment whenever you want to use it.  

You should see your prompt change to (venv) plus whatever it was before.  To verify the python version run:

`$ python --version`  You want to be on version 3.6 or higher.

If you want to leave the virtual environment, simple enter `$ deactivate` or close the terminal you are using.

See https://virtualenv.pypa.io/en/latest/ for more details on using virtualenv.

## Downloading and installing the Python TQL

Now that you have an environment for installing into you can install directly from GitHub with the command:

`$ pip install git+https://github.com/thoughtspot/py-tql`.  

You should see output as the py-tql and dependencies are installed.  

If you want or need to update to a newer version of the Python TQL, use the command:

`$ pip install --upgrade git+https://github.com/thoughtspot/py-tql`.  

