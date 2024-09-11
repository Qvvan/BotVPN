from dataclasses import dataclass


@dataclass
class WorksheetModel:
    name: str
    rows: int = 100
    cols: int = 26
