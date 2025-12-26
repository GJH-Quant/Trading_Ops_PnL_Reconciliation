from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from data_validation import (
    DataValidationError,
    normalize_fills, validate_fills,
    normalize_prices, validate_prices,
    validate_fees,
)
from schemas import FILLS, PRICES, FEES


# -----------------------------
# Generic reader (FIXED)
# -----------------------------
def read_any(path: Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suf = path.suffix.lower()  # includes leading dot: ".csv", ".parquet"
    if suf == ".csv":
        return pd.read_csv(path)

    if suf == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Unsupported document type: {suf}")


# -----------------------------
# Loaders
# -----------------------------
def load_fills(path: Path, *, tz: Optional[str] = None) -> pd.DataFrame:
    """
    Loads fills from CSV/Parquet, normalizes + validates using your schemas,
    returns canonical columns (FILLS.required_cols) and sorted by timestamp.

    Expected columns (after normalization):
      trade_id, timestamp (UTC), symbol, side ('B'/'S'), qty (>0), price (>0)
    """
    df = read_any(path)

    # normalize
    df = normalize_fills(df)

    # optional tz convert (timestamp is utc=True in normalize_fills)
    if tz is not None:
        if df["timestamp"].dt.tz is None:
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
        df["timestamp"] = df["timestamp"].dt.tz_convert(tz)

    # validate
    validate_fills(df)

    # keep canonical cols + sort
    out = df.loc[:, list(FILLS.required_cols)].copy()
    out = out.sort_values("timestamp").reset_index(drop=True)
    return out


def load_prices(path: Path, *, tz: Optional[str] = None) -> pd.DataFrame:
    """
    Loads daily close marks/prices.

    Expected columns:
      date, symbol, close, timestamp (optional but in schema)
    Note: your schema requires "timestamp". If your prices file truly doesn't have it,
    either add it or remove it from PricesSchema.required_cols.
    """
    df = read_any(path)
    df = normalize_prices(df)

    # optional tz convert if timestamp exists and is tz-aware/UTC
    if "timestamp" in df.columns:
        if tz is not None:
            if getattr(df["timestamp"].dt, "tz", None) is None:
                df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
            df["timestamp"] = df["timestamp"].dt.tz_convert(tz)

    validate_prices(df)

    out = df.loc[:, list(PRICES.required_cols)].copy()
    out = out.sort_values(["date", "symbol"]).reset_index(drop=True)
    return out


def load_fees(path: Path) -> pd.DataFrame:
    """
    Loads fees/rebates by trade_id.
    Your validate_fees() enforces:
      fees <= 0
      rebates >= 0
    """
    df = read_any(path)

    # basic normalization (keep it light, validation handles sign rules)
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    # enforce required cols exist
    missing = [c for c in FEES.required_cols if c not in df.columns]
    if missing:
        raise DataValidationError(f"fees: missing required columns: {missing}")

    df["trade_id"] = df["trade_id"].astype(str).str.strip()
    df["fees"] = pd.to_numeric(df["fees"], errors="coerce")
    df["rebates"] = pd.to_numeric(df["rebates"], errors="coerce")

    validate_fees(df)

    out = df.loc[:, list(FEES.required_cols)].copy()
    out = out.reset_index(drop=True)
    return out
