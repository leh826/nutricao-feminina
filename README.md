# Projeto de Engenharia de Dados: Nutricao Feminina

Este projeto tem como objetivo construir uma pipeline de dados para sugerir alimentos de acordo com a fase do ciclo menstrual. A ideia e consumir dados nutricionais da API Edamam, processar esses dados em uma arquitetura medalhao e gerar recomendacoes alimentares com base nos nutrientes mais relevantes para cada fase.

O projeto esta sendo estruturado para rodar em containers Docker, reduzindo a necessidade de instalacoes diretas na maquina local e facilitando a reproducao do ambiente.

## Objetivo

Criar um fluxo de dados capaz de:

- Extrair informacoes nutricionais de alimentos usando a API Edamam.
- Armazenar os dados brutos em uma camada Bronze.
- Tratar e padronizar os dados na camada Silver.
- Gerar recomendacoes na camada Gold de acordo com a fase do ciclo menstrual.
- Orquestrar todo o processo com Apache Airflow.
- Utilizar dbt para governanca e transformacoes entre as camadas Silver e Gold.
- Provisionar os buckets da arquitetura medalhao com Terraform.

## Arquitetura

O projeto segue a arquitetura medalhao:

- Bronze: dados brutos extraidos da API Edamam, salvos em formato JSON.
- Silver: dados tratados, consolidados e salvos em formato Parquet.
- Gold: dados refinados para consumo analitico, contendo sugestoes de alimentos por fase do ciclo menstrual.

Fluxo previsto:

```text
API Edamam
    -> Bronze
    -> Silver
    -> Gold
    -> Recomendacoes alimentares
```

## Fases do ciclo menstrual

A camada Gold considera regras de negocio para sugerir alimentos com base em nutrientes associados a cada fase:

- Menstrual: alimentos com maior quantidade de ferro.
- Lutea: alimentos com maior quantidade de magnesio.
- Folicular: alimentos com maior quantidade de calcio.
- Ovulatoria: alimentos com maior quantidade de zinco.

Atualmente, a sugestao e feita selecionando os alimentos com maior quantidade do nutriente alvo para a fase informada.

## Tecnologias utilizadas

- Python
- Apache Airflow
- Docker e Docker Compose
- Terraform
- MinIO, simulando armazenamento S3 local
- PostgreSQL
- Redis
- pgAdmin
- dbt
- DuckDB
- Streamlit
- Pandas
- PyArrow
- Boto3
- API Edamam

## Infraestrutura

A infraestrutura dos buckets e definida com Terraform.

Buckets criados:

- `projeto-nutricao-feminina-bronze`
- `projeto-nutricao-feminina-silver`
- `projeto-nutricao-feminina-gold`

O provider AWS do Terraform esta configurado para apontar para o MinIO local, usando endpoint `http://localhost:9000`.

## Estrutura atual do projeto

```text
.
|-- config/
|-- dags/
|-- data/
|-- dbt_projeto/
|-- app/
|-- logs/
|-- plugins/
|-- scripts/
|-- src/
|   |-- apify_extract.py
|   |-- apify_silver.py
|   `-- apify_gold.py
|-- docker-compose.yaml
|-- Dockerfile
|-- Dockerfile.streamlit
|-- main.tf
|-- terraform.tf
|-- requirements.txt
`-- README.md
```

## Scripts existentes

### `src/apify_extract.py`

Responsavel pela camada Bronze.

Esse script consulta a API Edamam para buscar informacoes nutricionais de uma lista inicial de alimentos e salva o retorno bruto em JSON no bucket Bronze.

### `src/apify_silver.py`

Responsavel pela camada Silver.

Esse script le os arquivos JSON da camada Bronze, extrai nutrientes relevantes e consolida os dados em um arquivo Parquet.

Nutrientes tratados atualmente:

- Magnesio
- Ferro
- Zinco
- Calcio
- Vitamina B6

### `src/apify_gold.py`

Prototipo inicial da camada Gold.

Esse script le o arquivo Parquet da camada Silver e gera uma recomendacao Top 3 de alimentos para uma fase do ciclo menstrual.

Com a entrada do dbt no projeto, a recomendacao da camada Gold passa a ser modelada preferencialmente em `dbt_projeto/models/marts/gold_recomendacoes_ciclo.sql`, deixando o script como referencia da primeira regra de negocio implementada.

## Docker

O projeto utiliza Docker Compose para subir os servicos necessarios ao ambiente local:

- Airflow API Server
- Airflow Scheduler
- Airflow Worker
- Airflow Triggerer
- Airflow DAG Processor
- PostgreSQL do Airflow
- Redis
- PostgreSQL do projeto
- pgAdmin
- MinIO

