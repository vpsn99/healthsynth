from pathlib import Path

import duckdb
import pandas as pd


def write_duckdb(
    datasets: dict[str, pd.DataFrame],
    output_dir: str = "output",
    database_name: str = "healthsynth.duckdb",
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    db_path = output_path / database_name

    if db_path.exists():
        db_path.unlink()

    with duckdb.connect(str(db_path)) as con:
        for table_name, dataframe in datasets.items():
            con.register("tmp_df", dataframe)
            con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM tmp_df")
            con.unregister("tmp_df")

    return db_path
