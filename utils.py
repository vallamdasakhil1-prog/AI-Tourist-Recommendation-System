import requests

API_KEY = "5ae2e3f221c38a28845f05b6aca8c165dd138ac840f4548e591d484c"

# -----------------------------
# BAD WORDS (FILTER OUT)
# -----------------------------
BAD_WORDS = [
    "hotel", "bar", "restaurant", "theatre", "theater",
    "cinema", "mall", "shop", "store", "cafe", "club", "pub",
    "lodge", "resort", "dhaba", "bakery"
]

# -----------------------------
# GET PLACES (OpenTripMap)
# -----------------------------
def get_places(lat, lon, radius):

    url = "https://api.opentripmap.com/0.1/en/places/radius"

    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "limit": 50,
        "apikey": API_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        places = []

        for place in data.get("features", []):
            name = place["properties"].get("name", "Unknown")

            # Skip unnamed places
            if name == "Unknown":
                continue

            name_lower = name.lower()

            # 🔥 FILTER BAD WORDS
            if any(word in name_lower for word in BAD_WORDS):
                continue

            coords = place["geometry"]["coordinates"]
            p_lon = coords[0]
            p_lat = coords[1]

            places.append({
                "name": name,
                "lat": p_lat,
                "lon": p_lon
            })

        return places

    except Exception as e:
        print("Error:", e)
        return []


# -----------------------------
# CATEGORY
# -----------------------------
def get_category(name):
    name = name.lower()

    if "temple" in name:
        return "🛕 Temple"
    elif "beach" in name:
        return "🏖 Beach"
    elif "fort" in name:
        return "🏰 Fort"
    elif "museum" in name:
        return "🏛 Museum"
    elif "park" in name:
        return "🌳 Park"
    elif "lake" in name:
        return "🌊 Lake"
    else:
        return "📍 Tourist Place"


# -----------------------------
# GOOGLE MAP LINK
# -----------------------------
def get_maps_link(lat1, lon1, lat2, lon2):
    return f"https://www.google.com/maps/dir/{lat1},{lon1}/{lat2},{lon2}"


# -----------------------------
# IMAGE LINK
# -----------------------------
def get_image_url(name):
    return f"https://www.google.com/search?tbm=isch&q={name}"