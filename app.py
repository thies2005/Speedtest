import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Consistent Speedtest",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main { background-color: #0e1117; }
.stMetric { 
    background: rgba(255, 255, 255, 0.05); 
    padding: 15px; 
    border-radius: 10px; 
}
</style>
""", unsafe_allow_html=True)

# Session State
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])
if 'test_triggered' not in st.session_state:
    st.session_state.test_triggered = False
if 'run_start' not in st.session_state:
    st.session_state.run_start = None
if 'continuous_mode' not in st.session_state:
    st.session_state.continuous_mode = False

# Sidebar
st.sidebar.title("⚙️ Settings")
test_mode = st.sidebar.radio("Mode", ["Single Test", "Continuous"])
duration_min = 5
freq_sec = 30
if test_mode == "Continuous":
    duration_min = st.sidebar.slider("Duration (min)", 1, 60, 5)
    freq_sec = st.sidebar.slider("Frequency (sec)", 10, 120, 30)

def create_chart(df, column, color):
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['Timestamp'], y=df[column],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}'
        ))
    fig.update_layout(
        title=dict(text=column, font=dict(color='white', size=16)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='#666'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#666'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=280
    )
    return fig

# Main UI
st.title("🚀 Device Speed Monitor")
st.caption("Measures your **browser/device** connection using Cloudflare.")

# Speedtest HTML Component
speedtest_html = """
<div id="speedtest-container" style="padding: 20px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 15px; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
        <button id="startBtn" onclick="runSpeedTest()" style="background: linear-gradient(135deg, #00ffcc, #00bfff); color: #000; border: none; padding: 15px 40px; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer; transition: transform 0.2s;">
            ▶ Run Speed Test
        </button>
        <div id="status" style="color: #888; font-size: 14px;"></div>
    </div>
    <div id="results" style="display: none; margin-top: 30px;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
            <div style="background: rgba(0,191,255,0.1); padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #00bfff;">
                <div style="color: #888; font-size: 12px;">PING</div>
                <div id="ping" style="color: #00bfff; font-size: 28px; font-weight: bold;">--</div>
                <div style="color: #666; font-size: 11px;">ms</div>
            </div>
            <div style="background: rgba(255,127,80,0.1); padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #ff7f50;">
                <div style="color: #888; font-size: 12px;">JITTER</div>
                <div id="jitter" style="color: #ff7f50; font-size: 28px; font-weight: bold;">--</div>
                <div style="color: #666; font-size: 11px;">ms</div>
            </div>
            <div style="background: rgba(0,255,204,0.1); padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #00ffcc;">
                <div style="color: #888; font-size: 12px;">DOWNLOAD</div>
                <div id="download" style="color: #00ffcc; font-size: 28px; font-weight: bold;">--</div>
                <div style="color: #666; font-size: 11px;">Mbps</div>
            </div>
            <div style="background: rgba(255,105,180,0.1); padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #ff69b4;">
                <div style="color: #888; font-size: 12px;">UPLOAD</div>
                <div id="upload" style="color: #ff69b4; font-size: 28px; font-weight: bold;">--</div>
                <div style="color: #666; font-size: 11px;">Mbps</div>
            </div>
        </div>
    </div>
</div>

