import streamlit as st
import pandas as pd
import json

@st.cache_data
def load_data(filepath = "data/fox_data.json"):
    # Загрузка стартового датасета из JSON файла.
    try:
        with open(filepath, "r", encoding = "utf-8") as file:
            data = json.load(file)
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], format = "%H:%M")
        return df
    except (FileNotFoundError, json.JSONDecodeError):
        # Резервный датасет на случай отсутствия файла
        fallback = [
            {"id": "obs_001", "fox_id": "fox_001", "location": "Северная поляна", "color": "рыжая", "has_prey": True, "suspicion_level": 8, "time": "08:20"},
            {"id": "obs_002", "fox_id": "fox_002", "location": "Туманная тропа", "color": "черная", "has_prey": False, "suspicion_level": 5, "time": "09:05"},
            {"id": "obs_003", "fox_id": "fox_001", "location": "Северная поляна", "color": "рыжая", "has_prey": False, "suspicion_level": 9, "time": "10:40"},
            {"id": "obs_004", "fox_id": "fox_003", "location": "Моховой овраг", "color": "серебристая", "has_prey": True, "suspicion_level": 7, "time": "11:15"},
            {"id": "obs_005", "fox_id": "fox_004", "location": "Северная поляна", "color": "рыжая", "has_prey": False, "suspicion_level": 3, "time": "12:10"}
        ]
        df = pd.DataFrame(fallback)
        df["time"] = pd.to_datetime(df["time"], format = "%H:%M")
        return df

def init_session_state():
    # Инициализация сессионного хранилища Streamlit.
    if "fox_data" not in st.session_state:
        st.session_state.fox_data = load_data()

def apply_filters(df, locations, colors, fox_ids, prey_filter, suspicion_range, time_range):
    # Сквозная фильтрация датасета по выбранным параметрам.
    if df is None or df.empty:
        return pd.DataFrame()
        
    filtered = df.copy()
    
    if locations:
        filtered = filtered[filtered["location"].isin(locations)]
    if colors:
        filtered = filtered[filtered["color"].isin(colors)]
    if fox_ids:
        filtered = filtered[filtered["fox_id"].isin(fox_ids)]
        
    filtered = filtered[filtered["suspicion_level"].between(suspicion_range[0], suspicion_range[1])]
    
    if prey_filter == "Has prey":
        filtered = filtered[filtered["has_prey"] == True]
    elif prey_filter == "No prey":
        filtered = filtered[filtered["has_prey"] == False]
        
    filtered = filtered[filtered["time"].between(pd.Timestamp(time_range[0]), pd.Timestamp(time_range[1]))]
    return filtered