import logging
import re
from datetime import datetime
from typing import Dict, List

import pytz

from src.utils.date_utils import convert_time, convert_time_to_days, parse_date
from src.utils.text_utils import extract_field_values, parse_task_text

logger = logging.getLogger(__name__)


def filter_tasks(
    tasks: List[Dict], timezone: str
) -> (List[Dict], List[Dict]):   # type: ignore
    filtered_data = []
    status_history_data = []
    emoji_pattern = re.compile(
        '['
        '\U0001F600-\U0001F64F'
        '\U0001F300-\U0001F5FF'
        '\U0001F680-\U0001F6FF'
        '\U0001F1E0-\U0001F1FF'
        ']+',
        flags=re.UNICODE,
    )

    for task in tasks:
        try:
            date_created = parse_date(task['date_created'], timezone)
            date_updated = parse_date(task['date_updated'], timezone)

            filtered_task = {
                'task_id': task['id'],
                'Status': emoji_pattern.sub(
                    r'', task['status'].get('status', '')
                ),
                'Name': task.get('name', ''),
                'Priority': task.get('priority', {}).get('priority', None)
                if task.get('priority')
                else None,
                'Líder': task.get('assignees', [{}])[0].get('username')
                if task.get('assignees')
                else None,
                'Email líder': task.get('assignees', [{}])[0].get('email')
                if task.get('assignees')
                else None,
                'date_created_data': date_created['data'],
                'date_created_ano': date_created['ano'],
                'date_created_hora': date_created['hora'],
                'date_updated_data': date_updated['data'],
                'date_updated_ano': date_updated['ano'],
                'date_updated_hora': date_updated['hora'],
            }

            task_text = parse_task_text(task.get('text_content', ''))
            field_values = extract_field_values(task_text)
            filtered_task.update(field_values)

            filtered_data.append(filtered_task)

            status_history = convert_status_history(
                task.get('time_in_status', {})
            )
            for entry in status_history.get('status_history', []):
                status_history_data.append(
                    {
                        'task_id': task['id'],
                        'status': emoji_pattern.sub(r'', entry['status']),
                        'time_in_status': convert_time_to_days(
                            entry['time_in_status']
                        ),
                        'timestamp': datetime.now(pytz.timezone(timezone)),
                    }
                )
        except KeyError as e:
            logger.error(f'Missing key {e} in task {task}')
            continue

    return filtered_data, status_history_data


def convert_status_history(status_history: Dict) -> Dict:
    result = {}
    if (
        'current_status' in status_history
        and 'total_time' in status_history['current_status']
    ):
        result['current_status'] = {
            'status': status_history['current_status']['status'],
            'time_in_status': convert_time(
                status_history['current_status']['total_time']['by_minute']
            ),
        }
    if 'status_history' in status_history:
        result['status_history'] = [
            {
                'status': status['status'],
                'time_in_status': convert_time(
                    status['total_time']['by_minute']
                ),
            }
            for status in status_history['status_history']
            if 'total_time' in status
        ]
    return result
