# dbt - Nutricao Feminina

Este projeto dbt transforma a camada Silver em uma camada Gold com recomendacoes de alimentos por fase do ciclo menstrual.

## Conceitos que este projeto ensina

- `ref`: dependencia entre modelos dbt.
- `model`: consulta SQL versionada.
- `test`: validacao de qualidade dos dados.
- `macro`: funcao reutilizavel em Jinja/SQL.

## Como o dbt entra na arquitetura

```text
Bronze JSON no MinIO
    -> Silver Parquet no MinIO
    -> dbt le Silver
    -> dbt cria modelos intermediarios
    -> dbt gera Gold
    -> macro exporta Gold em Parquet para o MinIO
```

## Comandos principais

```bash
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt run-operation export_gold_recomendacoes --profiles-dir .
```

## Observacao

O arquivo `profiles.yml` atual nao contem senhas. Ele apenas define o banco DuckDB usado pelo dbt. O arquivo `profiles.yml.example` fica como referencia caso voce queira adaptar caminhos ou ambientes no futuro.
