{% macro export_gold_recomendacoes() %}
    {% do run_query("install httpfs") %}
    {% do run_query("load httpfs") %}
    {% do run_query("create or replace secret minio_secret (type s3, key_id '" ~ env_var("MINIO_ACCESS_KEY") ~ "', secret '" ~ env_var("MINIO_SECRET_KEY") ~ "', endpoint '" ~ env_var("MINIO_DBT_ENDPOINT", "minio:9000") ~ "', region 'us-east-1', use_ssl false, url_style 'path')") %}

    {% set export_query %}
        copy (
            select *
            from {{ ref('gold_recomendacoes_ciclo') }}
        )
        to '{{ var("gold_parquet_path") }}'
        (format parquet, overwrite true)
    {% endset %}

    {% do run_query(export_query) %}
{% endmacro %}
