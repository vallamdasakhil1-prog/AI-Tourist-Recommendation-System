import streamlit as st
import pickle
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

from utils import get_places, get_category, get_maps_link, get_image_url
from ui import show_place_card

# -----------------------------
# LOAD MODEL
# -----------------------------
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Tourist Recommender", layout="centered")
st.title("🌍 AI Tourist Recommendation System")

# -----------------------------
# SESSION STATE DEFAULTS
# -----------------------------
if "lat" not in st.session_state:
    st.session_state.lat = 17.4206
if "lon" not in st.session_state:
    st.session_state.lon = 78.6546
if "gps_trigger_count" not in st.session_state:
    st.session_state.gps_trigger_count = 0
if "last_map_click" not in st.session_state:
    st.session_state.last_map_click = None

# -----------------------------
# GPS
# -----------------------------
st.subheader("📍 Use Current Location")

if st.button("📡 Get My GPS Location"):
    st.session_state.gps_trigger_count += 1

if st.session_state.gps_trigger_count > 0:
    coords = streamlit_js_eval(
        js_expressions="""
        new Promise((resolve) => {
            if (!navigator.geolocation) {
                resolve(null);
                return;
            }
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                }),
                () => resolve(null),
                { enableHighAccuracy: true, timeout: 10000 }
            );
        })
        """,
        key=f"gps_{st.session_state.gps_trigger_count}"
    )

    if coords is None:
        st.info("⏳ Detecting your location…")
        

    elif isinstance(coords, dict) and "lat" in coords:
        st.session_state.lat = float(coords["lat"])
        st.session_state.lon = float(coords["lon"])
        st.success(f"✅ GPS Location: {st.session_state.lat:.5f}, {st.session_state.lon:.5f}")
        

    else:
        st.error("❌ Allow location access")

# -----------------------------
# MAP CLICK
# -----------------------------
st.subheader("🗺️ Click Map to Select Location")

m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=12)

folium.Marker(
    [st.session_state.lat, st.session_state.lon],
    tooltip="📍 Selected Location"
).add_to(m)

map_data = st_folium(m, width=700, height=400, key="map")

if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    clicked_tuple = (round(clicked["lat"], 6), round(clicked["lng"], 6))

    if clicked_tuple != st.session_state.last_map_click:
        st.session_state.lat = clicked["lat"]
        st.session_state.lon = clicked["lng"]
        st.session_state.last_map_click = clicked_tuple

# -----------------------------
# SHOW CURRENT LOCATION
# -----------------------------
st.info(f"📌 Current Location: {st.session_state.lat:.5f}, {st.session_state.lon:.5f}")

# -----------------------------
# MANUAL INPUT
# -----------------------------
lat = st.number_input("Latitude", value=st.session_state.lat, format="%.6f")
lon = st.number_input("Longitude", value=st.session_state.lon, format="%.6f")

if lat != st.session_state.lat or lon != st.session_state.lon:
    st.session_state.lat = lat
    st.session_state.lon = lon

radius_km = st.slider("📏 Radius (km)", 1, 20, 5)
radius = radius_km * 1000

# -----------------------------
# FIND PLACES 
if st.button("🔍 Find Best Tourist Places"):

    # ✅ define inside button
    current_lat = st.session_state.lat
    current_lon = st.session_state.lon

    st.write(f"📍 Using Location: {current_lat}, {current_lon}")

    places_data = get_places(current_lat, current_lon, radius)

    # ✅ ONE WARNING
    if not places_data:
        if radius < 3000:
            st.warning("⚠️ No places found. Try increasing the radius or select a better location.")
        else:
            st.warning("⚠️ No tourist places found in this area. Try selecting a nearby location.")
        st.stop()

    # -----------------------------
    # PROCESS DATA
    # -----------------------------
    user_loc = (current_lat, current_lon)
    places = []
    coords_map = {}

    for place in places_data:
        name = place.get("name")
        p_lat = place.get("lat")
        p_lon = place.get("lon")

        if not name or p_lat is None or p_lon is None:
            continue

        distance = geodesic(user_loc, (p_lat, p_lon)).km
        coords_map[name] = (p_lat, p_lon)

        score = model.predict([[distance, 4.0, 100]])[0]

        places.append((name, get_category(name), distance, score))

    places.sort(key=lambda x: x[3], reverse=True)

    st.session_state.places = places
    st.session_state.coords_map = coords_map

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
if st.session_state.get("places"):

    st.subheader("🗺️ Map View")

    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=13)

    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        tooltip="📍 You"
    ).add_to(m)

    for i, p in enumerate(st.session_state.places[:6]):
        name = p[0]
        if name in st.session_state.coords_map:
            p_lat, p_lon = st.session_state.coords_map[name]

            folium.Marker(
                [p_lat, p_lon],
                tooltip=f"#{i+1} {name}"
            ).add_to(m)

    st_folium(m, width=700, height=400)

    st.subheader("🏆 Top Places")

    for p in st.session_state.places[:5]:
        name, cat, dist, score = p

        dlat, dlon = st.session_state.coords_map.get(name, (st.session_state.lat, st.session_state.lon))

        map_link = get_maps_link(st.session_state.lat, st.session_state.lon, dlat, dlon)
        img_link = get_image_url(name)

        show_place_card(name, cat, dist, score, map_link, img_link)
