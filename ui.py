import streamlit as st

def show_place_card(name, category, distance, score, map_link, image_link):

    st.markdown(f"""
    <div style="
        background:#1e1e1e;
        padding:15px;
        border-radius:10px;
        margin-bottom:15px;
        color:white;
    ">
        <h3>📍 {name}</h3>
        <p>📌 {category}</p>
        <p>📏 Distance: {distance:.2f} km</p>
        <p>🤖 Score: {score:.2f}</p>
        <a href="{map_link}" target="_blank">🧭 Directions</a> |
        <a href="{image_link}" target="_blank">🖼 Images</a>
    </div>
    """, unsafe_allow_html=True)