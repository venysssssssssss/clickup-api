with raw_tasks as (
    select *
    from {{ source('dwclickup', 'tasks') }}
)

select
    id,
    "Projeto",
    "ID",
    "Status",
    "Name",
    "Priority",
    "Líder",
    "Email líder",
    to_timestamp("date_created", 'DD-MM-YYYY HH24:MI:SS') as date_created,
    to_timestamp("date_updated", 'DD-MM-YYYY HH24:MI:SS') as date_updated,
    "Status History"
from raw_tasks
