# -*- coding: utf-8 -*-
import datetime


def get_utc_timestamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970, 1, 1)
    t = (d - epoch).total_seconds()
    return t