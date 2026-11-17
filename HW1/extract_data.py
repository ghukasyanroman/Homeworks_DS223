"""Extract the microwave data from the saved official EIA HTML table."""

from html.parser import HTMLParser
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://www.eia.gov/totalenergy/data/annual/showtext.php?t=ptb0206"


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"}:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join(" ".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)


def extract_microwave_data():
    """Read years and values from HTML, then save microwave_us_raw.csv."""
    source = ROOT / "data/source_eia_table_2_6.html"
    parser = TableRows()
    parser.feed(source.read_text(encoding="cp1252"))

    # The final HTML column is a change across years, not another observation.
    header = next(row for row in parser.rows if row and row[0] == "1978")
    year_columns = [i for i, value in enumerate(header) if re.fullmatch(r"\d{4}", value)]
    years = [int(header[i]) for i in year_columns]
    ownership = next(row for row in parser.rows if row[0] == "Microwave Oven")
    households = next(row for row in parser.rows if row[0] == "Total Households (millions)")

    def number(value):
        return np.nan if value == "NA" else float(value.replace(",", ""))

    data = pd.DataFrame({
        "year": years,
        "households_millions": [number(households[i + 1]) for i in year_columns],
        "microwave_ownership_pct": [number(ownership[i + 1]) for i in year_columns],
        "source_id": "R3",
        "source_url": SOURCE_URL,
    })
    output = ROOT / "data/microwave_us_raw.csv"
    data.to_csv(output, index=False)
    return data


if __name__ == "__main__":
    frame = extract_microwave_data()
    print(frame.to_string(index=False))
    print("Saved data/microwave_us_raw.csv from the EIA HTML table.")
