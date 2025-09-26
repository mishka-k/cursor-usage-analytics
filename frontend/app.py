import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests import HTTPError

BACKEND_URL = "http://backend:8000"
ANALYTICS_ENDPOINTS = {
    "events_per_day": "/analytics/events_per_day",
    "tokens_per_user": "/analytics/tokens_per_user",
    "tokens_by_model": "/analytics/tokens_by_model",
}


def fetch_dataframe(endpoint: str) -> pd.DataFrame:
    """Retrieve analytics data from the backend and convert to a dataframe."""

    url = f"{BACKEND_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except HTTPError as exc:  # pragma: no cover - streamlit app runtime handling
        st.error(f"Failed to load data from {url}: {exc}")
        return pd.DataFrame()
    except requests.RequestException as exc:  # pragma: no cover - runtime handling
        st.error(f"Error connecting to {url}: {exc}")
        return pd.DataFrame()

    data = response.json()
    if not isinstance(data, list):
        st.error(f"Unexpected response format from {url}: {data}")
        return pd.DataFrame()

    return pd.DataFrame(data)


@st.cache_data(show_spinner=False)
def get_events_per_day() -> pd.DataFrame:
    return fetch_dataframe(ANALYTICS_ENDPOINTS["events_per_day"])


@st.cache_data(show_spinner=False)
def get_tokens_per_user() -> pd.DataFrame:
    return fetch_dataframe(ANALYTICS_ENDPOINTS["tokens_per_user"])


@st.cache_data(show_spinner=False)
def get_tokens_by_model() -> pd.DataFrame:
    return fetch_dataframe(ANALYTICS_ENDPOINTS["tokens_by_model"])


st.set_page_config(page_title="Cursor Usage Analytics", layout="wide")
st.title("Cursor Usage Analytics Dashboard")

# Add a refresh button to clear cache and reload data
if st.button("🔄 Обновить данные", help="Обновить данные из CSV файла"):
    st.cache_data.clear()
    st.rerun()


events_tab, users_tab, models_tab = st.tabs([
    "Events per day",
    "Tokens per user",
    "Tokens by model",
])

with events_tab:
    st.header("Events per day")
    events_df = get_events_per_day()
    if not events_df.empty:
        line_fig = px.line(events_df, x="date", y="requests_count", markers=True)
        line_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(line_fig, use_container_width=True)
    st.dataframe(events_df, use_container_width=True)

with users_tab:
    st.header("Tokens per user")
    tokens_user_df = get_tokens_per_user()
    if not tokens_user_df.empty:
        bar_fig = px.bar(tokens_user_df, x="user", y="total_tokens", text="total_tokens")
        bar_fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        bar_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(bar_fig, use_container_width=True)
    st.dataframe(tokens_user_df, use_container_width=True)

with models_tab:
    st.header("Tokens by model")
    tokens_model_df = get_tokens_by_model()
    if not tokens_model_df.empty:
        pie_fig = px.pie(tokens_model_df, names="model", values="total_tokens")
        pie_fig.update_traces(textinfo="label+percent")
        pie_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(pie_fig, use_container_width=True)
    st.dataframe(tokens_model_df, use_container_width=True)
