# 🚀 Speedtest - Streamlit App

A premium network speed test application built with Streamlit and Chart.js. It measures Ping, Jitter, Download, and Upload speeds of your current device with high-frequency monitoring and live visualization.

![Sample Screenshot](![Uploading image.png…]()

## Features
- **Client-Side Testing**: Measures the speed of the user's phone or laptop, not the server.
- **Interactive Performance Graph**: Live toggleable metrics (Ping, Jitter, Download, Upload).
- **Average Metrics**: Displays running session averages for more consistent monitoring.
- **Extended History**: Full history list that extends automatically as you run more tests.
- **High-Frequency Monitoring**: Adjustable frequency down to 2 seconds.
- **Continuous Monitoring**: Automatic tests for 10 seconds to 5 minutes.
- **Premium UI**: Sleek dark mode design with live progress tracking.

## Local Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/thies2005/Speedtest
   cd Speedtest
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
- [Streamlit](https://streamlit.io/) - Python web framework
- [Chart.js](https://www.chartjs.org/) - JavaScript charting library
- [Cloudflare Speed Test API](https://speed.cloudflare.com/) - Network testing backend
