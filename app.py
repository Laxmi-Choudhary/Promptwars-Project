import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
import time
from datetime import datetime, timedelta
import pydeck as pdk

# =========================
# DATA GENERATION
# =========================
def generate_data(num_points=100):
    np.random.seed(int(time.time()))
    zones = ["Gate A", "Gate B", "Food Court", "Exit"]

    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=num_points)
    time_index = pd.date_range(start=start_time, end=end_time, periods=num_points)

    data = []

    for zone in zones:
        base_crowd = np.random.normal(loc=100, scale=20, size=num_points)
        base_queue = np.random.normal(loc=15, scale=5, size=num_points)

        num_anomalies = np.random.randint(1, 4)
        anomaly_indices = np.random.choice(num_points, num_anomalies, replace=False)

        base_crowd[anomaly_indices] += np.random.randint(50, 150, size=num_anomalies)
        base_queue[anomaly_indices] += np.random.randint(40, 80, size=num_anomalies)

        df_zone = pd.DataFrame({
            "Timestamp": time_index,
            "Zone": zone,
            "Crowd_Count": np.maximum(0, base_crowd.astype(int)),
            "Queue_Length": np.maximum(0, base_queue.astype(int))
        })

        data.append(df_zone)

    return pd.concat(data, ignore_index=True)

# =========================
# ML ANOMALY DETECTION
# =========================
def detect_anomalies(df):
    df_copy = df.copy()
    features = df_copy[["Crowd_Count", "Queue_Length"]].values

    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)

    preds = model.predict(features)
    df_copy["ML_Anomaly"] = preds == -1
    return df_copy

# =========================
# QUEUE ANOMALY
# =========================
def queue_detection(df):
    df_copy = df.copy()
    df_copy["Queue_Anomaly"] = df_copy["Queue_Length"] > 35
    return df_copy

# =========================
# RISK ENGINE
# =========================
def calculate_risk(crowd_count, queue_length):
    crowd_factor = min(crowd_count / 200.0, 1.0) * 60
    queue_factor = min(queue_length / 100.0, 1.0) * 40

    score = int(crowd_factor + queue_factor)

    if score < 40:
        return score, "Safe"
    elif score <= 70:
        return score, "Moderate"
    else:
        return score, "Critical"

# =========================
# TREND ANALYSIS
# =========================
def predict_trend(df):
    trends = {}

    for zone in df['Zone'].unique():
        zone_df = df[df['Zone'] == zone].sort_values("Timestamp")

        if len(zone_df) >= 5:
            diff = zone_df['Crowd_Count'].iloc[-1] - zone_df['Crowd_Count'].iloc[-5]

            if diff > 15:
                trends[zone] = "Increasing"
            elif diff < -15:
                trends[zone] = "Decreasing"
            else:
                trends[zone] = "Stable"
        else:
            trends[zone] = "Stable"

    return trends

# =========================
# RECOMMENDATIONS
# =========================
def generate_recommendations(row):
    if row['Status'] == "Critical":
        return "🚨 Redirect crowd immediately."
    elif row['Queue_Anomaly'] or row['Queue_Length'] > 25:
        return "⚠️ Deploy more staff."
    elif row['Status'] == "Moderate":
        return "👀 Monitor situation closely."
    return "✅ Normal operation."

# =========================
# HEATMAP
# =========================
def generate_heatmap(latest_data):
    fig = px.treemap(
        latest_data,
        path=[px.Constant("Stadium"), 'Zone'],
        values='Crowd_Count',
        color='Risk_Score',
        color_continuous_scale=["green", "yellow", "red"],
        range_color=[0, 100]
    )
    return fig

