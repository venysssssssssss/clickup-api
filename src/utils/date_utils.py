from datetime import datetime
import pytz

def parse_date(timestamp: int, timezone: pytz.timezone) -> str:
    return (
        datetime.utcfromtimestamp(int(timestamp) / 1000)
        .replace(tzinfo=pytz.utc)
        .astimezone(timezone)
        .strftime('%d-%m-%Y %H:%M:%S')
    )
