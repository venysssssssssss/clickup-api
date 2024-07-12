with leaders as (
    select
        distinct leader as leader,
        leader_email as email
    from {{ ref('tasks_cleaned') }}
)

select * from leaders
