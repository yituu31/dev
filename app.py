import streamlit as st
import fastf1
from fastf1 import plotting
from fastf1.core import Laps
import pandas as pd
import matplotlib.pyplot as plt
import os

# Hata almamak için cache klasörü oluştur
if not os.path.exists('./cache'):
    os.makedirs('./cache')

fastf1.Cache.enable_cache('./cache')

st.set_page_config(page_title="Formula 1 Tur Analiz Paneli", layout="wide")

st.title("🏁 Formula 1 Tur Analiz Paneli")

# Sezon ve yarış seçimi
season = st.selectbox("Sezon Seçiniz", list(range(2024, 2015, -1)))
event = st.selectbox("Yarış Seçiniz", [s['EventName'] for s in fastf1.get_event_schedule(season).iterrows()][::-1])
selected_event = fastf1.get_event_schedule(season).query("EventName == @event")

# Seçilen yarışın bilgileri
if not selected_event.empty:
    gp_round = int(selected_event['RoundNumber'].values[0])
    session = fastf1.get_session(season, gp_round, 'FP2')

    st.info(f"{season} {event} FP2 Verisi Yükleniyor...")
    session.load()
    laps = session.laps

    teams = sorted(laps['Team'].dropna().unique())
    selected_team = st.selectbox("Takım Seçin", teams)

    drivers = sorted(laps[laps['Team'] == selected_team]['Driver'].unique())
    selected_drivers = st.multiselect("Pilot Seçin", drivers, default=drivers)

    st.subheader("📊 Tur Süreleri ve Ortalama Tempo")

    fig, ax = plt.subplots(figsize=(10, 6))

    for driver in selected_drivers:
        driver_laps = laps.pick_driver(driver).pick_tyres('Soft').pick_quicklaps()
        
        # Tur sürelerini temizle (zayıf turları çıkar - 3σ filtresi)
        lap_times = driver_laps['LapTime'].dt.total_seconds()
        mean = lap_times.mean()
        std = lap_times.std()
        filtered_laps = driver_laps[(lap_times > mean - 2*std) & (lap_times < mean + 2*std)]
        
        filtered_laps = filtered_laps.sort_values(by='LapNumber')
        ax.plot(filtered_laps['LapNumber'], filtered_laps['LapTime'].dt.total_seconds(), label=driver)
        avg = filtered_laps['LapTime'].dt.total_seconds().mean()
        st.write(f"🔹 {driver}: Ortalama Tempo: {avg:.3f} sn ({len(filtered_laps)} tur)")

    ax.set_title(f"{event} - Soft Lastik Tur Süreleri")
    ax.set_xlabel("Tur")
    ax.set_ylabel("Süre (saniye)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
else:
    st.warning("Yarış bilgisi yüklenemedi.")
