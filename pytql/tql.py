import logging
import os
import paramiko
import re
import socket
import sys
import shlex
import subprocess
import time

from .model import DataTable

"""
Copyright 2019 ThoughtSpot
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
This module contains the class for interacting with TQL.
"""


def eprint(*args, **kwargs):
    """
    Prints to standard error similar to regular print.
    :param args:  Positional arguments.
    :param kwargs:  Keyword arguments.
    """
    print(*args, file=sys.stderr, **kwargs)


class TQL:
    """
    Wraps the TQL interface.  Note that this class expects to run on the ThoughtSpot cluster and have tql in the path.
    """

    COLUMN_SEPARATOR = "|"  # TQL uses pipes to separate output columns.
    COMMAND = "/usr/local/scaligent/release/bin/tql -query_results_apply_top_row_count=-1"

    # TQL specific queries.
    SHOW_DATABASES = "show databases;"

    def __init__(self):
        """
        Creates a new TQL interface.
        """
        pass

    def get_databases(self):
        """
        Returns a list of the databases.
        :return: A list of all the database commands.
        """
        out, err = self._execute_query(query=TQL.SHOW_DATABASES)

        tables = []
        for table in out:
            tables.append(table.strip())

        return tables

    def execute_tql_query(self, query):
        """
        Executes a TQL query and returns the data as a data table.
        :param query: A complete query to send to TQL.
        :type query: str
        :return: A data table with the results.
        :rtype: DataTable
        """
        out, err = self._execute_query(query=query)

        table = DataTable()

        # The header should be in the first row that contains pipes.
        header = None
        for line in err:
            if query in line:
                continue

            # The first line is the command.  The next line is the header.
            splitter = shlex.shlex(line, posix=True)
            splitter.whitespace = TQL.COLUMN_SEPARATOR
            splitter.whitespace_split = True
            splitter.commenters = ''
            splitter.quotes = '"'
            header = list(splitter)
            break

        if header:
            table._header = header

        for line in out:
            splitter = shlex.shlex(line, posix=True)
            splitter.whitespace = TQL.COLUMN_SEPARATOR
            splitter.whitespace_split = True
            splitter.commenters = ''
            splitter.quotes = '"'
            data = list(splitter)
            table.add_row(row=data)

        return table

    @staticmethod
    def _execute_query(query):
        """
        Executes the query and returns the standard out and standard error received from TQL.
        :param query: The query to execute.
        :type query: str
        :return: The results of the query.
        :rtype list of str,str
        """
        # TODO add more error checking.
        query = query.strip()

        # make sure a semi-colon was included.
        if not query.endswith(';'):
            query += ";"

        tql_file = "/tmp/tql.%s" % time.time()
        with open(tql_file, "w") as cmdfile:
            cmdfile.write(query)

        command = "cat '" + tql_file + "' | " + TQL.COMMAND
        logging.debug(command)

        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        os.remove(tql_file)  # bit of cleanup.

        logging.debug("==================================================================")
        logging.debug(out)
        logging.debug("==================================================================")
        logging.debug(err)
        logging.debug("==================================================================")

        # This isn't perfect if there is an error that doesn't have the text "error=" in it.
        if "error=" in err:
            raise Exception("Error from TQL: %s", err)

        stdout = out.decode("utf-8", "ignore").split('\n')
        # usually get a blank line that isn't needed.
        try:
            stdout.remove('')
        except ValueError:
            pass  # might not be there.

        stderr = err.decode("utf-8", "ignore").split('\n')
        # usually get a blank line that isn't needed.
        try:
            stderr.remove('')
        except ValueError:
            pass  # might not be there.

        return stdout, stderr


class RemoteTQL(TQL):
    """
    Provides a remote access to TQL via an SSH session.
    """

    def __init__(self, hostname, username=None, password=None, **kwargs):
        """
        Creates a remote session to TQL.
        """
        print(f"Starting remote TQL to host {hostname}")

        self.prompt = None # nice prompt to use.
        self._set_prompt(database="none")
        self.hostname = hostname

        self.__ssh_client = paramiko.SSHClient()
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__ssh_client.load_system_host_keys()
        self.__ssh_client.connect(hostname=hostname, username=username, password=password, timeout=10, **kwargs)

        self._channel = self.__ssh_client.invoke_shell()
        self._connect_to_tql()

        super(RemoteTQL, self).__init__()

    def _set_prompt(self, partial=False, database=None, data=None):

        if partial:
            self.prompt = "$> "
        else:
            if database:
                pass  # use the database, but don't do other checks.
            elif data:
                m = re.search("\[database=(.*)\]", data)
                if m:
                    database = m.group(1)
            else:
                database = "none"

            self.prompt = f"rtql [database=({database})] > "

    def _connect_to_tql(self):
        """
        Opens TQL using the SSH connection.
        :return: None
        """
        # start the TQL session.
        # TODO disabling comments, but may want to make a parameter.
        self._channel.send("tql -script_comments=false\n")
        response = self._get_tql_response()
        print("\n".join(response))

    def execute_tql_query(self, query):
        """
        Executes a TQL query and returns the data as a data table.
        :param query: A complete query to send to TQL.
        :type query: str
        :return: A data table with the results.
        :rtype: DataTable
        """
        pass

    def run_tql_command(self, command):
        """
        Runs a command in TQL and returns the results as a list of strings..
        :param command: The command to run.
        :type command: str
        :return: The data from the command as a list.
        :rtype: list of str
        """
        self._channel.send(command)
        self._channel.send("\n")

        return self._get_tql_response()

    def _get_tql_response(self):
        """
        Waits for a response to a command and returns as a list.  The TQL prompt is not returned.
        :return: The list of values back from TQL.
        :rtype: list of str
        """
        data = ""
        full_command = False
        partial_command = False
        while (not full_command) and (not partial_command):

            while self._channel.recv_ready():
                data += str(self._channel.recv(9999))
                print(data)

            if re.search("TQL \[database=", data):
                full_command = True
                self._set_prompt(data=data)
            elif re.search("\$> ", data):
                self._set_prompt(partial=True)
                partial_command = True
            else:
                time.sleep(1)  # give it time to work.


        data = data.replace("\\r", "")
        data = data.split("\\n")
        data = data[1:-1]  # first is the command, last is the prompt.

        return data

    def __del__(self):
        """
        Ends the remote TQL session.
        :return: None
        """
        print(f"{self.prompt} closing connection to {self.hostname}")
        self.__ssh_client.close()


# TODO move to an application.
if __name__ == "__main__":
    tql = TQL()
    # send the command.  Wrap in quotes if it has spaces.
    tql.execute_tql_query(sys.argv[1])
