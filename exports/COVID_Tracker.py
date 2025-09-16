import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="COVID-19 Global Tracker 🌍", layout="wide")

# ------------------------------
# Data Loader
# ------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("filtered_data.csv")
    df.columns = [c.strip().lower() for c in df.columns]
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    df.sort_values(['location', 'date'], inplace=True)
    return df

df = load_data()

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.title("🔎 Filters")
countries = sorted(df['location'].dropna().unique())

# Default country = Kenya if exists
default = ['Kenya'] if 'Kenya' in countries else [countries[0]]
selected_country = st.sidebar.selectbox("Country", options=countries, index=countries.index(default[0]))

# Date range for chosen country
country_dates = df[df['location'] == selected_country]['date']
min_date = country_dates.min().date()
max_date = country_dates.max().date()

start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

# Validation: Ensure start <= end
if start_date > end_date:
    st.sidebar.error("⚠️ Start date must be before end date.")
    st.stop()

# Convert to pandas timestamps
start_ts = pd.to_datetime(start_date)
end_ts = pd.to_datetime(end_date)

# Filter dataset
df_country = df[(df['location'] == selected_country) &
                (df['date'] >= start_ts) &
                (df['date'] <= end_ts)].copy()

# ------------------------------
# Title & Overview
# ------------------------------
st.title("🦠 COVID-19 Data Tracker")
st.markdown(f"Showing data for **{selected_country}** from **{start_date}** to **{end_date}**")

# ------------------------------
# Metrics
# ------------------------------
def metric_val(series):
    return "N/A" if series.dropna().empty else f"{int(series.dropna().iloc[-1]):,}"

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🧪 Total Cases", metric_val(df_country.get('total_cases', pd.Series(dtype=float))))
with col2:
    st.metric("☠️ Total Deaths", metric_val(df_country.get('total_deaths', pd.Series(dtype=float))))
with col3:
    st.metric("💉 Total Vaccinations", metric_val(df_country.get('total_vaccinations', pd.Series(dtype=float))))

# ------------------------------
# Chart Helpers
# ------------------------------
def show_line(y, title):
    if y not in df_country.columns or df_country[y].dropna().empty:
        return
    fig = px.line(df_country, x="date", y=y, title=title, markers=False)
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=30))
    st.plotly_chart(fig, use_container_width=True)

def show_bar(y, title):
    if y not in df_country.columns or df_country[y].dropna().empty:
        return
    fig = px.bar(df_country, x="date", y=y, title=title)
    fig.update_layout(margin=dict(l=30, r=30, t=50, b=30))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Plots
# ------------------------------
show_line("total_cases", "📈 Total Cases Over Time")
show_line("total_deaths", "📉 Total Deaths Over Time")
show_line("total_vaccinations", "💉 Total Vaccinations Over Time")

show_bar("new_cases", "🆕 Daily New Cases")
show_bar("new_deaths", "⚰️ Daily New Deaths")
show_bar("new_vaccinations", "💉 Daily New Vaccinations")

# ------------------------------
# Footer
# ------------------------------
st.sidebar.markdown("---")
st.sidebar.info("Built with ❤️ using Streamlit + Plotly\n\nData source: Your CSV")
st.caption("✨ Built with care, clarity, and a blush beige vibe")
