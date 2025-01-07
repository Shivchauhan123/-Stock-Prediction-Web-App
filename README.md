
# Stock Prediction Web App

## Overview

The **Stock Prediction Web App** is a financial market prediction tool that leverages machine learning algorithms to forecast stock prices. The app uses historical data to predict the future stock trends and offers real-time data access, technical indicators, portfolio tracking, and more. It is developed using **Flask** for the backend and **Streamlit** for the frontend, providing a seamless user experience.

---

## Features

- **Real-Time Stock Data Access**: Users can access up-to-date stock prices, market trends, and financial data.
- **Stock Predictions**: The app uses advanced machine learning models (like Prophet) to predict stock prices based on historical data.
- **Technical Indicators**: Displays commonly used technical indicators such as Bollinger Bands, MACD, and RSI.
- **Portfolio Management**: Allows users to track their investments and portfolio performance over time, including metrics like total return and volatility.
- **Multi-Stock Comparison**: Users can compare multiple stocks on the same chart with interactive graphs.
- **News Feed Integration**: Keeps users updated with real-time stock news.

---

## Requirements

- Python 3.x
- Flask
- Streamlit
- SQLite (for database)
- Prophet
- Pandas
- Matplotlib
- Plotly
- TA-Lib (for technical indicators)
- NewsAPI (for news integration)

---

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/stock-prediction-web-app.git
   ```

2. **Navigate to the project directory**:
   ```bash
   cd stock-prediction-web-app
   ```

3. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the App

1. **Start the Flask backend**:
   ```bash
   python app.py
   ```

2. **Start the Streamlit frontend**:
   ```bash
   streamlit run frontend.py
   ```

3. Visit `http://localhost:5000` in your browser to access the app.

---

## Usage

- **Login**: Create an account or log in to the app to start using the features.
- **Stock Search**: Enter the stock symbol (e.g., "AAPL") to get real-time data and predictions.
- **Portfolio Tracking**: Add stocks to your portfolio and track their performance over time.
- **Charts and Indicators**: View interactive charts with technical indicators to make better trading decisions.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to your fork.
5. Submit a pull request.

---

## License

This project is licensed under the MIT License.
