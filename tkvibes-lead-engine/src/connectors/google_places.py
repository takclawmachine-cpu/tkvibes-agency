import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models import Lead

PLACES_SEARCH = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.location,places.nationalPhoneNumber,places.internationalPhoneNumber,"
    "places.websiteUri,places.regularOpeningHours,places.rating,"
    "places.userRatingCount,places.primaryTypeDisplayName,places.businessStatus"
)


class GooglePlacesConnector:
    """Compliant Places API (New) connector — primary source."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
    def discover(self, city: str, category: str, limit: int = 60) -> list[Lead]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        leads, token = [], None
        with httpx.Client(timeout=30) as client:
            while len(leads) < limit:
                body = {"textQuery": f"{category} in {city}", "pageSize": 20}
                if token:
                    body["pageToken"] = token
                r = client.post(PLACES_SEARCH, headers=headers, json=body)
                r.raise_for_status()
                data = r.json()
                for p in data.get("places", []):
                    leads.append(self._to_lead(p, city, category))
                token = data.get("nextPageToken")
                if not token:
                    break
        return leads[:limit]

    def _to_lead(self, p: dict, city: str, category: str) -> Lead:
        website = p.get("websiteUri", "")
        loc = p.get("location", {}) or {}
        hours = p.get("regularOpeningHours", {}) or {}
        return Lead(
            business_name=(p.get("displayName") or {}).get("text", ""),
            category=(p.get("primaryTypeDisplayName") or {}).get("text", "") or category,
            phone_primary=p.get("nationalPhoneNumber", "")
                          or p.get("internationalPhoneNumber", ""),
            address=p.get("formattedAddress", ""),
            city=city,
            latitude=loc.get("latitude"),
            longitude=loc.get("longitude"),
            opening_hours="; ".join(hours.get("weekdayDescriptions", [])),
            has_website=bool(website),
            website_url=website,
            rating=p.get("rating"),
            review_count=p.get("userRatingCount"),
            source="google_places",
            source_url=f"https://www.google.com/maps/place/?q=place_id:{p.get('id','')}",
            place_id=p.get("id", ""),
        )
