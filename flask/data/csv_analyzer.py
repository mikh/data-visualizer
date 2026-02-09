"""Module csv_analyzer analyzes the stats of a csv file."""

from typing import Dict, Any

import pandas as pd


def analyze_csv_stats(file_path: str) -> Dict[str, Any]:
    """Analyze a csv file for its stats."""
    df = pd.read_csv(file_path)

    column_stats = []
    for col in df.columns:
        col_data = df[col]

        if pd.api.types.is_numeric_dtype(col_data):
            data_type = "numeric"
        else:
            data_type = "string"

        num_rows = len(col_data)
        num_null = col_data.isnull().sum()
        num_unique = col_data.nunique()

        stats = {
            "column_name": col,
            "data_type": data_type,
            "num_rows": int(num_rows),
            "num_unique_values": int(num_unique),
            "num_null_values": int(num_null),
        }

        if data_type == "numeric":
            numeric_data = col_data.dropna()
            if len(numeric_data) > 0:
                stats["num_zeros_values"] = int(numeric_data.eq(0).sum())
                stats["std_dev"] = float(numeric_data.std())
                stats["mean"] = float(numeric_data.mean())
                stats["median"] = float(numeric_data.median())
                stats["min_value"] = float(numeric_data.min())
                stats["max_value"] = float(numeric_data.max())
        else:
            string_data = col_data.dropna().astype(str)
            stats["num_empty_values"] = int((string_data == "").sum())

        column_stats.append(stats)
    return {
        "num_columns": len(df.columns),
        "num_rows": len(df),
        "column_stats": column_stats,
    }
