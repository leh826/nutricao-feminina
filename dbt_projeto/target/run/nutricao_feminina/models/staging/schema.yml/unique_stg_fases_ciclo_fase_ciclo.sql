
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    fase_ciclo as unique_field,
    count(*) as n_records

from "nutricao_feminina"."main"."stg_fases_ciclo"
where fase_ciclo is not null
group by fase_ciclo
having count(*) > 1



  
  
      
    ) dbt_internal_test