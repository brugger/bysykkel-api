#!/usr/bin/env python3



import argparse
import datetime

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
import kbr.json_utils as json_utils


def date_as_epoch(timestamp:str) -> []:

    try:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    except:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z")

    return ts.timestamp()


stations = {}
def get_station_id( station_id:int, name:str, lat:float, lon:float):
    global stations

    if stations == {}:
        for station in db.stations():
            stations[ station[ 'station_id']] = station[ 'id' ]

    if station_id in stations:
        return stations[ station_id ]

    print( "adding station {}".format( station_id))
    db.station_add( station_id=station_id, name=name, lat=lat, lon=lon, capacity=0)

    for station in db.stations():
        stations[ station[ 'station_id']] = station[ 'id' ]


    return stations[ station_id ]



def import_stations( filename:str) -> None:
    data = json_utils.read( filename )
    for entry in data['data']['stations']:
        db.station_add( station_id=entry['station_id'], name=entry['name'], lat=entry['lat'], lon=entry['lon'], capacity=entry['capacity'])


def import_status( filename:str) -> None:
    data = json_utils.read( filename )

    global stations

    for station in db.stations():
        stations[ station[ 'station_id']] = station[ 'id' ]


    for entry in data['data']['stations']:
        db.status_add( station_id=stations[int(entry['station_id'])], bikes_available=entry['num_bikes_available'],
                       docks_available=entry['num_docks_available'], timestamp=entry['last_reported'])


def import_trips( filename:str) -> None:
    data = json_utils.read( filename )

    station_ids = {}
    for station in db.stations():
        station_ids[ station[ 'station_id']] = station[ 'id' ]

    for entry in data:
#        print( entry )
        start_station_id = get_station_id( int(entry['start_station_id']), name=entry['start_station_name'],
                                           lat=entry['start_station_latitude'], lon=entry['start_station_longitude'])

        end_station_id = get_station_id( int(entry['end_station_id']), name=entry['end_station_name'],
                                         lat=entry['end_station_latitude'], lon=entry['end_station_longitude'])

        db.trip_add( start_station_id=start_station_id,
                     end_station_id=end_station_id,
                     start_time=int(date_as_epoch(entry['started_at'])),
                     end_time=int(date_as_epoch(entry['ended_at'])) )

def main():

    commands = ['stations', 'status', 'trips', 'help']


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


    args_utils.min_count(1, len(args.command), msg="import take one of the following commands: {}".format(string_utils.comma_sep( commands )))

    command = args.command.pop(0)
    if command not in commands:
        parser.print_help()

    if command == 'stations':
        args_utils.count(1, len(args.command), msg="import stations require a filename")
        import_stations(args.command.pop(0))
    elif command == 'status':
        args_utils.count(1, len(args.command), msg="import status require a filename")
        import_status(args.command.pop(0))
    elif command == 'trips':
        args_utils.count(1, len(args.command), msg="import trips require a filename")
        import_trips(args.command.pop(0))
    else:
        print("The tool support the following commands: {}".format(string_utils.comma_sep( commands )))
        sys.exit( 1 )


if __name__ == "__main__":
    main()

