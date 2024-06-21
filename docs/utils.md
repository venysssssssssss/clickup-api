# parse_date Function Documentation

## Overview
This function parses a UNIX timestamp into a formatted date string in the specified timezone using the `datetime` and `pytz` libraries.

## Parameters
- `timestamp` (int): UNIX timestamp in milliseconds.
- `timezone` (pytz.timezone): Timezone object from the `pytz` library used to localize the timestamp.

## Returns
- `str`: Formatted date string in the format '%d-%m-%Y %H:%M:%S'.

## Function Implementation
The function converts the UNIX timestamp to UTC time, applies the specified timezone conversion, and formats the resulting datetime object into a string.

```python
from datetime import datetime
import pytz

def parse_date(timestamp: int, timezone: pytz.timezone) -> str:
    return (
        datetime.utcfromtimestamp(int(timestamp) / 1000)
        .replace(tzinfo=pytz.utc)
        .astimezone(timezone)
        .strftime('%d-%m-%Y %H:%M:%S')
    )
```

# FIELD_PATTERNS Documentation

## Overview
This dictionary `FIELD_PATTERNS` contains compiled regular expressions for extracting field values from task descriptions based on predefined field names (`FIELD_NAMES`).

## Field Names
The `FIELD_NAMES` list defines the names of the fields for which patterns are compiled.

```python
FIELD_NAMES = [
    'CARTEIRA DEMANDANTE',
    'E-MAIL',
    'ESCOPO',
    'OBS',
    'OBJETIVO DO GANHO',
    'KPI GANHO',
    '💡 TIPO DE PROJETO',
    'TIPO DE PROJETO',
    'TIPO DE OPERAÇÃO',
    'PRODUTO',
    'OPERAÇÃO',
    'SITE',
    'UNIDADE DE NEGÓCIO',
    'DIRETOR TAHTO',
    'CLIENTE',
    'TIPO',
    '💡 R$ ANUAL (PREVISTO)',
    'GERENTE OI',
    'FERRAMENTA ENVOLVIDA',
    'CENÁRIO PROPOSTO',
    'DATA ALVO',
]
```


# Field Patterns Function documentation

### Regular Expressions: The patterns are compiled using Python's re.compile() function. Each pattern is designed to match a specific field name followed by a colon (:) and its corresponding value, ignoring case.

### Usage: These patterns are used in functions such as extract_field_values() to extract specific information from task descriptions.

``` python
import re

FIELD_PATTERNS = {
    field_name: re.compile(
        rf'{re.escape(field_name)}\s*:\s*(.*?)(?=\s*({"|".join([re.escape(name) for name in FIELD_NAMES])})\s*:|$)',
        re.IGNORECASE,
    )
    for field_name in FIELD_NAMES
}
```