
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select fase_ciclo
from "nutricao_feminina"."main"."stg_fases_ciclo"
where fase_ciclo is null



  
  
      
    ) dbt_internal_test