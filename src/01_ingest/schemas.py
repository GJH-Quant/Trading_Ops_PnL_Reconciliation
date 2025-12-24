from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class FillsSchema:

    """ FILLS SCHEMA """

    optional_cols = (
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

    optional_cols = (
        "date",
        "symbol",
        "close",  
        "timestamp",     
        "mid",
        "bid",
        "ask",
    )


@dataclass(frozen=True)
class FeesSchema:

    """ FEES SCHEMA """
    
    optional_cols = (
        "trade_id", 
        "exchange_fees",
        "broker_commissions",
        "liquidity_rebates",
        "routing_fees",     
    )


FILLS = FillsSchema()
PRICES = PricesSchema()
FEES = FeesSchema()