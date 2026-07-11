import os
import json
import requests
import boto3
import time

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# CONFIGURAÇÕES
APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")

BUCKET_NAME = "projeto-nutricao-feminina-bronze"

# Cliente MinIO/S3
s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

CATALOGO_ALIMENTOS = [
    "100g avocado",
    "100g spinach",
    "100g salmon",
    "100g pumpkin seeds",
    "30g dark chocolate",
    "2 eggs",
    "100g lentils",
    "100g kale",
    "100g walnuts",
    "100g red meat"
]

def extrair_dados_nutricionais(ingrediente: str):
    url = (
        f"https://api.edamam.com/api/nutrition-details"
        f"?app_id={APP_ID}&app_key={APP_KEY}"
    )

    payload = {
        "title": "Catalogo Nutricional",
        "ingr": [ingrediente]
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    except Exception as err:
        print(f"Erro ao extrair {ingrediente}: {err}")
        return None


def salvar_na_bronze(data: dict, nome_alimento: str):

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")

    nome_arquivo = nome_alimento.replace(" ", "_").lower()

    caminho_s3 = (
        f"catalogo/"
        f"ingestion_date={data_hoje}/"
        f"{nome_arquivo}_{timestamp}.json"
    )

    # Payload enriquecido
    payload_final = {
        "metadata": {
            "alimento": nome_alimento,
            "data_ingestao": data_hoje,
            "timestamp_ingestao": timestamp,
            "origem": "edamam_api"
        },
        "data": data
    }

    try:

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=caminho_s3,
            Body=json.dumps(payload_final, indent=4),
            ContentType="application/json"
        )

        print(f"{nome_alimento} salvo na Bronze.")

    except Exception as e:
        print(f"Erro ao salvar {nome_alimento}: {e}")

if __name__ == "__main__":

    print(
        f"Iniciando ingestão Bronze "
        f"({len(CATALOGO_ALIMENTOS)} itens)"
    )

    for item in CATALOGO_ALIMENTOS:

        dados = extrair_dados_nutricionais(item)

        if dados:
            salvar_na_bronze(dados, item)

            # Limite API gratuita
            time.sleep(2)

    print("Camada Bronze populada.")