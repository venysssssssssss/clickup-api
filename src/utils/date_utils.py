from datetime import datetime
import pytz

def parse_date(timestamp: int, timezone: str) -> dict:
    dt = datetime.utcfromtimestamp(int(timestamp) / 1000).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
    return {
        'data': dt.strftime('%d-%m-%Y'),
        'ano': dt.strftime('%Y'),
        'hora': dt.strftime('%H:%M:%S')
    }

def convert_time(time_in_minutes: int) -> str:
    if time_in_minutes < 60:
        return f'{time_in_minutes} minutos'
    elif time_in_minutes < 1440:
        hours = time_in_minutes / 60
        return f'{hours:.1f} horas'
    else:
        days = time_in_minutes / 1440
        return f'{days:.1f} dias'

def convert_time_to_days(time_str: str) -> float:
    if 'horas' in time_str:
        hours = float(time_str.split()[0])
        return hours / 24
    elif 'dias' in time_str:
        return float(time_str.split()[0])
    elif 'minutos' in time_str:
        minutes = float(time_str.split()[0])
        return minutes / 1440
    else:
        return 0.0
