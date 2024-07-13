from datetime import datetime

import pytz


def convert_time(time_in_minutes: int) -> str:
    if time_in_minutes < 60:
        return f'{time_in_minutes} minutos'
    elif time_in_minutes < 1440:
        hours = time_in_minutes / 60
        return f'{hours:.1f} horas'
    else:
        days = time_in_minutes / 1440
        return f'{days:.1f} dias'


def parse_date(timestamp: int, timezone: pytz.timezone) -> str:
    return (
        datetime.utcfromtimestamp(int(timestamp) / 1000)
        .replace(tzinfo=pytz.utc)
        .astimezone(timezone)
        .strftime('%d-%m-%Y %H:%M:%S')
    )
