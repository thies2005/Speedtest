# 🚀 Consistent Speedtest - Streamlit App

A premium network speed test application built with Streamlit and Plotly. It measures Ping, Jitter, Download, and Upload speeds while maintaining a session history for consistency tracking.

![Sample Screenshot](https://raw.githubusercontent.com/streamlit/docs/main/public/images/streamlit-logo-secondary-colormark-darktext.png) *Note: You can add your own screenshot here.*

## Features
- **Real-time measurement**: Ping, Jitter, Download, and Upload speeds.
- **Consistency Tracking**: Historical charts for all 4 metrics.
- **Premium UI**: Sleek dark mode design with interactive Plotly charts.
- **Detailed History**: Expandable table view of all previous tests.

## Local Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd cobalt-astro
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account.
4. Select this repository and `app.py` as the main file.
5. Click **Deploy**!

## Technologies Used
- [Streamlit](https://streamlit.io/)
- [speedtest-cli](https://pypi.org/project/speedtest-cli/)
- [Plotly](https://plotly.com/python/)
- [Pandas](https://pandas.pydata.org/)
