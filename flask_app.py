from flask import Flask, render_template_string, request
import pickle
from geopy.distance import geodesic
import json

from utils import get_places

app = Flask(__name__)

# -----------------------------
# LOAD MODEL
# -----------------------------
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

# -----------------------------
# HTML 
# -----------------------------
<!DOCTYPE html>
<html>
<head>
    <title>Tourist Recommendation</title>

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>

    <style>
        #map { height: 400px; margin-top: 20px; }
    </style>
</head>
<body>

<h2>Tourist Recommendation System</h2>

<!-- GPS BUTTON -->
<button onclick="getLocation()">📍 Use My Current Location</button><br><br>

<form method="POST">
    Latitude: 
    <input id="lat" name="lat" value="{{lat if lat else ''}}"><br><br>

    Longitude: 
    <input id="lon" name="lon" value="{{lon if lon else ''}}"><br><br>

    Radius (km): 
    <input name="radius" value="{{radius if radius else '3'}}"><br><br>

    <button type="submit">Find Places</button>
</form>

<!-- MAP -->
<div id="map"></div>

{% if places %}
    <h3>Results:</h3>
    {% for p in places %}
        <p>{{p[0]}} | {{p[1]}} km | Score: {{p[2]}}</p>
    {% endfor %}
{% endif %}

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<script>
// -----------------------------
// GPS FUNCTION
// -----------------------------
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById("lat").value = position.coords.latitude;
            document.getElementById("lon").value = position.coords.longitude;
            initMap(position.coords.latitude, position.coords.longitude);
        }, function() {
            alert("Please allow location access!");
        });
    } else {
        alert("Geolocation not supported.");
    }
}

// -----------------------------
// INIT MAP
// -----------------------------
var map;

function initMap(lat, lon) {
    map = L.map('map').setView([lat, lon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © OpenStreetMap contributors'
    }).addTo(map);

    // User marker
    L.marker([lat, lon]).addTo(map)
        .bindPopup("📍 You are here")
        .openPopup();
}

// -----------------------------
// LOAD DATA FROM FLASK
// -----------------------------
var places = {{places_json | safe}};

if (places.length > 0) {
    var first = places[0];
    initMap(first.lat, first.lon);

    places.forEach(function(p) {
        L.marker([p.lat, p.lon]).addTo(map)
            .bindPopup("<b>" + p.name + "</b><br>Score: " + p.score);
    });
}
</script>

</body>
</html>
"""

# -----------------------------
# ROUTE
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def home():

    places_result = []
    places_json = []
    lat = ""
    lon = ""
    radius = "3"

    if request.method == 'POST':
        try:
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            radius = request.form.get('radius')

            lat_f = float(lat)
            lon_f = float(lon)
            radius_m = int(radius) * 1000

        except:
            return "Invalid input"

        user_loc = (lat_f, lon_f)

        data = get_places(lat_f, lon_f, radius_m)

        for place in data:
            name = place.get("tags", {}).get("name", "Unknown")
            p_lat = place.get("lat")
            p_lon = place.get("lon")

            if not p_lat or not p_lon:
                continue

            distance = round(geodesic(user_loc, (p_lat, p_lon)).km, 2)
            score = model.predict([[distance, 4.0, 100]])[0]

            places_result.append((name, distance, round(score, 2)))

            # For map
            places_json.append({
                "name": name,
                "lat": p_lat,
                "lon": p_lon,
                "score": round(score, 2)
            })

        places_result.sort(key=lambda x: x[2], reverse=True)
        places_json = sorted(places_json, key=lambda x: x["score"], reverse=True)

    return render_template_string(
        HTML,
        places=places_result,
        places_json=json.dumps(places_json),
        lat=lat,
        lon=lon,
        radius=radius
    )

if __name__ == '__main__':
    app.run(debug=True)
