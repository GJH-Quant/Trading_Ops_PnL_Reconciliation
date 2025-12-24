from __future__ import annotations
import pandas as pd
from schemas import FILLS, PRICES, FEES

class DataValidationError(ValueError):
    pass

def require_columns(df: pd.DataFrame, required_cols: tuple, name: str) -> None:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise DataValidationError(f"{name}: missing required columns: {missing}")

def normalize_fills(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, FILLS.required_cols, "fills")
    out = df.copy()

    out["trade_id"] = out["trade_id"].astype(str).str.strip()
    out["symbol"]   = out["symbol"].astype(str).str.strip().str.upper()
    out["side"]     = out["side"].astype(str).str.strip().str.upper()

    out["qty"]       = pd.to_numeric(out["qty"], errors="coerce")
    out["price"]     = pd.to_numeric(out["price"], errors="coerce")
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce", utc=True)

    return out

def validate_fills(df: pd.DataFrame) -> None:
    require_columns(df, FILLS.required_cols, "fills")

    # trade_id non-empty
    tid = df["trade_id"]
    if tid.isna().any() or (tid.astype(str).str.len() == 0).any():
        raise DataValidationError("fills: trade_id has empty/NaN values")

    # trade_id unique
    dups = tid[tid.duplicated()].unique()
    if len(dups) > 0:
        raise DataValidationError(f"fills: duplicate trade_ids: {dups}")

    # timestamp parseable
    if df["timestamp"].isna().any():
        raise DataValidationError("fills: timestamp has unparsable values")

    # side valid
    mask = df["side"].isin(["B", "S"])
    if not mask.all():
        bad_side = df.loc[~mask, "side"].unique()
        raise DataValidationError(f"fills: wrong or missing side values: {bad_side.tolist()}")

    # qty valid
    if df["qty"].isna().any() or (df["qty"] <= 0).any():
        raise DataValidationError("fills: qty must be numeric and > 0")

    # price valid
    if df["price"].isna().any() or (df["price"] <= 0).any():
        raise DataValidationError("fills: price must be numeric and > 0")

def normalize_prices(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, PRICES.required_cols, "prices")
    out = df.copy()

    out["symbol"] = out["symbol"].astype(str).str.strip().str.upper()
    out["date"]   = pd.to_datetime(out["date"], errors="coerce").dt.date
    out["close"]  = pd.to_numeric(out["close"], errors="coerce")

    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce", utc=True)

    return out

def validate_prices(df: pd.DataFrame) -> None:
    require_columns(df, PRICES.required_cols, "prices")

    if df["date"].isna().any():
        raise DataValidationError("prices: date has unparsable values")

    sym = df["symbol"]
    if sym.isna().any() or (sym.astype(str).str.len() == 0).any():
        raise DataValidationError("prices: symbol has empty/NaN values")

    if df["close"].isna().any() or (df["close"] <= 0).any():
        raise DataValidationError("prices: close must be numeric and > 0")

    if df.duplicated(subset=["date", "symbol"]).any():
        raise DataValidationError("prices: duplicate rows for (date, symbol)")

def validate_fees(df: pd.DataFrame) -> None:
    require_columns(df, FEES.required_cols, "fees")

    if df["trade_id"].isna().any() or (df["trade_id"].astype(str).str.len() == 0).any():
        raise DataValidationError("fees: trade_id has empty/NaN values")

    fees = pd.to_numeric(df["fees"], errors="coerce")
    if fees.isna().any() or (fees > 0).any():
        raise DataValidationError("fees: fees contain NaNs or are the wrong sign")

    rebates = pd.to_numeric(df["rebates"], errors="coerce")
    if rebates.isna().any() or (rebates < 0).any():
        raise DataValidationError("fees: rebates contain NaNs or are the wrong sign")