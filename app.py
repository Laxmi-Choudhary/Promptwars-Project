import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

def generate_data(num_points=100):
    """Generate synthetic time-series data for multiple zones."""
    np.random.seed(int(time.time()))
    zones = ["Gate A", "Gate B", "Food Court", "Exit"]
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=num_points)
    time_index = pd.date_range(start=start_time, end=end_time, periods=num_points)
    
    data = []
    for zone in zones:
        base_crowd = np.random.normal(loc=100, scale=20, size=num_points)
        base_queue = np.random.normal(loc=15, scale=5, size=num_points)
        
        # Inject anomalies
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

def detect_anomalies(df):
    """Detect anomalies in crowd data using Isolation Forest."""
    df_copy = df.copy()
    features = df_copy[["Crowd_Count", "Queue_Length"]].values
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)
    preds = model.predict(features)
    df_copy["ML_Anomaly"] = preds == -1
    return df_copy

def queue_detection(df):
    """Implement threshold-based logic for queue anomalies."""
    df_copy = df.copy()
    df_copy["Queue_Anomaly"] = df_copy["Queue_Length"] > 35
    return df_copy

def calculate_risk(crowd_count, queue_length):
    """Calculate risk score and return status category."""
    crowd_factor = min(crowd_count / 200.0, 1.0) * 60
    queue_factor = min(queue_length / 100.0, 1.0) * 40
    score = int(crowd_factor + queue_factor)
    
    if score < 40:
        return score, "Safe"
    elif score <= 70:
        return score, "Moderate"
    else:
        return score, "Critical"

def predict_trend(df):
    """Predict crowd count trend for the next 5-10 minutes using rolling difference."""
    trends = {}
    for zone in df['Zone'].unique():
        zone_df = df[df['Zone'] == zone].sort_values("Timestamp")
        if len(zone_df) >= 5:
            # Compare latest with 5 periods ago
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

def generate_recommendations(row):
    """Generate smart recommendations based on Risk and Anomalies."""
    if row['Status'] == "Critical":
        return "🚨 Redirect crowd to nearby zones immediately."
    elif row['Queue_Anomaly'] or row['Queue_Length'] > 25:
        return "⚠️ Deploy more staff to manage queues."
    elif row['Status'] == "Moderate" or row['Crowd_Count'] > 120:
        return "👀 Open additional gate if high volume persists."
    
    return "✅ Operating smoothly. No action required."

