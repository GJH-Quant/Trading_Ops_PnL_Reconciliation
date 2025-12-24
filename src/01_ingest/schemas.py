from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class FillsSchema:

    """ FILLS SCHEMA """

    required_cols = (
        "trade_id",
        "timestamp",
        "symbol",
        "side",
        "qty",
        "price",
    )


@dataclass(frozen=True)
class PricesSchema:

    """ PRICES SCHEMA """

    required_cols = (
        "date",
        "symbol",
        "close",  
        "timestamp",     
    )


@dataclass(frozen=True)
class FeesSchema:

    """ FEES SCHEMA """
    
    required_cols = (
        "trade_id", 
        "fees",
        "rebates",
    )


FILLS = FillsSchema()
PRICES = PricesSchema()
FEES = FeesSchema()