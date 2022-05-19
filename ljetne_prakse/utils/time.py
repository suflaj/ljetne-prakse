import datetime
from typing import Optional


def get_timestamp(
    date: Optional[datetime.datetime] = None, format: str = "%Y%m%d-%H%M%S"
) -> str:
    if date is None:
        date = datetime.datetime.now()

    return date.strftime(format)
