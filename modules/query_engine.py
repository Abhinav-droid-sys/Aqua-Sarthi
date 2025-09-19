import pandas as pd
import re

# Load dataset once
DATA_PATH = "data/groundwater.csv"
df = pd.read_csv(DATA_PATH)

# List of unique states and districts for matching
states = df["state"].unique().tolist()
districts = df["district"].unique().tolist()

def extract_filters(query: str):
    """Extract state, district, and year from query text."""
    query_lower = query.lower()

    # Match state
    state_match = None
    for state in states:
        if state.lower() in query_lower:
            state_match = state
            break

    # Match district
    district_match = None
    for district in districts:
        if district.lower() in query_lower:
            district_match = district
            break

    # Match year (any 4 digit number between 2000–2025)
    year_match = None
    year_found = re.findall(r"\b(20[0-2][0-9]|2025)\b", query_lower)
    if year_found:
        year_match = int(year_found[0])

    return state_match, district_match, year_match


def search_data(query: str):
    """Filter dataset based on extracted info."""
    state, district, year = extract_filters(query)
    filtered = df.copy()

    if state:
        filtered = filtered[filtered["state"] == state]
    if district:
        filtered = filtered[filtered["district"] == district]
    if year:
        filtered = filtered[filtered["year"] == year]

    if filtered.empty:
        return None, {"state": state, "district": district, "year": year}

    return filtered, {"state": state, "district": district, "year": year}
