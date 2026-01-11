import streamlit as st
import speedtest
import time
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Consistent Speedtest",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #ffffff;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        border-color: #00ffcc;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])

def get_jitter(st_client, server, count=5):
    """Calculate jitter by performing multiple pings."""
    latencies = []
    for _ in range(count):
        try:
            # Re-measuring latency to the same server
            st_client.get_servers([server['id']])
            latencies.append(st_client.results.ping)
            time.sleep(0.1)
        except:
            continue
    
    if len(latencies) < 2:
        return 0
    
    deltas = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
    return np.mean(deltas)

def run_speedtest():
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        status_text.text("Connecting to best server...")
        s = speedtest.Speedtest()
        s.get_best_server()
        progress_bar.progress(20)
        
        status_text.text("Measuring Ping & Jitter...")
        best_server = s.best
        ping = best_server['latency']
        jitter = get_jitter(s, best_server)
        progress_bar.progress(40)
        
        status_text.text("Testing Download Speed...")
        download_speed = s.download() / 1_000_000  # Convert to Mbps
        progress_bar.progress(70)
        
        status_text.text("Testing Upload Speed...")
        upload_speed = s.upload() / 1_000_000  # Convert to Mbps
        progress_bar.progress(100)
        
        status_text.text("Test Complete!")
        
        result = {
            'Timestamp': datetime.now().strftime("%H:%M:%S"),
            'Ping (ms)': round(ping, 2),
            'Jitter (ms)': round(jitter, 2),
            'Download (Mbps)': round(download_speed, 2),
            'Upload (Mbps)': round(upload_speed, 2)
        }
        
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([result])], ignore_index=True)
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        progress_bar.empty()
        status_text.empty()

def create_chart(df, column, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Timestamp'],
        y=df[column],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=8, color='#ffffff', line=dict(color=color, width=2)),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}'
    ))
    
    fig.update_layout(
        title=dict(text=f"{column} History", font=dict(size=20, color='#ffffff')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, color='#888888'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#888888'),
        hovermode='x unified'
    )
    return fig

# UI Layout
st.title("🚀 Consistent Speedtest")
st.markdown("Measure your internet performance with precision and track consistency over time.")

col1, col2, col3, col4 = st.columns(4)

if st.button("▶ Run Speedtest", use_container_width=True):
    run_speedtest()

# Display current results if history exists
if not st.session_state.history.empty:
    latest = st.session_state.history.iloc[-1]
    
    col1.metric("Ping", f"{latest['Ping (ms)']} ms")
    col2.metric("Jitter", f"{latest['Jitter (ms)']} ms")
    col3.metric("Download", f"{latest['Download (Mbps)']} Mbps")
    col4.metric("Upload", f"{latest['Upload (Mbps)']} Mbps")

    st.divider()

    chart_col1, chart_col2 = st.columns(2)
    chart_col3, chart_col4 = st.columns(2)

    with chart_col1:
        st.plotly_chart(create_chart(st.session_state.history, 'Ping (ms)', '#00BFFF'), use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(create_chart(st.session_state.history, 'Jitter (ms)', '#FF7F50'), use_container_width=True)
    
    with chart_col3:
        st.plotly_chart(create_chart(st.session_state.history, 'Download (Mbps)', '#00FFCC'), use_container_width=True)
    
    with chart_col4:
        st.plotly_chart(create_chart(st.session_state.history, 'Upload (Mbps)', '#FF69B4'), use_container_width=True)

    # Historical Data Table
    with st.expander("📊 View Detailed History"):
        st.dataframe(st.session_state.history.sort_index(ascending=False), use_container_width=True)
        
        if st.button("🗑 Clear History"):
            st.session_state.history = pd.DataFrame(columns=['Timestamp', 'Ping (ms)', 'Jitter (ms)', 'Download (Mbps)', 'Upload (Mbps)'])
            st.rerun()

else:
    st.info("Click 'Run Speedtest' to start measuring your connection.")
    
# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, Plotly, and Speedtest-cli")
