import streamlit as st
from datetime import date
import yfinance as yf
from plotly import graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import pandas as pd
import io
import csv

# Flask app initialization
app = Flask(__name__)
app.secret_key = "secretkey123"  # Replace with a more secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Database model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Database model for portfolio
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    shares = db.Column(db.Float, nullable=False)

# Ensure database is created
if not os.path.exists('users.db'):
    with app.app_context():
        db.create_all()

# Custom CSS for Streamlit styling
st.markdown("""<style>
    .title {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        color: #4b4b4b;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 1.8em;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
</style>""", unsafe_allow_html=True)

# Title of the app
st.markdown('<p class="title">📈 Stock Prediction Dashboard</p>', unsafe_allow_html=True)

# User Authentication
def check_login():
    return 'username' in st.session_state

def register_user(username, email, password):
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

def login_user(username, password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            st.session_state['username'] = user.username
            return True
    return False

def logout_user():
    if 'username' in st.session_state:
        del st.session_state['username']

def add_to_portfolio(user_id, ticker, shares):
    with app.app_context():
        new_stock = Portfolio(user_id=user_id, ticker=ticker, shares=shares)
        db.session.add(new_stock)
        db.session.commit()

def get_portfolio(user_id):
    with app.app_context():
        portfolio = Portfolio.query.filter_by(user_id=user_id).all()
    return portfolio

def remove_from_portfolio(stock_id):
    with app.app_context():
        stock_to_remove = Portfolio.query.get(stock_id)
        if stock_to_remove:
            db.session.delete(stock_to_remove)
            db.session.commit()

# Login and Registration forms
if not check_login():
    st.sidebar.header("User Authentication")
    choice = st.sidebar.selectbox("Login or Register", ["Login", "Register"])

    if choice == "Register":
        username = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Register"):
            try:
                register_user(username, email, password)
                st.sidebar.success("Registration successful! Please log in.")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")
    else:  # Login
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            if login_user(username, password):
                st.sidebar.success("Login successful!")
            else:
                st.sidebar.error("Invalid credentials, please try again.")

# After successful login
if check_login():
    st.sidebar.success(f"Logged in as {st.session_state['username']}")

    # Logout button
    if st.sidebar.button("Logout"):
        logout_user()
        st.sidebar.success("You have logged out.")
        st.experimental_rerun()  # Refresh the app to update the session state

    # Sidebar settings for stock selection
    st.sidebar.header("Settings")
    stocks = ("AAPL", "GOOG", "MSFT", "GME", "^NSEI")
    selected_stocks = st.sidebar.multiselect("Select Stock Datasets", stocks, default=["AAPL"])

    # Date range selector
    st.sidebar.subheader("Date Range")
    date_range = st.sidebar.date_input("Select Date Range", [date(2020, 1, 1), date.today()])

    # Data Sampling Option
    data_sampling = st.sidebar.selectbox("Data Sampling", ["Daily", "Weekly", "Monthly"])

    # Technical Indicator Selection
    indicators = ["None", "Bollinger Bands", "MACD", "RSI"]
    selected_indicator = st.sidebar.selectbox("Select Technical Indicator", indicators)

    # Load data function with caching
    @st.cache_data
    def load_data(tickers, start, end, frequency):
        data = {}
        for ticker in tickers:
            if frequency == "Daily":
                data[ticker] = yf.download(ticker, start=start, end=end)
            elif frequency == "Weekly":
                data[ticker] = yf.download(ticker, start=start, end=end, interval='1wk')
            else:  # Monthly
                data[ticker] = yf.download(ticker, start=start, end=end, interval='1mo')
            data[ticker].reset_index(inplace=True)
        return data

    # Data loading
    data_load_state = st.text("Loading data...")
    data_dict = load_data(selected_stocks, date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d"), data_sampling)
    data_load_state.text("")

    # Check if data is empty
    if not data_dict or all(data.empty for data in data_dict.values()):
        st.error("No data found for the selected stocks.")
    else:
        # Normal Stock Price Chart Section
        st.markdown('<p class="section-header">Stock Price Chart</p>', unsafe_allow_html=True)

        # Plotting normal data
        def plot_normal_data(data_dict, indicator=None):
            fig = go.Figure()
            for ticker, data in data_dict.items():
                if not data.empty:
                    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name=f'{ticker} Close'))
                    # Add indicators
                    if indicator == "Bollinger Bands":
                        rolling_mean = data['Close'].rolling(window=20).mean()
                        rolling_std = data['Close'].rolling(window=20).std()
                        upper_band = rolling_mean + (rolling_std * 2)
                        lower_band = rolling_mean - (rolling_std * 2)
                        fig.add_trace(go.Scatter(x=data['Date'], y=upper_band, mode='lines', name=f'{ticker} Upper Band', line=dict(dash='dash')))
                        fig.add_trace(go.Scatter(x=data['Date'], y=lower_band, mode='lines', name=f'{ticker} Lower Band', line=dict(dash='dash')))
                    elif indicator == "MACD":
                        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
                        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
                        macd = exp1 - exp2
                        signal = macd.ewm(span=9, adjust=False).mean()
                        fig.add_trace(go.Scatter(x=data['Date'], y=macd, mode='lines', name=f'{ticker} MACD'))
                        fig.add_trace(go.Scatter(x=data['Date'], y=signal, mode='lines', name=f'{ticker} Signal', line=dict(dash='dash')))
                    elif indicator == "RSI":
                        delta = data['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        fig.add_trace(go.Scatter(x=data['Date'], y=rsi, mode='lines', name=f'{ticker} RSI'))

            fig.update_layout(title="Stock Prices with Indicators", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        plot_normal_data(data_dict, selected_indicator)  # Call the plot function to display normal data with indicators

        # Volume Analysis Section
        st.markdown('<p class="section-header">Volume Analysis</p>', unsafe_allow_html=True)

        # Function to plot volume data for each selected stock
        def plot_volume(data_dict):
            for ticker, data in data_dict.items():
                if not data.empty:
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name=ticker, marker_color='lightblue'))
                    fig_volume.update_layout(title=f'Trading Volume for {ticker}', xaxis_title='Date', yaxis_title='Volume', template='plotly_white')
                    st.plotly_chart(fig_volume, use_container_width=True)

        # Call the volume plotting function
        plot_volume(data_dict)

        # Forecasting Section
        st.markdown('<p class="section-header">Forecasting</p>', unsafe_allow_html=True)

        # Number of days for forecasting
        forecast_days = st.sidebar.slider("Days to Forecast", 1, 365, 30)

        # Forecast for the first selected stock (for simplicity)
        first_stock = selected_stocks[0]
        df_train = data_dict[first_stock][['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
        df_train['ds'] = df_train['ds'].dt.tz_localize(None)  # Remove timezone

        model = Prophet(interval_width=0.95, seasonality_mode='additive')
        model.fit(df_train)
        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)

        # Forecast Plot
        st.write(f"Forecast Plot for {first_stock}")
        forecast_fig = plot_plotly(model, forecast)
        st.plotly_chart(forecast_fig)

        # Display forecast components
        st.write("Forecast Components")
        forecast_components_fig = model.plot_components(forecast)
        st.pyplot(forecast_components_fig)

        
        # Footer
        st.sidebar.write("Developed by [Your Name]")  # Replace with your name

else:
    st.error("Please log in to access the stock prediction features.")