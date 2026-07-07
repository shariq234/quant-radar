import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration for mobile-friendly layout
st.set_page_config(
    page_title="Fitness Tracker Pro",
    page_icon="🏃‍♂️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, mobile-friendly interface
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e24;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 3rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-green { color: #4CAF50; }
    .status-yellow { color: #FFC107; }
    .status-red { color: #F44336; }

    /* Optimize for mobile screens */
    @media (max-width: 768px) {
        .metric-value { font-size: 2.5rem; }
        .metric-label { font-size: 1rem; }
        .stPlotlyChart { width: 100% !important; }
    }
    </style>
""", unsafe_allow_html=True)

# Generate mock 7-day historical data if not in session state
if 'history' not in st.session_state:
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
    st.session_state.history = pd.DataFrame({
        'Date': dates,
        'Recovery': np.random.randint(30, 95, 7),
        'Strain': np.random.uniform(8.0, 18.0, 7).round(1),
        'Sleep_Performance': np.random.randint(50, 100, 7)
    })

# --- SIDEBAR: DATA INPUT ---
st.sidebar.header("📊 Daily Log")
st.sidebar.markdown("Enter today's biometrics:")

hrv_input = st.sidebar.number_input("HRV (ms)", min_value=10, max_value=200, value=65)
rhr_input = st.sidebar.number_input("Resting Heart Rate (bpm)", min_value=30, max_value=120, value=55)
sleep_hours = st.sidebar.slider("Sleep Duration (hours)", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
workout_intensity = st.sidebar.slider("Workout Intensity", min_value=0, max_value=10, value=6)

if st.sidebar.button("Log Today's Data"):
    # Calculate new metrics based on input

    # 1. Recovery Score (0-100)
    # Higher HRV and lower RHR generally mean better recovery. Mock formula for demonstration.
    base_recovery = 50
    hrv_factor = (hrv_input - 60) * 0.5
    rhr_factor = (60 - rhr_input) * 0.5
    sleep_factor = (sleep_hours - 7) * 5
    new_recovery = max(0, min(100, int(base_recovery + hrv_factor + rhr_factor + sleep_factor)))

    # 2. Strain Score (0-21)
    # Logarithmic scale approximation based on intensity
    new_strain = round(min(21.0, workout_intensity * 2.1), 1)

    # 3. Sleep Performance (0-100)
    # Assuming 8 hours is 100% need
    new_sleep_perf = max(0, min(100, int((sleep_hours / 8.0) * 100)))

    # Update history (shift and append)
    new_row = pd.DataFrame({
        'Date': [datetime.now().strftime('%m-%d')],
        'Recovery': [new_recovery],
        'Strain': [new_strain],
        'Sleep_Performance': [new_sleep_perf]
    })

    updated_history = pd.concat([st.session_state.history.iloc[1:], new_row], ignore_index=True)
    st.session_state.history = updated_history
    st.sidebar.success("Data logged successfully!")

# --- MAIN APP AREA ---
st.title("📱 Fitness Tracker Pro")
st.markdown("Your daily performance and recovery insights.")

# Get today's data (last row of history)
today_data = st.session_state.history.iloc[-1]
recovery = today_data['Recovery']
strain = today_data['Strain']
sleep_perf = today_data['Sleep_Performance']

# Determine colors
def get_recovery_color(val):
    if val >= 67: return "status-green"
    elif val >= 34: return "status-yellow"
    else: return "status-red"

def get_sleep_color(val):
    if val >= 85: return "status-green"
    elif val >= 70: return "status-yellow"
    else: return "status-red"

# Display Metrics in Columns
col1, col2, col3 = st.columns(3)

with col1:
    color_class = get_recovery_color(recovery)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Recovery</div>
            <div class="metric-value {color_class}">{recovery}%</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Strain doesn't have a strict color code like recovery, usually blue/white
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Day Strain</div>
            <div class="metric-value" style="color: #4da6ff;">{strain}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    color_class = get_sleep_color(sleep_perf)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Sleep Perf</div>
            <div class="metric-value {color_class}">{sleep_perf}%</div>
        </div>
    """, unsafe_allow_html=True)

# --- CHARTS ---
st.markdown("### 📈 7-Day Trends")

tab1, tab2 = st.tabs(["Recovery & Sleep", "Strain"])

hist_df = st.session_state.history

with tab1:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=hist_df['Date'],
        y=hist_df['Recovery'],
        name='Recovery %',
        marker_color=[
            '#4CAF50' if val >= 67 else '#FFC107' if val >= 34 else '#F44336'
            for val in hist_df['Recovery']
        ]
    ))
    fig1.add_trace(go.Scatter(
        x=hist_df['Date'],
        y=hist_df['Sleep_Performance'],
        name='Sleep Perf %',
        mode='lines+markers',
        line=dict(color='#8c9eff', width=2),
        marker=dict(size=8)
    ))
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=hist_df['Date'],
        y=hist_df['Strain'],
        name='Strain',
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#4da6ff', width=3),
        marker=dict(size=10)
    ))
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(range=[0, 21])
    )
    st.plotly_chart(fig2, use_container_width=True)
