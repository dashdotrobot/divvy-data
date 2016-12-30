#!/usr/bin/env python

'Create table of number of trips from station I to station J'

import sodapy
import pandas as pd


data_url = 'data.cityofchicago.org'
trip_data = 'fg6s-gzvg'
station_data = 'aavc-b2wj'

# Open Socrata resource
data = sodapy.Socrata(data_url, None)

# Get station information
select = 'id, station_name, total_docks, latitude, longitude'
stations_json = data.get(station_data, select=select,
                         limit=1000, order='id ASC')

# Convert to DataFrame and convert columns to numeric types
stations = pd.DataFrame(stations_json)
cols_convert = ['id', 'total_docks', 'latitude', 'longitude']
stations[cols_convert] = stations[cols_convert].apply(pd.to_numeric)
stations.set_index('id', inplace=True)

print 'Retrieved {0:d} station records'.format(len(stations))

stations.to_csv('stations.csv')


# Create empty dataframe
stat_to_stat = pd.DataFrame(columns=stations.index)

# Get all trips origination from station i
c = 0
for i in stations.index:
    select = 'count(trip_id), to_station_id'
    trips_json = data.get(trip_data, select=select, limit=100,
                          from_station_id=i,
                          group='to_station_id',
                          order='to_station_id ASC')

    trips = dict(zip([int(t['to_station_id']) for t in trips_json],
                     [int(t['count_trip_id']) for t in trips_json]))

    stat_to_stat.loc[i] = pd.Series(trips)

    print '{:6.2f}%'.format(100*float(c+1)/len(stations))
    c += 1

# Fill zeros, convert to ints, and write to CSV
stat_to_stat.fillna(0, inplace=True)
stat_to_stat = stat_to_stat.astype(int)
stat_to_stat.to_csv('stat_to_stat.csv')

data.close()