# =========================
# LIVE MAP
# =========================
def render_live_map(df):
    st.subheader("🗺️ Live Stadium Heatmap")

    zone_coords = {
        "Gate A": [72.8777, 19.0760],
        "Gate B": [72.8785, 19.0765],
        "Food Court": [72.8790, 19.0755],
        "Exit": [72.8765, 19.0758]
    }

    latest = df.groupby("Zone").tail(1).copy()
    latest["lat"] = latest["Zone"].map(lambda x: zone_coords[x][1])
    latest["lon"] = latest["Zone"].map(lambda x: zone_coords[x][0])

    layer = pdk.Layer(
        "HeatmapLayer",
        data=latest,
        get_position='[lon, lat]',
        get_weight="Crowd_Count",
        radiusPixels=60
    )

    view_state = pdk.ViewState(
        latitude=19.0760,
        longitude=72.8777,
        zoom=15,
        pitch=40
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# =========================
# PIPELINE
# =========================
@st.cache_data(ttl=60)
def get_processed_data():
    raw = generate_data()
    df = detect_anomalies(raw)
    df = queue_detection(df)

    df["Is_Anomaly"] = df["ML_Anomaly"] | df["Queue_Anomaly"]

    rs = df.apply(lambda r: calculate_risk(r["Crowd_Count"], r["Queue_Length"]), axis=1)
    df["Risk_Score"] = [x[0] for x in rs]
    df["Status"] = [x[1] for x in rs]

    return df

# =========================
# DECISION ENGINE
# =========================
def decision_engine(row):
    if row["Risk_Score"] > 80:
        return "🔴 EMERGENCY"
    elif row["Risk_Score"] > 60:
        return "🟡 CONTROL"
    return "🟢 SAFE"

# =========================
# UI
# =========================
def display_dashboard():

    st.set_page_config(page_title="CrowdSense AI", layout="wide")
    st.title("🏟️ CrowdSense AI")

    df = get_processed_data()

    # =========================
    # CONTROL PANEL (SIDEBAR)
    # =========================
    st.sidebar.header("🎛️ Control Panel")

    zones = df["Zone"].unique()
    selected = st.sidebar.multiselect("Zones", zones, default=zones)

    df = df[df["Zone"].isin(selected)]

    latest_data = df.groupby("Zone").tail(1)

    # =========================
    # EXPORT DATA (SIDEBAR)
    # =========================
    st.sidebar.subheader("📤 Export Data")

    csv = latest_data.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        label="Download Latest Zone Data (CSV)",
        data=csv,
        file_name="crowdsense_latest_data.csv",
        mime="text/csv"
    )

    trends = predict_trend(df)

    # =========================
    # ALERTS
    # =========================
    st.subheader("🚨 Alerts")

    for _, row in latest_data.iterrows():
        if row["Status"] == "Critical":
            st.error(f"{row['Zone']} CRITICAL")

    # =========================
    # ZONE CARDS
    # =========================
    st.subheader("📊 Zones")

    for _, row in latest_data.iterrows():
        st.metric(row["Zone"], f"{row['Crowd_Count']} people")

    # =========================
    # STATUS MODULE
    # =========================
    st.subheader("📍 Live Zone Status (Control Panel)")

    for _, row in latest_data.iterrows():

        if row["Status"] == "Safe":
            icon, label = "🟢", "Safe Zone"
        elif row["Status"] == "Moderate":
            icon, label = "🟡", "Warning Zone"
        else:
            icon, label = "🔴", "Critical Zone"

        st.markdown(f"""
        ### {icon} {row['Zone']} - {label}

        - 👥 Crowd Count: **{row['Crowd_Count']}**
        - ⚠️ Queue Length: **{row['Queue_Length']}**
        - 📊 Risk Score: **{row['Risk_Score']}**
        - 🚦 Status: **{row['Status']}**
        """)

        st.divider()

    # =========================
    # HEATMAP
    # =========================
    st.subheader("🔥 Heatmap")
    st.plotly_chart(generate_heatmap(latest_data), use_container_width=True)

    # =========================
    # LIVE MAP
    # =========================
    render_live_map(df)

    # =========================
    # RECOMMENDATIONS
    # =========================
    st.subheader("💡 Recommendations")

    for _, row in latest_data.iterrows():
        st.info(generate_recommendations(row))

    # =========================
    # TRENDS
    # =========================
    st.subheader("📈 Trends")
    st.write(trends)

    # =========================
    # AI TABLE
    # =========================
    latest_data["AI_Action"] = latest_data.apply(decision_engine, axis=1)
    st.dataframe(latest_data[["Zone", "Crowd_Count", "Risk_Score", "Status", "AI_Action"]])

    # =========================
    # LIVE CHART
    # =========================
    st.subheader("📊 Crowd Trend")
    fig = px.line(df, x="Timestamp", y="Crowd_Count", color="Zone")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # AUTO REFRESH
    # =========================
    time.sleep(10)
    st.rerun()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    display_dashboard()