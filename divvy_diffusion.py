#!/usr/bin/env python

'Track the diffusion of individual bikes through the Divvy system'

import sodapy
import matplotlib.pyplot as pp


data_url = 'data.cityofchicago.org'
divvy_data = 'fg6s-gzvg'

data = sodapy.Socrata(data_url, None)

# Get most recent trips terminating at a particular station
# Station ID = 353: Touhy and Clark
# station_in = data.get(divvy_data, limit=10, to_station_id='353',
                      # order='stop_time DESC')
# for t in station_in:
    # print t['stop_time'], t['from_station_name'], ' >> ', t['to_station_name']

# Get most recent trips made by a particular bike
# bike_id: 2350
# trip_chain = data.get(divvy_data, limit=10, bike_id='1',
                      # order='stop_time DESC')
# for t in trip_chain:
    # print t['stop_time'], t['from_station_name'], ' >> ', t['to_station_name']

# Determine fraction of subscriber rides by women in each Divvy year
for y in [2013, 2014, 2015, 2016]:
    where = 'stop_time between \'{0:d}-01-01T00:00:00\''.format(y) +\
        ' and \'{0:d}-12-31T11:59:00\''.format(y)
    num_trips = data.get(divvy_data, select='gender, count(trip_id)',
                         where=where,
                         group='gender')
    for i, r in enumerate(num_trips):
        if 'gender' in r:
            if r['gender'] == 'Male':
                i_male = i
            elif r['gender'] == 'Female':
                i_female = i

    num_female = int(num_trips[i_female]['count_trip_id'])
    num_male = int(num_trips[i_male]['count_trip_id'])

    num_total = num_female + num_male

    print y, float(num_female)/num_total, num_total, num_trips[i_female]

data.close()
