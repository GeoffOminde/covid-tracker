import pandas as pd
import streamlit as st

st.set_page_config(page_title="COVID-19 Global Tracker 🌍", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("owid-covid-data.csv")
    df.columns = [c.strip().lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    df.sort_values(['location', 'date'], inplace=True)
    return df

df = load_data()

st.sidebar.title("🔎 Filters")
countries = sorted(df['location'].dropna().unique())
default = ['Kenya'] if 'Kenya' in countries else [countries[0]]
selected_country = st.sidebar.selectbox("Country", options=countries, index=countries.index(default[0]))
min_date = df[df['location'] == selected_country]['date'].min().date()
max_date = df[df['location'] == selected_country]['date'].max().date()
start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

# Convert date_input (date) -> pandas Timestamp
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date)

df_country = df[df['location'] == selected_country].copy()
df_country = df_country[(df_country['date'] >= start_ts) & (df_country['date'] <= end_ts)]

st.title("🦠 COVID-19 Data Tracker")
st.markdown(f"Showing data for **{selected_country}** from **{start_date}** to **{end_date}**")

def metric_val(series):
    return "N/A" if series.dropna().empty else f"{int(series.dropna().iloc[-1]):,}"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🧪 Total Cases", metric_val(df_country.get('total_cases', pd.Series(dtype=float))))
with col2:
    st.metric("☠️ Total Deaths", metric_val(df_country.get('total_deaths', pd.Series(dtype=float))))
with col3:
    st.metric("💉 Total Vaccinations", metric_val(df_country.get('total_vaccinations', pd.Series(dtype=float))))

# Plots
import plotly.express as px

def show_line(y, title):
    if y not in df_country.columns or df_country[y].dropna().empty:
        return
    fig = px.line(df_country, x="date", y=y, title=title, markers=False)
    st.plotly_chart(fig, use_container_width=True)

def show_bar(y, title):
    if y not in df_country.columns or df_country[y].dropna().empty:
        return
    fig = px.bar(df_country, x="date", y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)

show_line("total_cases", "Total Cases Over Time")
show_line("total_deaths", "Total Deaths Over Time")
show_line("total_vaccinations", "Total Vaccinations Over Time")

show_bar("new_cases", "Daily New Cases")
show_bar("new_deaths", "Daily New Deaths")
show_bar("new_vaccinations", "Daily New Vaccinations")

st.caption("Built with care, clarity, and a blush beige vibe ✨")
