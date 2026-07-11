with source as (
    select *
    from read_parquet('s3://projeto-nutricao-feminina-silver/nutricao/alimentos_tratados/catalogo_nutricional_consolidado.parquet')
),

renamed as (
    select
        cast(alimento as varchar) as alimento,
        coalesce(cast(magnesio_mg as double), 0) as magnesio_mg,
        coalesce(cast(ferro_mg as double), 0) as ferro_mg,
        coalesce(cast(zinco_mg as double), 0) as zinco_mg,
        coalesce(cast(calcio_mg as double), 0) as calcio_mg,
        coalesce(cast(vit_b6_mg as double), 0) as vit_b6_mg
    from source
    where alimento is not null
),

deduplicated as (
    select
        alimento,
        avg(magnesio_mg) as magnesio_mg,
        avg(ferro_mg) as ferro_mg,
        avg(zinco_mg) as zinco_mg,
        avg(calcio_mg) as calcio_mg,
        avg(vit_b6_mg) as vit_b6_mg
    from renamed
    group by alimento
)

select *
from deduplicated