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

import argparse
import select
import socket
import sys
import paramiko

from pytql.tql import eprint, RemoteTQL

VERSION = "2.0"


def main():
    """Runs TQL against a remote cluster."""

    args = parse_args()
    hostname = args.hostname

    try:
        rtql = RemoteTQL(hostname=hostname, username=args.username, password=args.password)

        # This probably only works on Unix systems.  TODO add ability to detect Windows and not allow streaming.
        i, o, e = select.select([sys.stdin], [], [], 1)
        if i:
            stream_commands(rtql)
        else:
            interactive_mode(rtql)

    except socket.timeout as t:
        eprint(f"Timeout connecting to {hostname}")
    except paramiko.ssh_exception.AuthenticationException:
        eprint(f"Failed to login as {args.username} on {hostname}")


def parse_args():

    """Parses the arguments from the command line."""
    parser = argparse.ArgumentParser()

    parser.add_argument("hostname", help="IP or host name for ThoughtSpot")
    parser.add_argument("--username", default="admin", help="username for accessing ThoughtSpot from CLI")
    parser.add_argument("--password", default="th0ughtSp0t", help="password for accessing ThoughtSpot from CLI")

    args = parser.parse_args()
    return args


def stream_commands(rtql):
    """
    Streams commands from stdin, e.g. cat some_file | rtql.
    :param rtql: The remote TQL instance.
    :type rtql: RemoteTQL
    :return: None
    """
    pass


def interactive_mode(rtql):
    """
    Runs in interactive mode, prompting users for input.
    :param rtql: The remote TQL object for sending commands.
    :type rtql: RemoteTQL
    :return: None
    """
    print(f"Starting RTQL version {VERSION}")

    command = input(rtql.prompt)
    while command.lower() != "exit":
        results = rtql.run_tql_command(command=command)
        print("\n".join(results))
        command = input(rtql.prompt)


if __name__ == "__main__":
    main()