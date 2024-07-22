from typing import Dict
from src.utils.regex_utils import FIELD_NAMES_SET, FIELD_PATTERNS

def parse_task_text(task_text: str) -> str:
    return task_text.replace('\n', ' ').replace('.:', '') if task_text else ''

def extract_field_values(task_text: str) -> Dict[str, str]:
    field_values = {field: '' for field in FIELD_NAMES_SET}
    for field_name in FIELD_NAMES_SET:
        pattern = FIELD_PATTERNS[field_name]
        match = pattern.search(task_text)
        if match:
            field_values[field_name] = match.group(1).strip()
    return field_values
