"""
Table Adapter Configurations - Declarative CDC Framework
Defines schema mapping for each table in finance.db
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TableAdapter:
    """Declarative configuration for a table's CDC behavior"""
    table: str                    # Table name in database
    pk: str                       # Primary key column
    name_col: str                 # Column used as "name" for lookups
    value_cols: List[str]         # Columns that can be updated (create new version)
    date_col: Optional[str]       # Investment date column (None if not applicable)
    extra_cols: List[str]         # Additional columns carried forward on update
    cdc_cols: List[str]           # CDC columns: ["status", "superseded_by", "is_latest"]


# ============================================================================
# TABLE ADAPTER REGISTRY
# ============================================================================

TABLE_ADAPTERS = {
    "mutual_fund": TableAdapter(
        table="mutual_fund",
        pk="sr_no",
        name_col="name",
        value_cols=["invested_value", "current_value", "total_profit"],
        date_col="investment_date",
        extra_cols=["field_of_invest"],
        cdc_cols=["status", "superseded_by", "is_latest"]
    ),
    "fixed_deposit": TableAdapter(
        table="fixed_deposit",
        pk="sr_no",
        name_col="investment_name",
        value_cols=["investment_amount", "maturity_amount"],
        date_col="investment_date",
        extra_cols=["field_of_invest", "interest_rate_per_annum", "days", "maturity_date"],
        cdc_cols=["status", "superseded_by", "is_latest"]
    ),
    "physical": TableAdapter(
        table="physical",
        pk="sr_no",
        name_col="investment_name",
        value_cols=["total_investment", "current_value"],
        date_col="investment_date",
        extra_cols=["field_of_invest"],
        cdc_cols=["status", "superseded_by", "is_latest"]
    ),
    "saving": TableAdapter(
        table="saving",
        pk="sr_no",
        name_col="name",
        value_cols=["amt"],
        date_col="investment_date",
        extra_cols=[],
        cdc_cols=["status", "superseded_by", "is_latest"]
    ),
    "stock": TableAdapter(
        table="stock",
        pk="sr_no",
        name_col="name",
        value_cols=["invested_value", "current_value", "total_profit"],
        date_col="investment_date",
        extra_cols=["field_of_invest", "no_of_shares"],
        cdc_cols=["status", "superseded_by", "is_latest"]
    ),
}


def get_adapter(table_name: str) -> TableAdapter:
    """Get adapter by table name, raise if not found"""
    if table_name not in TABLE_ADAPTERS:
        raise ValueError(f"Unknown table: {table_name}. Available: {list(TABLE_ADAPTERS.keys())}")
    return TABLE_ADAPTERS[table_name]


def list_tables() -> List[str]:
    """List all configured table names"""
    return list(TABLE_ADAPTERS.keys())


# ============================================================================
# VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("TABLE ADAPTER REGISTRY")
    print("=" * 60)
    for name, adapter in TABLE_ADAPTERS.items():
        print(f"\n{name}:")
        print(f"  Table: {adapter.table}")
        print(f"  PK: {adapter.pk}")
        print(f"  Name Col: {adapter.name_col}")
        print(f"  Value Cols: {adapter.value_cols}")
        print(f"  Date Col: {adapter.date_col}")
        print(f"  Extra Cols: {adapter.extra_cols}")
        print(f"  CDC Cols: {adapter.cdc_cols}")
    print(f"\nTotal tables: {len(TABLE_ADAPTERS)}")