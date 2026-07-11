
  
    
    

    create  table
      "nutricao_feminina"."main"."gold_recomendacoes_ciclo__dbt_tmp"
  
    as (
      select
    fase_ciclo,
    ranking,
    alimento,
    nutriente_prioritario,
    valor_nutriente,
    descricao
from "nutricao_feminina"."main"."int_recomendacoes_por_fase"
where ranking <= 3
order by fase_ciclo, ranking
    );
  
  