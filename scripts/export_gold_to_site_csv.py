from __future__ import annotations

from pathlib import Path

import duckdb


ROOT_DIR = Path(__file__).resolve().parents[1]
DUCKDB_PATH = ROOT_DIR / "dbt_projeto" / "nutricao_feminina.duckdb"
OUTPUT_PATH = ROOT_DIR / "docs" / "data" / "gold_recomendacoes.csv"


def main() -> None:
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DUCKDB_PATH}. Run dbt before exporting the CSV."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as connection:
        df = connection.sql(
            """
            select
                fase_ciclo,
                ranking,
                alimento,
                nutriente_prioritario,
                valor_nutriente,
                descricao
            from gold_recomendacoes_ciclo
            order by fase_ciclo, ranking
            """
        ).df()

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"CSV exported to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
