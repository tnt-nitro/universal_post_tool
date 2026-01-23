from datetime import datetime
from .constants import TS_FORMAT, WEEKDAYS_DE


def generate_timestamp() -> str:
    now = datetime.now()

    date_part = now.strftime(TS_FORMAT)
    weekday = WEEKDAYS_DE[now.weekday()]

    return f"{date_part} | {weekday}"
