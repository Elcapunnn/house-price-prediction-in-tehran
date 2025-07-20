import streamlit as st
import pandas as pd
import joblib
from streamlit_folium import st_folium
import folium

# --- بارگذاری مدل و ویژگی‌ها ---
model = joblib.load("house_price_model.pkl")
feature_names = joblib.load("features.pkl")
addresses = [col.replace("Address_", "") for col in feature_names if col.startswith("Address_")]

# --- انتخاب تم ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

if st.sidebar.toggle("🌓 تغییر تم"):
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# --- تم رنگی ---
dark_mode = st.session_state.theme == 'dark'
bg_color = "#1e1e1e" if dark_mode else "#ffffff"
text_color = "#f5f5f5" if dark_mode else "#222222"
card_color = "#2d2d2d" if dark_mode else "#f9f9f9"

st.markdown(f"""
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .card {{
            background-color: {card_color};
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            margin-top: 20px;
        }}
        label, input, select, textarea {{
            color: {text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='color: {text_color}; text-align:center;'>🏡 پیش‌بینی قیمت خانه</h1>", unsafe_allow_html=True)

# --- نمایش نقشه برای انتخاب موقعیت ---
st.markdown("### 🗺 انتخاب موقعیت تقریبی ملک روی نقشه:")
map_object = folium.Map(location=[35.6892, 51.3890], zoom_start=12)  # موقعیت تهران به عنوان پیش‌فرض
map_object.add_child(folium.LatLngPopup())
map_data = st_folium(map_object, width=700, height=450)
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"📍 مختصات انتخاب‌شده: ({lat:.5f}, {lon:.5f})")
else:
    st.info("روی نقشه کلیک کنید تا موقعیت ملک ثبت شود. (تأثیری در پیش‌بینی ندارد)")

# --- فرم ورودی اطلاعات ---
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        area = st.number_input("متراژ (متر مربع)", min_value=1, max_value=1000, value=100)
        rooms = st.number_input("تعداد اتاق", min_value=0, max_value=10, value=2)
        parking = st.selectbox("پارکینگ دارد؟", ["بله", "خیر"]) == "بله"
    with col2:
        warehouse = st.selectbox("انباری دارد؟", ["بله", "خیر"]) == "بله"
        elevator = st.selectbox("آسانسور دارد؟", ["بله", "خیر"]) == "بله"
        address = st.selectbox("آدرس", addresses)

    submitted = st.form_submit_button("📊 پیش‌بینی قیمت")

if submitted:
    input_data = {
        "Area": area,
        "Room": rooms,
        "Parking": int(parking),
        "Warehouse": int(warehouse),
        "Elevator": int(elevator)
    }
    for addr in addresses:
        input_data[f"Address_{addr}"] = 1 if addr == address else 0

    X_new = pd.DataFrame([input_data])
    for col in feature_names:
        if col not in X_new.columns:
            X_new[col] = 0
    X_new = X_new[feature_names]

    predicted_price = model.predict(X_new)[0]

    st.markdown(f"""
        <div class='card'>
            <h3 style='color:{text_color};'>💰 قیمت تخمینی:</h3>
            <p style='font-size:28px; color:#4CAF50;'>{predicted_price:,.0f} تومان</p>
        </div>
    """, unsafe_allow_html=True)
