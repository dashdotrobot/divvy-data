#!/usr/bin/env python

'Calculate tripchains for all bikes'

import sodapy
import tripchains


data_url = 'data.cityofchicago.org'
divvy_data = 'fg6s-gzvg'

# Get all valid bikes
data = sodapy.Socrata(data_url, None)
valid_bikes = data.get(divvy_data,
                       select='bike_id, count(trip_id)',
                       group='bike_id',
                       limit=10000)

bike_ids = [int(b['bike_id']) for b in valid_bikes]
num_trips = [int(b['count_trip_id']) for b in valid_bikes]
num_bikes = len(bike_ids)

f_out = open('tripchains.txt', 'w')
f_out.write('bike_id, tripchain_length, start_trip_id, end_trip_ed\n')

for i in range(num_bikes):

    # Get all rides from bike
    success = False
    while not success:
        try:
            all_trips = data.get(divvy_data,
                                 bike_id=str(bike_ids[i]),
                                 limit=10000,
                                 order='stop_time ASC')

            tc_starts = tripchains.tripchain_starts(all_trips)
            tc_ends = [ts-1 for ts in tc_starts[1:]] + [len(all_trips)-1]
            tc_len = tripchains.tripchain_lengths(tc_starts, len(all_trips))

            # Print each tripchain to datafile
            for (s, e, tcl) in zip(tc_starts, tc_ends, tc_len):
                tid_start = int(all_trips[s]['trip_id'])
                tid_end = int(all_trips[e]['trip_id'])

                f_out.write('{0:d}, {1:d}, {2:d}, {3:d}\n'
                            .format(bike_ids[i], tcl, tid_start, tid_end))

            success = True
            print 'Bike {0:5d}: OK: {1:4.1f} %'.format(bike_ids[i],
                                                       100*float(i)/num_bikes)
        except Exception as e:
            print e
            print 'Retrying...'

data.close()
f_out.close()
