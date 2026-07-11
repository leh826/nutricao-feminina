
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select descricao
from "nutricao_feminina"."main"."stg_fases_ciclo"
where descricao is null



  
  
      
    ) dbt_internal_test