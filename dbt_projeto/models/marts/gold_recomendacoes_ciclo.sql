select
    fase_ciclo,
    ranking,
    alimento,
    nutriente_prioritario,
    valor_nutriente,
    descricao
from {{ ref('int_recomendacoes_por_fase') }}
where ranking <= 3
order by fase_ciclo, ranking
