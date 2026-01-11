import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime, timedelta
from streamlit_javascript import st_javascript

# Set page config
st.set_page_config(
    page_title="Consistent Speedtest (Client-Side)",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ffcc;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])
if 'running' not in st.session_state:
    st.session_state.running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# Sidebar Controls
st.sidebar.title("⚙️ Test Settings")
test_mode = st.sidebar.radio("Test Mode", ["Single Speed Test", "Continuous Monitoring"])

duration_min = 1
if test_mode == "Continuous Monitoring":
    duration_min = st.sidebar.slider("Total Duration (minutes)", 1, 60, 5)
    frequency_sec = st.sidebar.slider("Frequency (seconds)", 10, 300, 30)
else:
    frequency_sec = 0

# JavaScript Speedtest Logic
JS_CODE = """
async function runTest() {
    const endpoints = {
        ping: "https://speed.cloudflare.com/__down?bytes=0",
        download: "https://speed.cloudflare.com/__down?bytes=2000000",
        upload: "https://speed.cloudflare.com/__up"
    };

    async function measurePing() {
        const start = performance.now();
        await fetch(endpoints.ping, { cache: 'no-store' });
        return performance.now() - start;
    }

    // 1. Measure Ping & Jitter
    const pings = [];
    for(let i=0; i<5; i++) {
        pings.push(await measurePing());
    }
    const ping = Math.min(...pings);
    const deltas = pings.slice(1).map((v, i) => Math.abs(v - pings[i]));
    const jitter = deltas.reduce((a, b) => a + b, 0) / deltas.length;

    // 2. Measure Download
    const dlStart = performance.now();
    const dlRes = await fetch(endpoints.download, { cache: 'no-store' });
    const dlBlob = await dlRes.blob();
    const dlEnd = performance.now();
    const dlMbps = (dlBlob.size * 8) / ((dlEnd - dlStart) / 1000) / 1_000_000;

    // 3. Measure Upload
    const ulData = new Uint8Array(1000000); // 1MB for upload test
    const ulStart = performance.now();
    await fetch(endpoints.upload, {
        method: 'POST',
        body: ulData
    });
    const ulEnd = performance.now();
    const ulMbps = (ulData.length * 8) / ((ulEnd - ulStart) / 1000) / 1_000_000;

    return {
        ping: ping.toFixed(2),
        jitter: jitter.toFixed(2),
        download: dlMbps.toFixed(2),
        upload: ulMbps.toFixed(2)
    };
}
return await runTest();
"""

def create_chart(df, column, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Timestamp'], y=df[column],
        mode='lines+markers',
        line=dict(color=color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}'
    ))
    fig.update_layout(
        title=dict(text=f"{column}", font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='gray'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='gray'),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300
    )
    return fig

# UI Body
st.title("🚀 Device Speed Monitor")
st.info("This app tests the connection of your **current device** (browser), not the server.")

if not st.session_state.running:
    if st.button("▶ START TEST", use_container_width=True):
        st.session_state.running = True
        st.session_state.start_time = datetime.now()
        st.rerun()
else:
    if st.button("⏹ STOP TEST", use_container_width=True):
        st.session_state.running = False
        st.rerun()

# Execution Loop
if st.session_state.running:
    # Check for duration timeout
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds() / 60
    if test_mode == "Continuous Monitoring" and elapsed >= duration_min:
        st.session_state.running = False
        st.success(f"Continuous monitoring completed ({duration_min} minutes).")
        st.rerun()

    # Trigger JS Test
    with st.spinner("Testing..."):
        result = st_javascript(JS_CODE)
    
    if result and isinstance(result, dict):
        new_row = {
            'Timestamp': datetime.now().strftime("%H:%M:%S"),
            'Ping (ms)': float(result['ping']),
            'Jitter (ms)': float(result['jitter']),
            'Download (Mbps)': float(result['download']),
            'Upload (Mbps)': float(result['upload'])
        }
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
        
        # If Single Test, stop here
        if test_mode == "Single Speed Test":
            st.session_state.running = False
            st.rerun()
        else:
            # For continuous, wait for frequency and rerun
            time.sleep(frequency_sec)
            st.rerun()

# Metrics Display
if not st.session_state.history.empty:
    latest = st.session_state.history.iloc[-1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ping", f"{latest['Ping (ms)']} ms")
    m2.metric("Jitter", f"{latest['Jitter (ms)']} ms")
    m3.metric("Download", f"{latest['Download (Mbps)']} Mbps")
    m4.metric("Upload", f"{latest['Upload (Mbps)']} Mbps")

    st.divider()

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1: st.plotly_chart(create_chart(st.session_state.history, 'Ping (ms)', '#00BFFF'), use_container_width=True)
    with c2: st.plotly_chart(create_chart(st.session_state.history, 'Jitter (ms)', '#FF7F50'), use_container_width=True)
    with c3: st.plotly_chart(create_chart(st.session_state.history, 'Download (Mbps)', '#00FFCC'), use_container_width=True)
    with c4: st.plotly_chart(create_chart(st.session_state.history, 'Upload (Mbps)', '#FF69B4'), use_container_width=True)

    with st.expander("📋 Data Log"):
        st.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
        if st.button("🗑 Reset"):
            st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])
            st.rerun()
else:
    st.write("Press Start to begin measuring your device's connection quality.")

st.sidebar.markdown("---")
st.sidebar.info("Continuous mode will record data points every few seconds to visualize connection stability.")
