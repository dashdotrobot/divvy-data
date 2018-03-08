#!/usr/bin/env python

'Get average hourly bike counts for Divvy stations'

import os.path
import sodapy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import smopy


def get_num_trips_to(stat_id):
    'Get number of trips TO station stat_id in 2017'

    r = api.get(d_trips, select=("count(trip_id)"),
                where=("to_station_id='{:d}'".format(stat_id) +
                       "and stop_time between '2017-01-01' and '2017-12-31'"))

    return int(r[0]['count_trip_id'])


def get_num_trips_from(stat_id):
    'Get number of trips FROM station stat_id in 2017'

    r = api.get(d_trips, select=("count(trip_id)"),
                where=("from_station_id='{:d}'".format(stat_id) +
                       "and start_time between '2017-01-01' and '2017-12-31'"))

    return int(r[0]['count_trip_id'])


def get_hourly_counts(stat_id, dirxn):
    'Get number of trips per hour (0-23) to or from a station'

    # Get all trips TO this station in 2017
    r = api.get(d_trips, select=("count(trip_id), " +
                                 "date_extract_hh({:s}_time) as hour".format(dirxn[1])),
                where=("{0:s}_station_id='{3:d}' " +
                       "and {1:s}_time between '2017-01-01' and '2017-12-31' " +
                       "and date_extract_dow({1:s}_time) in ({2:s})")\
                       .format(dirxn[0], dirxn[1], ','.join(str(d) for d in days_to_count),
                               stat_id),
                group="hour")

    df_r = pd.DataFrame.from_records(r).astype('int').set_index('hour')

    df_T = pd.DataFrame(df_r.transpose().to_dict())
    df_T.index = [stat_id]

    return df_T


data_url = 'data.cityofchicago.org'
app_token = '6xUrAQkGuIctuyUrTEdLZZFRY'
d_trips = 'fg6s-gzvg'
d_stats = 'aavc-b2wj'

api = sodapy.Socrata(data_url, app_token)


if not os.path.exists('stations_trip_counts.csv'):

    r = api.get(d_stats)

    cols = ['id', 'address', 'docks_in_service',
            'latitude', 'longitude', 'station_name', 'total_docks']
    df_stats = pd.DataFrame.from_records(r, columns=cols)

    # Convert data types
    df_stats[['id', 'docks_in_service', 'total_docks']] =\
        df_stats[['id', 'docks_in_service', 'total_docks']].astype(int)

    df_stats[['latitude', 'longitude']] =\
        df_stats[['latitude', 'longitude']].astype(float)

    df_stats.set_index('id', inplace=True)

    # Get number of trips TO each station in 2017
    df_stats['num_trips_to'] = 0
    df_stats['num_trips_from'] = 0

    for stat_id in df_stats.index:
        # Get number of trips TO this station in 2017
        print 'TRIP COUNTS FOR STATION: {:d}'.format(stat_id)

        df_stats.at[stat_id, 'num_trips_to'] = get_num_trips_to(stat_id)

        # Get number of trips FROM this station in 2017
        df_stats.at[stat_id, 'num_trips_from'] = get_num_trips_from(stat_id)

    # Save scraped station information
    df_stats.to_csv('stations_trip_counts.csv')
else:
    print 'LOAD TRIP COUNTS FOR STATIONS'
    df_stats = pd.read_csv('stations_trip_counts.csv', index_col='id')

print df_stats.head()

if not os.path.exists('stations_hourly_wd_to_counts.csv'):
    df_counts = pd.DataFrame()

    days_to_count = [1, 2, 3, 4, 5]
    dirxn = ('to', 'stop')

    for stat_id in df_stats.index:

        success = False
        n_tries = 0
        while not success and n_tries < 5:
            try:
                df_counts = df_counts.append(get_hourly_counts(stat_id, dirxn))
                success = True
            except Exception as e:
                print '   ## ERROR ON STATION: {:d}'.format(stat_id)
                print '   ## {:s}'.format(e)
                n_tries = n_tries + 1

    df_wk_to_counts = df_counts.fillna(0)

    # Save weekday trip information
    df_wk_to_counts.to_csv('stations_hourly_wd_to_counts.csv')

if not os.path.exists('stations_hourly_wd_from_counts.csv'):
    df_counts = pd.DataFrame()

    days_to_count = [1, 2, 3, 4, 5]
    dirxn = ('from', 'start')

    for stat_id in df_stats.index:

        print 'GET WEEKEND TRIP COUNTS FROM STATION: {:d}'.format(stat_id)

        success = False
        n_tries = 0
        while not success and n_tries < 5:
            try:
                df_counts = df_counts.append(get_hourly_counts(stat_id, dirxn))
                success = True
            except Exception as e:
                print '   ## ERROR ON STATION: {:d}'.format(stat_id)
                print '   ## {:s}'.format(e)
                n_tries = n_tries + 1

    df_wk_from_counts = df_counts.fillna(0)

    # Save weekday trip information
    df_wk_from_counts.to_csv('stations_hourly_wd_from_counts.csv')

if not os.path.exists('stations_hourly_we_to_counts.csv'):
    df_counts = pd.DataFrame()

    days_to_count = [0, 6]
    dirxn = ('to', 'stop')

    for stat_id in df_stats.index:

        success = False
        n_tries = 0
        while not success and n_tries < 5:
            try:
                df_counts = df_counts.append(get_hourly_counts(stat_id, dirxn))
                success = True
            except Exception as e:
                print '   ## ERROR ON STATION: {:d}'.format(stat_id)
                print '   ## {:s}'.format(e)
                n_tries = n_tries + 1

    df_wk_to_counts = df_counts.fillna(0)

    # Save weekday trip information
    df_wk_to_counts.to_csv('stations_hourly_we_to_counts.csv')

if not os.path.exists('stations_hourly_we_from_counts.csv'):
    df_counts = pd.DataFrame()

    days_to_count = [0, 6]
    dirxn = ('from', 'start')

    for stat_id in df_stats.index:

        print 'GET WEEKEND TRIP COUNTS FROM STATION: {:d}'.format(stat_id)

        success = False
        n_tries = 0
        while not success and n_tries < 5:
            try:
                df_counts = df_counts.append(get_hourly_counts(stat_id, dirxn))
                success = True
            except Exception as e:
                print '   ## ERROR ON STATION: {:d}'.format(stat_id)
                print '   ## {:s}'.format(e)
                n_tries = n_tries + 1

    df_wk_from_counts = df_counts.fillna(0)

    # Save weekday trip information
    df_wk_from_counts.to_csv('stations_hourly_we_from_counts.csv')
