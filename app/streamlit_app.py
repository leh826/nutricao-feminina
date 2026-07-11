from __future__ import annotations

import os
from io import BytesIO

import boto3
import pandas as pd
import streamlit as st


GOLD_BUCKET = "projeto-nutricao-feminina-gold"
GOLD_KEY = "recomendacoes/ciclo_menstrual/recomendacoes_top3.parquet"
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/opt/airflow/dbt_projeto/nutricao_feminina.duckdb")


PHASE_NOTES = {
    "Menstrual": "Foco em alimentos ricos em ferro para apoiar a reposicao nutricional.",
    "Lutea": "Foco em magnesio, nutriente associado ao suporte da fase lutea.",
    "Folicular": "Foco em calcio para apoiar metabolismo e saude ossea.",
    "Ovulatoria": "Foco em zinco para apoiar imunidade e equilibrio hormonal.",
}


def configure_page() -> None:
    st.set_page_config(
        page_title="Nutricao Feminina",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        """
        <style>
        :root {
            --rose: #b76e79;
            --rose-soft: #f5dde2;
            --ink: #2f2a2c;
            --muted: #6f6368;
            --line: #ead8dd;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(245, 221, 226, 0.78), transparent 34rem),
                linear-gradient(135deg, #fffaf8 0%, #f8f3ef 48%, #eef5ef 100%);
            color: var(--ink);
        }

        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        .hero {
            border: 1px solid rgba(183, 110, 121, 0.22);
            border-radius: 8px;
            background: rgba(255, 250, 248, 0.80);
            padding: 1.35rem 1.45rem;
            box-shadow: 0 18px 45px rgba(72, 50, 55, 0.08);
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 760;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.55;
            max-width: 760px;
        }

        .metric-card, .recommendation-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.76);
            padding: 1rem;
            min-height: 116px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
            margin-bottom: 0.28rem;
        }

        .metric-value {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 760;
            line-height: 1.15;
        }

        .metric-note, .nutrient-line {
            color: var(--muted);
            font-size: 0.92rem;
            margin-top: 0.38rem;
        }

        .rank {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 50%;
            background: var(--rose-soft);
            color: #8d4e59;
            font-weight: 760;
            margin-bottom: 0.75rem;
        }

        .food-name {
            font-size: 1.2rem;
            font-weight: 730;
            color: var(--ink);
            margin-bottom: 0.35rem;
        }

        .stDataFrame {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=120)
def load_gold_from_minio() -> pd.DataFrame:
    s3_client = boto3.client(
        "s3",
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    )
    response = s3_client.get_object(Bucket=GOLD_BUCKET, Key=GOLD_KEY)
    return pd.read_parquet(BytesIO(response["Body"].read()))


@st.cache_data(ttl=120)
def load_gold_from_duckdb() -> pd.DataFrame:
    import duckdb

    connection = duckdb.connect(DUCKDB_PATH, read_only=True)
    return connection.sql("select * from gold_recomendacoes_ciclo").df()


def load_data() -> tuple[pd.DataFrame, str]:
    try:
        return load_gold_from_minio(), "MinIO Gold"
    except Exception:
        return load_gold_from_duckdb(), "DuckDB local"


def format_food_name(value: str) -> str:
    return str(value).replace("_", " ").strip().title()


def render_header(source_name: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">Nutricao Feminina</div>
            <div class="hero-subtitle">
                Recomendacoes alimentares baseadas nos nutrientes priorizados para cada fase do ciclo menstrual.
                Dados processados pela arquitetura medalhao e servidos a partir da camada Gold.
            </div>
            <div class="metric-note">Fonte atual: {source_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(row: pd.Series) -> None:
    st.markdown(
        f"""
        <div class="recommendation-card">
            <div class="rank">{int(row["ranking"])}</div>
            <div class="food-name">{format_food_name(row["alimento"])}</div>
            <div class="nutrient-line">
                {row["nutriente_prioritario"]}: {row["valor_nutriente"]:.2f} mg
            </div>
            <div class="metric-note">{row["descricao"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    configure_page()

    try:
        df, source_name = load_data()
    except Exception as exc:
        st.error("Nao encontrei a camada Gold. Execute a DAG do Airflow antes de abrir o painel.")
        st.caption(str(exc))
        return

    if df.empty:
        st.warning("A camada Gold foi encontrada, mas ainda nao possui registros.")
        return

    df = df.copy()
    df["alimento_formatado"] = df["alimento"].map(format_food_name)

    render_header(source_name)
    st.write("")

    phases = sorted(df["fase_ciclo"].unique())
    selected_phase = st.selectbox("Fase do ciclo", phases, index=0)

    filtered = (
        df[df["fase_ciclo"] == selected_phase]
        .sort_values("ranking")
        .reset_index(drop=True)
    )

    nutrient = filtered["nutriente_prioritario"].iloc[0]
    top_food = filtered["alimento_formatado"].iloc[0]
    note = PHASE_NOTES.get(selected_phase, filtered["descricao"].iloc[0])

    metric_cols = st.columns(3)
    with metric_cols[0]:
        render_metric("Fase selecionada", selected_phase, note)
    with metric_cols[1]:
        render_metric("Nutriente priorizado", str(nutrient).replace("_mg", "").title(), "Ranking ordenado pelo maior valor do nutriente.")
    with metric_cols[2]:
        render_metric("Principal recomendacao", top_food, "Alimento com maior pontuacao para a fase.")

    st.write("")
    st.subheader("Top 3 recomendacoes")
    card_cols = st.columns(3)
    for col, (_, row) in zip(card_cols, filtered.iterrows()):
        with col:
            render_recommendation_card(row)

    st.write("")
    st.subheader("Comparativo nutricional")
    chart_data = filtered.set_index("alimento_formatado")[["valor_nutriente"]]
    st.bar_chart(chart_data, color="#b76e79", height=280)

    st.write("")
    st.subheader("Dados da camada Gold")
    table = filtered[
        [
            "fase_ciclo",
            "ranking",
            "alimento_formatado",
            "nutriente_prioritario",
            "valor_nutriente",
            "descricao",
        ]
    ].rename(
        columns={
            "fase_ciclo": "Fase",
            "ranking": "Ranking",
            "alimento_formatado": "Alimento",
            "nutriente_prioritario": "Nutriente",
            "valor_nutriente": "Valor mg",
            "descricao": "Descricao",
        }
    )
    st.dataframe(table, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    main()
