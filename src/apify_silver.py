import os
import boto3
import json
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Configurações
BUCKET_BRONZE = "projeto-nutricao-feminina-bronze"
BUCKET_SILVER = "projeto-nutricao-feminina-silver"
S3_PATH_BRONZE = "catalogo/"

# Cliente MinIO/S3
s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

def processar_e_salvar_silver():
    print(" Iniciando processamento Silver...")
    
    response = s3_client.list_objects_v2(Bucket=BUCKET_BRONZE, Prefix=S3_PATH_BRONZE)
    lista_final = []

    if 'Contents' in response:
        for obj in response['Contents']:
            if obj['Key'].endswith('.json'):
                # Leitura
                file_obj = s3_client.get_object(Bucket=BUCKET_BRONZE, Key=obj['Key'])
                payload = json.loads(file_obj['Body'].read().decode('utf-8'))

                metadata = payload.get("metadata", {})
                data = payload.get("data", {})
                
                # Extração de Nutrientes (Lógica que já funcionou)
                nutrientes = (data.get('totalNutrients') or data['ingredients'][0]
                    .get('parsed', [{}])[0]
                    .get('nutrients')
                    )
                
                if nutrientes:
                   nome_alimento = metadata.get("alimento")
                   linha = {
                        "alimento": nome_alimento,
                        "magnesio_mg": nutrientes.get('MG', {}).get('quantity', 0),
                        "ferro_mg": nutrientes.get('FE', {}).get('quantity', 0),
                        "zinco_mg": nutrientes.get('ZN', {}).get('quantity', 0),
                        "calcio_mg": nutrientes.get('CA', {}).get('quantity', 0),
                        "vit_b6_mg": nutrientes.get('VITB6A', {}).get('quantity', 0)
                    }
                   lista_final.append(linha)

        # 1. Unir tudo em um DataFrame
        df = pd.DataFrame(lista_final)
        
        # 2. Converter para Parquet em Memória
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
        
        # 3. Salvar na Camada Silver
        nome_arquivo_silver = "catalogo_nutricional_consolidado.parquet"
        caminho_silver = f"nutricao/alimentos_tratados/{nome_arquivo_silver}"

        s3_client.put_object(
            Bucket=BUCKET_SILVER,
            Key=caminho_silver,
            Body=parquet_buffer.getvalue()
        )
        
        print(f"Sucesso! Arquivo unificado salvo em: s3://{BUCKET_SILVER}/{caminho_silver}")
        print(f" Total de registros processados: {len(df)}")

if __name__ == "__main__":
    processar_e_salvar_silver()