def generate_heatmap(latest_data):
    """Generate a visual dynamic Heatmap for the monitored zones."""
    if latest_data.empty:
        return go.Figure()
        
    fig = px.treemap(
        latest_data,
        path=[px.Constant("Stadium Zones"), 'Zone'],
        values='Crowd_Count',
        color='Risk_Score',
        color_continuous_scale=[[0.0, "#2e7d32"], [0.4, "#fbc02d"], [0.7, "#c62828"], [1.0, "#b71c1c"]],
        range_color=[0, 100],
        custom_data=['Status']
    )
    
    fig.update_traces(
        textinfo="label+text",
        texttemplate="<b>%{label}</b><br>Crowd Volume: %{value}",
        hovertemplate="<b>%{label}</b><br>Risk Score: %{color}/100<br>Status: %{customdata[0]}<extra></extra>"
    )
                    
    fig.update_layout(
        title="Stadium Zone Risk Heatmap (Size=Volume, Color=Risk)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )
    return fig

@st.cache_data(ttl=60)
def get_processed_data():
    """Pipeline to process all data sequentially."""
    raw_data = generate_data()
    df = detect_anomalies(raw_data)
    df = queue_detection(df)
    df["Is_Anomaly"] = df["ML_Anomaly"] | df["Queue_Anomaly"]
    
    rs_outputs = df.apply(lambda row: calculate_risk(row['Crowd_Count'], row['Queue_Length']), axis=1)
    df['Risk_Score'] = [res[0] for res in rs_outputs]
    df['Status'] = [res[1] for res in rs_outputs]
    return df

def display_dashboard():
    """Render the main Streamlit UI."""
    st.set_page_config(page_title="CrowdSense AI", page_icon="🏟️", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .stMetric { background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E88E5; margin-bottom: 0px; }
    .sub-header { font-size: 1.2rem; color: #6c757d; margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="main-header">🏟️ CrowdSense AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Real-Time Smart Crowd & Queue Anomaly Detection</p>', unsafe_allow_html=True)
    st.divider()

    df = get_processed_data()
    
    # --- Sidebar Filter ---
    st.sidebar.header("Control Panel")
    all_zones = list(df["Zone"].unique())
    selected_zones = st.sidebar.multiselect("Select Zones to Monitor", all_zones, default=all_zones)
    
    # Filter Dataframes globally based on selection
    df = df[df["Zone"].isin(selected_zones)]
    
    if df.empty:
        st.warning("Please select at least one zone from the sidebar.")
        return
        
    # --- Export Functionality ---
    st.sidebar.divider()
    st.sidebar.subheader("📥 Export Data")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Report (CSV)",
        data=csv_data,
        file_name=f"CrowdSense_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        help="Export the active, filtered dataset as a CSV file for historical analysis."
    )
        
    zones = list(df["Zone"].unique())
    latest_data = df.sort_values(by="Timestamp").groupby("Zone").tail(1)
    trends = predict_trend(df)
    
    # 1. & 2. Alerts & Predictive System
    st.subheader("🚨 Live Alerts & Predictive Insights")
    critical_zones = latest_data[latest_data["Status"] == "Critical"]
    queue_anomalies = latest_data[latest_data["Queue_Anomaly"] == True]
    ml_anomalies = latest_data[latest_data["ML_Anomaly"] == True]

    alert_triggered = False
    
    if not critical_zones.empty:
        for _, row in critical_zones.iterrows():
            st.error(f"**Critical risk at {row['Zone']}!** (Score: {row['Risk_Score']})")
            alert_triggered = True
            
    if not ml_anomalies.empty:
        for _, row in ml_anomalies.iterrows():
            if row['Zone'] not in critical_zones['Zone'].values:
                st.warning(f"High congestion at {row['Zone']}")
                alert_triggered = True
            
    if not queue_anomalies.empty:
        for _, row in queue_anomalies.iterrows():
            st.warning(f"Queue too long at {row['Zone']} ({row['Queue_Length']} people)")
            alert_triggered = True
            
    # Predictive Alerts
    for zone, trend in trends.items():
        if trend == "Increasing":
            # Highlight zones where risk is likely to increase
            st.info(f"📈 **Predictive Alert**: Crowd expected to increase at **{zone}** in the next 5-10 minutes.")
            alert_triggered = True
                
    if not alert_triggered:
        st.success("All monitored zones operating safely. No alerts or surging trends.")

    st.divider()

    # Metrics Layout - Zone Cards
    st.subheader("📊 Zone Status Cards")
    cols = st.columns(len(zones))
    
    for idx, (index, row) in enumerate(latest_data.iterrows()):
        with cols[idx]:
            with st.container(border=True):
                color = "🟢" if row['Status'] == "Safe" else "🟡" if row['Status'] == "Moderate" else "🔴"
                trend_arrow = "↗️" if trends[row['Zone']] == "Increasing" else "↘️" if trends[row['Zone']] == "Decreasing" else "➡️"
                
                st.markdown(f"### **{row['Zone']}**")
                st.metric("Status", f"{color} {row['Status']}")
                st.metric("Risk Level & Trend", f"{row['Risk_Score']}/100 {trend_arrow}")
                st.metric("Current Crowd", f"{row['Crowd_Count']}")
                st.metric("Queue Length", f"{row['Queue_Length']}")

    st.divider()

    # Heatmap Section
    st.subheader("📍 Stadium Zone Heatmap")
    heatmap_fig = generate_heatmap(latest_data)
    st.plotly_chart(heatmap_fig, use_container_width=True)

    st.divider()

    # Recommendations Section
    st.subheader("💡 Smart AI Recommendations")
    rec_cols = st.columns(len(zones))
    
    for idx, (index, row) in enumerate(latest_data.iterrows()):
        with rec_cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{row['Zone']} Action Plan**")
                suggestion = generate_recommendations(row)
                st.info(suggestion)

    st.divider()

    # Visualizations - Live Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Live Crowd Density Trends")
        fig = px.area(df, x="Timestamp", y="Crowd_Count", color="Zone", 
                      title="Crowd Movement (Past Hour)",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        
        anomalies_df = df[df["Is_Anomaly"]]
        if not anomalies_df.empty:
            fig.add_trace(go.Scatter(
                x=anomalies_df["Timestamp"],
                y=anomalies_df["Crowd_Count"],
                mode='markers',
                name='Anomaly Detected',
                marker=dict(color='red', size=10, symbol='x', line=dict(width=2, color='white'))
            ))
            
        fig.update_layout(xaxis_title="Time", yaxis_title="Crowd Count", 
                          plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⏱️ Queue Length Snapshot")
        fig_bar = px.bar(latest_data, x="Zone", y="Queue_Length", 
                         title="Current Queues vs Limit",
                         color="Status",
                         color_discrete_map={"Safe": "#2e7d32", "Moderate": "#fbc02d", "Critical": "#c62828"})
        fig_bar.add_hline(y=35, line_dash="dash", line_color="red", annotation_text="35 ppl limit")
        fig_bar.update_layout(xaxis_title="", yaxis_title="People in Queue", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    display_dashboard()
    
    # Auto-refresh cycle (every 10 seconds)
    time.sleep(10)
    get_processed_data.clear()
    st.rerun()
