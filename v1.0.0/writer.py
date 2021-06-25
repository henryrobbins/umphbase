"""Contains functions for writing data."""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

def date_stamp():
    """Return a properly formatted date stamp for the current time."""
    t = datetime.now()
    return "%d-%d-%d" % (t.year, t.month, t.day)


def time_stamp():
    """Return a properly formatted time stamp for the current time."""
    t = datetime.now()
    return "%d-%d-%d-T%d%s" % (t.year, t.month, t.day, t.hour, str(t.minute).zfill(2))