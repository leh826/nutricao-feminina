
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ranking
from "nutricao_feminina"."main"."int_recomendacoes_por_fase"
where ranking is null



  
  
      
    ) dbt_internal_test