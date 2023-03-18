from datetime import datetime, date
import numpy as np
import datetime as dt

def daysCount():
    today = datetime.now()

    start = dt.date(today.year,1,1)
    end = dt.date(today.year, today.month, today.day)

    days = np.busday_count(start, end)

    return int(days)

def predDuration(lastDay: datetime):

    today = datetime.now()

    start = dt.date(today.year, today.month, today.day)
    end = dt.date(lastDay.year, lastDay.month, lastDay.day)

    days = np.busday_count(start, end)

    return int(days)



