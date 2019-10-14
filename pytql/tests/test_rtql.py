import unittest

from pytql.model import Row, DataTable
from pytql.tql import RemoteTQL

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

TEST_HOSTNAME = "tstest"
TEST_USERNAME = "admin"
TEST_PASSWORD = "somepassword"


class TestRemoteTQL(unittest.TestCase):
    """Test case for testing remote TQL."""

    def setUp(self) -> None:
        """Returns a new TQL shell."""
        self.rtql = RemoteTQL(hostname=TEST_HOSTNAME, username=TEST_USERNAME, password=TEST_PASSWORD)

    def tearDown(self) -> None:
        """Returns a new TQL shell."""
        del self.rtql

    def test_get_databases(self):
        databases = self.rtql.get_databases()

        # check for a couple of known DBs.  Not exhaustive.
        self.assertIn("thoughtspot_internal_stats", databases)
        self.assertIn("thoughtspot_internal", databases)

    def test_get_data(self):
        """Tests making a data query."""
        self.rtql.run_tql_command("CREATE DATABASE foo;")
        self.rtql.run_tql_command("USE foo;")
        self.rtql.run_tql_command("CREATE TABLE foo (col1 int, col2 varchar(0));")
        self.rtql.run_tql_command("DELETE FROM foo;")  # make sure empty.
        for row in range(1, 4): # creates three rows 1-3
            self.rtql.run_tql_command(f"INSERT INTO foo VALUES ({row}, 'value_{row}');")

        table = self.rtql.execute_tql_query("SELECT * FROM foo;")

        self.assertEqual(2, table.nbr_columns())
        self.assertEqual(3, table.nbr_rows())

        self.rtql.run_tql_command("DROP DATABASE foo;")
