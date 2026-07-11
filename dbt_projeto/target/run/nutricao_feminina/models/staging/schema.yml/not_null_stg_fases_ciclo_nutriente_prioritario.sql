
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nutriente_prioritario
from "nutricao_feminina"."main"."stg_fases_ciclo"
where nutriente_prioritario is null



  
  
      
    ) dbt_internal_test