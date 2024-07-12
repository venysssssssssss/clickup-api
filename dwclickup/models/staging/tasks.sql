with cleaned_tasks as (
    select *
    from {{ ref('tasks_cleaned') }}
)

select
    id,
    task_id,
    "Status",
    "Name",
    "Priority",
    leader,
    leader_email,
    date_created,
    date_updated,
    status_history
from cleaned_tasks
