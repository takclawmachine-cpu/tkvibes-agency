"""City → region / country resolution for TKVibes lead engine.

Maps discovery cities to business regions used for employee assignment
and CRM segmentation. Add new cities here as the agency expands.
"""

# ── India ────────────────────────────────────────────────────────────────────
_CITY_REGION_IN = {
    # Delhi NCR
    "Delhi": ("Delhi NCR", "India"),
    "New Delhi": ("Delhi NCR", "India"),
    "Gurgaon": ("Delhi NCR", "India"),
    "Noida": ("Delhi NCR", "India"),
    "Ghaziabad": ("Delhi NCR", "India"),
    "Faridabad": ("Delhi NCR", "India"),
    # Metros
    "Mumbai": ("Mumbai Metro", "India"),
    "Bengaluru": ("Bengaluru", "India"),
    "Hyderabad": ("Hyderabad", "India"),
    "Chennai": ("Chennai", "India"),
    "Kolkata": ("Kolkata", "India"),
    "Pune": ("Pune", "India"),
    "Ahmedabad": ("Ahmedabad", "India"),
    # North India
    "Jaipur": ("North India", "India"),
    "Lucknow": ("North India", "India"),
    "Chandigarh": ("North India", "India"),
    "Dehradun": ("North India", "India"),
    # Central India
    "Indore": ("Central India", "India"),
    "Bhopal": ("Central India", "India"),
    "Nagpur": ("Central India", "India"),
    # West India
    "Surat": ("West India", "India"),
    # South India
    "Kochi": ("South India", "India"),
    "Coimbatore": ("South India", "India"),
    "Visakhapatnam": ("South India", "India"),
    # East India
    "Bhubaneswar": ("East India", "India"),
}

# ── Canada ───────────────────────────────────────────────────────────────────
_CITY_REGION_CA = {
    # Ontario — GTA
    "Toronto": ("Ontario - GTA", "Canada"),
    "Mississauga": ("Ontario - GTA", "Canada"),
    "Brampton": ("Ontario - GTA", "Canada"),
    "Markham": ("Ontario - GTA", "Canada"),
    "Vaughan": ("Ontario - GTA", "Canada"),
    "Richmond Hill": ("Ontario - GTA", "Canada"),
    "Oakville": ("Ontario - GTA", "Canada"),
    "Burlington": ("Ontario - GTA", "Canada"),
    "Milton": ("Ontario - GTA", "Canada"),
    # Ontario — Rest
    "Ottawa": ("Ontario - East", "Canada"),
    "Hamilton": ("Ontario - West", "Canada"),
    "Kitchener": ("Ontario - West", "Canada"),
    "Waterloo": ("Ontario - West", "Canada"),
    "London": ("Ontario - West", "Canada"),
    "Windsor": ("Ontario - West", "Canada"),
    # British Columbia
    "Vancouver": ("British Columbia", "Canada"),
    "Surrey": ("British Columbia", "Canada"),
    "Burnaby": ("British Columbia", "Canada"),
    "Richmond": ("British Columbia", "Canada"),
    "Coquitlam": ("British Columbia", "Canada"),
    # Alberta
    "Calgary": ("Alberta", "Canada"),
    "Edmonton": ("Alberta", "Canada"),
    # Quebec
    "Montreal": ("Quebec", "Canada"),
    "Laval": ("Quebec", "Canada"),
    # Manitoba
    "Winnipeg": ("Manitoba", "Canada"),
    # Saskatchewan
    "Saskatoon": ("Saskatchewan", "Canada"),
    "Regina": ("Saskatchewan", "Canada"),
    # Nova Scotia
    "Halifax": ("Nova Scotia", "Canada"),
}

# Combined map (lowercase keys for case-insensitive lookup)
_REGION_MAP = {}
for city, (region, country) in _CITY_REGION_IN.items():
    _REGION_MAP[city.lower()] = (region, country)
for city, (region, country) in _CITY_REGION_CA.items():
    _REGION_MAP[city.lower()] = (region, country)


def resolve(city: str) -> tuple[str, str]:
    """Return (region, country) for a city name.  Unknown cities → ('Other', 'India')."""
    key = (city or "").strip().lower()
    return _REGION_MAP.get(key, ("Other", "India"))


def all_regions() -> list[dict]:
    """Return all known regions in a compact form for the CRM config."""
    seen = set()
    regions = []
    for city, (region, country) in _REGION_MAP.items():
        key = (region, country)
        if key not in seen:
            seen.add(key)
            regions.append(dict(region=region, country=country))
    return sorted(regions, key=lambda r: (r["country"], r["region"]))