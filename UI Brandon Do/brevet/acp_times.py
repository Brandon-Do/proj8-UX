"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

brevet_km_distances = {
    200: (15, 34),
    300: (15, 32),
    400: (15, 30),
    600: (11.428, 28),
    1000: (13.333, 26)
}

def calculate_times(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       A tuple of arrow objects, (open_time, close_time) in that order.
    """
    min_speed, max_speed = False, False

    for c in brevet_km_distances.keys():
        if c == brevet_dist_km:
            min_speed, max_speed = brevet_km_distances[c]
            break

    if max_speed and min_speed:
        open_hours = control_dist_km / max_speed        #The open time in hours with respect to brevet_dist_km
        close_hours = control_dist_km / min_speed       #The closing time in hours with respect to brevet_dist_km
        open_days = 0
        close_days = 0

        if open_hours >= 24 or close_hours >= 24:
            open_days = open_hours // 24
            close_days = close_hours // 24
            open_hours = open_hours % 24
            close_hours = close_hours % 24

        start_time = arrow.get(brevet_start_time) #Take the start time, add both open, close to get open_time and close_time
        open_time = start_time.shift(days =+ open_days, hours=+open_hours)
        close_time= start_time.shift(days =+ close_days, hours=+close_hours)

        return (open_time, close_time)

    else:
        print("Nominal distance is not official, must be of 200, 300, 400, 600, or 1000")

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    open_time = calculate_times(control_dist_km, brevet_dist_km, brevet_start_time)[0]

    return open_time.isoformat()


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    close_time = calculate_times(control_dist_km, brevet_dist_km, brevet_start_time)[1]

    return close_time.isoformat()
