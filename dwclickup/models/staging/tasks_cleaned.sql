with raw_tasks as (
    select *
    from {{ source('dwclickup', 'tasks') }}
)

select
    id,
    "Projeto",
    "ID" as task_id,
    "Status",
    "Name",
    "Priority",
    "Líder" as leader,
    "Email líder" as leader_email,
    to_timestamp("date_created", 'DD-MM-YYYY HH24:MI:SS') as date_created,
    to_timestamp("date_updated", 'DD-MM-YYYY HH24:MI:SS') as date_updated,
    "Status History" as status_history
from raw_tasks
