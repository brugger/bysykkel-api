#!/home/brugger/projects/citybike/venv/bin/python3.7


import argparse
import sys


import pprint as pp
import re

from kbr import config_utils
from tabulate import tabulate
from urllib.parse import urlparse

import kbr_api.auth_db  as auth_db
import kbr.string_utils as string_utils
import kbr.args_utils as args_utils
import kbr.password_utils as password_utils
import kbr.db_utils as db_utils
import bysykkel.db as bysykkel_db


def main():

    commands = ['stations', 'status', 'trip', 'help']


    parser = argparse.ArgumentParser(description='bysykkel_import: importing data')


    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")

    parser.add_argument('-p', '--port', help="Port to bind to")
    parser.add_argument('-v', '--verbose', default=4, action="count",  help="Increase the verbosity of logging output")
    parser.add_argument('command', nargs='+', help="{}".format(",".join(commands)))

    args = parser.parse_args()

    config = config_utils.readin_config_file( args.config )

    if args.port:
        config.server.port = args.port


    if 'database' in config:
        global db
        db = bysykkel_db.DB()
        db.connect( config.database )


    args_utils.count(1, len(args.command), msg="import take one of the following commands: {}".format(string_utils.comma_sep( commands )))

    command = args.command.pop(0)
    if command not in commands:
        parser.print_help()

    if command == 'stations':
        args_utils.count(1, len(args.command), msg="import stations require a filename")
        import_stations(args.command.pop)
    elif command == 'status':
        args_utils.count(1, len(args.command), msg="import status require a filename")
        import_status(args.command.pop)
    elif command == 'trips':
        args_utils.count(1, len(args.command), msg="import trips require a filename")
        import_trips(args.command.pop)
    else:
        print("The tool support the following commands: {}".format(string_utils.comma_sep( commands )))
        sys.exit( 1 )


if __name__ == "__main__":
    main()