Tambem existe um `Dockerfile` customizado baseado na imagem `apache/airflow:3.1.7`, instalando dependencias como dbt, boto3, pandas, pyarrow e python-dotenv.

## Airflow

O Airflow sera usado para orquestrar todo o processo de dados, executando as etapas da pipeline na ordem correta:

1. Extracao da API Edamam para Bronze.
2. Processamento da Bronze para Silver.
3. Transformacoes e governanca com dbt.
4. Geracao da Gold com recomendacoes alimentares.

A DAG principal esta em `dags/nutricao_feminina_pipeline.py`.

Ela executa as tarefas:

```text
extract_edamam_to_bronze
    -> process_bronze_to_silver
    -> dbt_run_silver_to_gold
    -> dbt_test
    -> export_gold_to_minio
```

Para acessar o Airflow local:

```text
http://localhost:8080
```

Procure pela DAG:

```text
nutricao_feminina_medalhao
```

Como a DAG esta com `schedule=None`, ela deve ser executada manualmente pela interface do Airflow.

## Visualizacao

O projeto possui uma aplicacao Streamlit em `app/streamlit_app.py` para visualizar as recomendacoes da camada Gold de forma mais amigavel.

Ela apresenta:

- Selecao da fase do ciclo menstrual.
- Top 3 alimentos recomendados.
- Nutriente priorizado para a fase.
- Grafico comparativo dos alimentos.
- Tabela final da camada Gold.

Para subir a visualizacao:

```bash
docker compose up -d --build web
```

Acesse:

```text
http://localhost:8501
```

Antes de abrir o painel, execute a DAG `nutricao_feminina_medalhao` no Airflow para garantir que a camada Gold foi gerada.

## dbt

O dbt sera utilizado para apoiar a governanca e as transformacoes entre as camadas Silver e Gold.

Neste projeto, o dbt usa DuckDB como motor SQL leve para ler arquivos Parquet da camada Silver no MinIO e gerar a camada Gold. Essa escolha evita adicionar Spark neste momento e mantem a arquitetura mais simples para aprendizado.

Estrutura inicial criada:

```text
dbt_projeto/
|-- dbt_project.yml
|-- profiles.yml.example
|-- README.md
|-- models/
|   |-- staging/
|   |-- intermediate/
|   `-- marts/
`-- macros/
```

O fluxo previsto com dbt e:

```text
Silver Parquet no MinIO
    -> stg_nutricao_alimentos
    -> int_recomendacoes_por_fase
    -> gold_recomendacoes_ciclo
    -> exportacao da Gold em Parquet
```

Comandos principais:

```bash
cd dbt_projeto
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt run-operation export_gold_recomendacoes --profiles-dir .
```

## Variaveis de ambiente

O projeto usa arquivo `.env` para armazenar configuracoes de acesso, como:

- Credenciais da API Edamam.
- Credenciais do MinIO.
- Configuracoes do PostgreSQL.
- Configuracoes do Airflow.
- Configuracoes do pgAdmin.

Exemplo de `.env` sem expor credenciais reais:

```env
# API Edamam
EDAMAM_APP_ID=seu_app_id
EDAMAM_APP_KEY=sua_app_key

# MinIO / S3 local
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=seu_usuario_minio
MINIO_SECRET_KEY=sua_senha_minio

# Airflow
AIRFLOW_UID=50000
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASS=sua_senha_airflow
AIRFLOW_DB_NAME=airflow
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=sua_senha_webserver

# Banco do projeto
PROJECT_DB_USER=usuario_projeto
PROJECT_DB_PASS=senha_projeto
PROJECT_DB_NAME=nome_banco_projeto
PROJECT_DB_PORT=5433

# pgAdmin
PGADMIN_EMAIL=seu_email@exemplo.com
PGADMIN_PASSWORD=sua_senha_pgadmin
```

O arquivo `.env` real deve ficar apenas no ambiente local e nao deve ser versionado, pois contem credenciais e configuracoes sensiveis.

## Status atual

Ja foi iniciado:

- Ambiente Docker com Airflow, MinIO, PostgreSQL, Redis e pgAdmin.
- Infraestrutura Terraform para os buckets Bronze, Silver e Gold.
- Scripts Python para Bronze, Silver e Gold.
- Estrutura inicial de pastas para Airflow, dbt, scripts, dados e plugins.
- Projeto dbt com modelos staging, intermediate e marts.
- DAG do Airflow para orquestrar Bronze, Silver, dbt run, dbt test e exportacao da Gold.
- Aplicacao Streamlit para visualizar as recomendacoes da camada Gold.

Ainda falta:

- Definir melhor as regras de negocio das recomendacoes.
- Adicionar testes e validacoes de dados.
- Melhorar tratamento de erros e logs dos scripts.
- Organizar arquivos sensiveis e evitar versionar `.env`, `venv`, logs e state local.
