
    
    

select
    alimento as unique_field,
    count(*) as n_records

from "nutricao_feminina"."main"."stg_nutricao_alimentos"
where alimento is not null
group by alimento
having count(*) > 1


