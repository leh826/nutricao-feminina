
  
  create view "nutricao_feminina"."main"."int_recomendacoes_por_fase__dbt_tmp" as (
    with alimentos as (
    select *
    from "nutricao_feminina"."main"."stg_nutricao_alimentos"
),

fases as (
    select *
    from "nutricao_feminina"."main"."stg_fases_ciclo"
),

pontuado as (
    select
        fases.fase_ciclo,
        fases.nutriente_prioritario,
        fases.descricao,
        alimentos.alimento,
        case fases.nutriente_prioritario
            when 'ferro_mg' then alimentos.ferro_mg
            when 'magnesio_mg' then alimentos.magnesio_mg
            when 'calcio_mg' then alimentos.calcio_mg
            when 'zinco_mg' then alimentos.zinco_mg
        end as valor_nutriente
    from fases
    cross join alimentos
),

rankeado as (
    select
        *,
        row_number() over (
            partition by fase_ciclo
            order by valor_nutriente desc
        ) as ranking
    from pontuado
)

select *
from rankeado
  );
