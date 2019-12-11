#!/usr/bin/env python3



import argparse
import datetime

import sys
import os
import time

os.environ['TZ'] = 'Europe/Oslo'
time.tzset()


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


def datestr_to_epoch(timestamp:str) -> []:

    try:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    except:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z")

    return ts.timestamp()



def day_blocks(ts:str) -> {}:

    dts = int(day_epoch(ts))
    blocks = {}
    for i in range(dts, dts+24*60*60, 300):
        blocks[ i ] = 0
    return blocks


def epoch_to_timestr(time:int):
    ts = datetime.datetime.fromtimestamp(time)
    return ts

def five_min_block(time:int):
    return 300*int( time/300 )


def day_epoch(ts:int) -> int:
    timestamp = datetime.datetime.fromtimestamp(ts)
    stime = "{}-{}-{} 00:00:00".format( timestamp.year, timestamp.month, timestamp.day )

    return datetime.datetime.strptime(stime, "%Y-%m-%d %H:%M:%S").timestamp()

def weekday(timestamp:str) -> []:

    try:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f%z")
    #        return ts.weekday(), ts.hour, ts.minute
    except:
        ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z")

    return ts.weekday(), ts.hour, ts.minute



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



def print_stations():
    table = []
    for station in db.stations(order='name'):
        table.append( [station['id'], station['station_id'], station['name']])

    headers = ['id', 'station-id', 'name']
    print(tabulate(table, headers, tablefmt="psql"))
    return

def print_station( id:str) -> None:
    print(','.join(['date', 'weekday', 'bikes', 'docks']))
    for station in db.status(station_id=id, order='timestamp'):
        timestamp = epoch_to_timestr(station['timestamp'])
        st = [timestamp, timestamp.weekday(), station['bikes_available'], station['docks_available']]
        print(",".join(map(str, st)))

def print_trips_to(station_id:str):

    prev_timestamp = None
    count = None

    print(','.join(['date', 'weekday', 'bikes']))

    blocks = {}
    for station in db.trips(end_station_id=station_id, order='end_time'):
        timestamp = five_min_block( station['end_time'] )
        if timestamp not in blocks:
            for block in blocks:
                print("{},{},{}".format(epoch_to_timestr(block), 0, blocks[ block]))
            #return
            #print( "TS",timestamp )
            blocks = day_blocks(timestamp)
            #pp.pprint( blocks )

        try:
            blocks[ timestamp ] += 1
        except:
            pass
#        if prev_timestamp != timestamp:
#            if prev_timestamp is None:
#                prev_timestamp = timestamp
#                count = 0
#            else:
#                ts = epoch_as_timestr(prev_timestamp)
#                st = [ts, ts.weekday(), count]
#                print(",".join(map(str, st)))
#                prev_timestamp = timestamp
#                count = 0



    for block in blocks:
        print("{},{},{}".format(epoch_to_timestr(block), 0, blocks[ block]))



#    ts = epoch_as_timestr(prev_timestamp)
#    st = [ts, ts.weekday(), count]
#    print(",".join(map(str, st)))


def print_trips_from(station_id:str):

    print(','.join(['date', 'weekday', 'bikes']))
    for station in db.trips(start_station_id=station_id, order='start_time'):
        timestamp = epoch_to_timestr(station['start_time'])
        st = [timestamp, timestamp.weekday(), 1]
        print(",".join(map(str, st)))


def main():

    commands = ['stations', 'station', 'trips_to', 'trips_from','help']


    parser = argparse.ArgumentParser(description='bysykkel exporter: importing data')


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
        print_stations()
    elif command == 'station':
        args_utils.count(1, len(args.command), msg="station require a station id")
        print_station(args.command.pop(0))
    elif command == 'trips_to':
        args_utils.count(1, len(args.command), msg="trips_to require a station id")
        print_trips_to(args.command.pop(0))
    elif command == 'trips_from':
        args_utils.count(1, len(args.command), msg="trips_from require a station id")
        print_trips_from(args.command.pop(0))
    else:
        print("The tool support the following commands: {}".format(string_utils.comma_sep( commands )))
        sys.exit( 1 )


if __name__ == "__main__":
    main()

