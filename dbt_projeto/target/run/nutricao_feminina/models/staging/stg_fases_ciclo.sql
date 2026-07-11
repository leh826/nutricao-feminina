
  
  create view "nutricao_feminina"."main"."stg_fases_ciclo__dbt_tmp" as (
    with fases as (
    select *
    from (
        values
            ('Menstrual', 'ferro_mg', 'Apoio a reposicao de ferro'),
            ('Lutea', 'magnesio_mg', 'Apoio a sintomas comuns da fase lutea'),
            ('Folicular', 'calcio_mg', 'Apoio a saude ossea e metabolismo'),
            ('Ovulatoria', 'zinco_mg', 'Apoio a imunidade e equilibrio hormonal')
    ) as t(fase_ciclo, nutriente_prioritario, descricao)
)

select *
from fases
  );
