
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ferro_mg
from "nutricao_feminina"."main"."stg_nutricao_alimentos"
where ferro_mg is null



  
  
      
    ) dbt_internal_test