<script>
async function runSpeedTest() {
    const btn = document.getElementById('startBtn');
    const status = document.getElementById('status');
    const results = document.getElementById('results');
    
    btn.disabled = true;
    btn.textContent = '⏳ Testing...';
    status.textContent = 'Connecting to test server...';
    
    try {
        // Ping test
        status.textContent = 'Measuring latency...';
        const pings = [];
        for (let i = 0; i < 5; i++) {
            const t0 = performance.now();
            await fetch('https://speed.cloudflare.com/__down?bytes=0', { cache: 'no-store' });
            pings.push(performance.now() - t0);
        }
        const ping = Math.min(...pings);
        const jitter = pings.slice(1).reduce((sum, v, i) => sum + Math.abs(v - pings[i]), 0) / (pings.length - 1);
        
        // Download test
        status.textContent = 'Testing download speed...';
        const dlStart = performance.now();
        const dlResp = await fetch('https://speed.cloudflare.com/__down?bytes=25000000', { cache: 'no-store' });
        const dlBlob = await dlResp.blob();
        const dlTime = (performance.now() - dlStart) / 1000;
        const dlMbps = (dlBlob.size * 8 / 1_000_000) / dlTime;
        
        // Upload test
        status.textContent = 'Testing upload speed...';
        const ulData = new Uint8Array(5000000);
        const ulStart = performance.now();
        await fetch('https://speed.cloudflare.com/__up', { method: 'POST', body: ulData });
        const ulTime = (performance.now() - ulStart) / 1000;
        const ulMbps = (ulData.length * 8 / 1_000_000) / ulTime;
        
        // Display results
        document.getElementById('ping').textContent = ping.toFixed(1);
        document.getElementById('jitter').textContent = jitter.toFixed(1);
        document.getElementById('download').textContent = dlMbps.toFixed(1);
        document.getElementById('upload').textContent = ulMbps.toFixed(1);
        
        results.style.display = 'block';
        status.textContent = '✅ Test complete! Results shown below.';
        
        // Send to Streamlit via query param (workaround)
        const data = { ping: ping.toFixed(2), jitter: jitter.toFixed(2), download: dlMbps.toFixed(2), upload: ulMbps.toFixed(2) };
        
        // Store in localStorage for persistence
        const history = JSON.parse(localStorage.getItem('speedtest_history') || '[]');
        history.push({ ...data, timestamp: new Date().toLocaleTimeString() });
        localStorage.setItem('speedtest_history', JSON.stringify(history));
        localStorage.setItem('speedtest_latest', JSON.stringify(data));
        
    } catch(e) {
        status.textContent = '❌ Error: ' + e.message;
    }
    
    btn.disabled = false;
    btn.textContent = '▶ Run Speed Test';
}

// Load previous results if any
window.onload = function() {
    const latest = JSON.parse(localStorage.getItem('speedtest_latest'));
    if (latest) {
        document.getElementById('ping').textContent = parseFloat(latest.ping).toFixed(1);
        document.getElementById('jitter').textContent = parseFloat(latest.jitter).toFixed(1);
        document.getElementById('download').textContent = parseFloat(latest.download).toFixed(1);
        document.getElementById('upload').textContent = parseFloat(latest.upload).toFixed(1);
        document.getElementById('results').style.display = 'block';
        document.getElementById('status').textContent = '📊 Showing last test results.';
    }
};
</script>
"""

# Render the speedtest component
st.components.v1.html(speedtest_html, height=350)

# Manual data entry for charting (since JS can't directly update Python state)
st.divider()
st.subheader("📊 Historical Data")

with st.expander("➕ Add Test Result Manually (or view history)"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        manual_ping = st.number_input("Ping (ms)", min_value=0.0, value=0.0)
    with col2:
        manual_jitter = st.number_input("Jitter (ms)", min_value=0.0, value=0.0)
    with col3:
        manual_dl = st.number_input("Download (Mbps)", min_value=0.0, value=0.0)
    with col4:
        manual_ul = st.number_input("Upload (Mbps)", min_value=0.0, value=0.0)
    
    if st.button("Add to History"):
        new_row = {
            'Timestamp': datetime.now().strftime("%H:%M:%S"),
            'Ping (ms)': manual_ping,
            'Jitter (ms)': manual_jitter,
            'Download (Mbps)': manual_dl,
            'Upload (Mbps)': manual_ul
        }
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Added!")
        st.rerun()

# Display charts if we have data
if not st.session_state.history.empty:
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1: st.plotly_chart(create_chart(st.session_state.history, 'Ping (ms)', '#00BFFF'), use_container_width=True)
    with c2: st.plotly_chart(create_chart(st.session_state.history, 'Jitter (ms)', '#FF7F50'), use_container_width=True)
    with c3: st.plotly_chart(create_chart(st.session_state.history, 'Download (Mbps)', '#00FFCC'), use_container_width=True)
    with c4: st.plotly_chart(create_chart(st.session_state.history, 'Upload (Mbps)', '#FF69B4'), use_container_width=True)

    with st.expander("📋 Raw Data"):
        st.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
        if st.button("🗑 Clear History"):
            st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])
            st.rerun()

st.sidebar.divider()
st.sidebar.caption("Speed tests run directly in your browser using Cloudflare endpoints. Results are displayed live above.")
