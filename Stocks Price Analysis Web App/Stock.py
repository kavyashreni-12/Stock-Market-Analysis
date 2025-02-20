import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

# Title
st.title('📈 S&P 500 Stock Analysis App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!  
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn  
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)  
""")

# Sidebar for user input
st.sidebar.header('User Input Features')

# Web scraping S&P 500 data
@st.cache_data
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Select Sector', sorted_sector_unique, sorted_sector_unique)

# Filter data based on selection
df_selected_sector = df[df['GICS Sector'].isin(selected_sector)]

# Display filtered data
st.header('📋 Display Companies in Selected Sector')
st.write(f'Data Dimension: {df_selected_sector.shape[0]} rows and {df_selected_sector.shape[1]} columns')
st.dataframe(df_selected_sector)

# Function to download CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Convert to bytes
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# Fetch stock data from Yahoo Finance
data = yf.download(
        tickers=list(df_selected_sector[:10].Symbol),
        period="ytd",
        interval="1d",
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )

# Function to plot stock closing prices
def price_plot(symbol):
    df_stock = pd.DataFrame(data[symbol]['Close'])
    df_stock['Date'] = df_stock.index
    fig, ax = plt.subplots()  #  Create figure explicitly
    ax.fill_between(df_stock.Date, df_stock.Close, color='skyblue', alpha=0.3)
    ax.plot(df_stock.Date, df_stock.Close, color='skyblue', alpha=0.8)
    ax.set_xticklabels(df_stock.Date, rotation=90)
    ax.set_title(symbol, fontweight='bold')
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Closing Price', fontweight='bold')
    st.pyplot(fig)  #  Pass figure explicitly

# Sidebar - Select number of companies
num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Stock Closing Price Plots'):
    st.header('📈 Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)

# Additional charts
st.sidebar.header('📊 Additional Charts')
chart_type = st.sidebar.radio("Select Chart Type", ['Pie Chart', 'Line Chart', 'Bar Chart'])

if chart_type == 'Pie Chart':
    st.header("📊 Sector Distribution Pie Chart")
    sector_counts = df['GICS Sector'].value_counts()
    fig, ax = plt.subplots()  #  Create figure explicitly
    ax.pie(sector_counts, labels=sector_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    ax.set_title('S&P 500 Sector Distribution')
    st.pyplot(fig)  # Pass figure explicitly

elif chart_type == 'Line Chart':
    st.header("📈 Stock Line Chart")
    selected_stock = st.selectbox("Select a Stock Symbol", df['Symbol'])
    
    # Fetch stock data
    stock_data = yf.download(selected_stock, period="1y", interval="1d")
    
    if not stock_data.empty:
        fig, ax = plt.subplots()  # ✅ Create figure explicitly
        ax.plot(stock_data.index, stock_data['Close'], label=f'{selected_stock} Closing Price', color='blue')
        ax.set_xlabel('Date')
        ax.set_ylabel('Closing Price')
        ax.legend()
        st.pyplot(fig)  # ✅ Pass figure explicitly

elif chart_type == 'Bar Chart':
    st.header("📊 Sector-Wise Company Count (Bar Chart)")
    sector_counts = df['GICS Sector'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))  # ✅ Create figure explicitly
    sns.barplot(x=sector_counts.index, y=sector_counts.values, palette="viridis", ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_xlabel("GICS Sector")
    ax.set_ylabel("Number of Companies")
    ax.set_title("Number of Companies in Each Sector")
    st.pyplot(fig)  # ✅ Pass figure explicitly
