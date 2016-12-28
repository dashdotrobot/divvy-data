#!/usr/bin/env python

'Analyze Divvy trip chains'

import sodapy
import numpy as np
import matplotlib.pyplot as pp


def tripchain_starts(trips):
    'Divide a trip sequence into contiguous trip chains'

    from_stat_id = [int(t['from_station_id']) for t in trips]
    to_stat_id = [int(t['to_station_id']) for t in trips]

    trip_starts = [0] + [i for i in range(1, len(trips))
                         if from_stat_id[i] != to_stat_id[i-1]]

    return trip_starts


def tripchain_lengths(tc_starts, num_trips):
    'Get length of tripchains'

    tc_len = [tc_starts[i] - tc_starts[i-1] for i in range(1, len(tc_starts))]

    return tc_len + [num_trips - tc_starts[-1]]
