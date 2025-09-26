import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests import HTTPError
import time

BACKEND_URL = "http://backend:8000"
ANALYTICS_ENDPOINTS = {
    "events_per_day": "/analytics/events_per_day",
    "tokens_per_user": "/analytics/tokens_per_user",
    "tokens_by_model": "/analytics/tokens_by_model",
    "raw_data": "/analytics/raw_data",
}


def fetch_dataframe(endpoint: str, params: dict = None) -> pd.DataFrame:
    """Retrieve analytics data from the backend and convert to a dataframe."""

    url = f"{BACKEND_URL}{endpoint}"
    
    # Add timestamp to avoid browser caching
    if params is None:
        params = {}
    params["_t"] = str(int(time.time()))
    
    try:
        response = requests.get(url, params=params, timeout=10)
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


@st.cache_data(show_spinner=False)
def get_raw_data(start_date: str = None, end_date: str = None, user: str = None, model: str = None) -> pd.DataFrame:
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if user:
        params["user"] = user
    if model:
        params["model"] = model
    
    return fetch_dataframe(ANALYTICS_ENDPOINTS["raw_data"], params)


st.set_page_config(page_title="Cursor Usage Analytics", layout="wide")
st.title("Cursor Usage Analytics Dashboard")

# Add a refresh button to clear cache and reload data
if st.button("🔄 Обновить данные", help="Обновить данные из CSV файла"):
    # Clear all cached data
    st.cache_data.clear()
    # Force rerun to reload all data
    st.rerun()


raw_data_tab, events_tab, users_tab, models_tab = st.tabs([
    "📊 Сырые данные",
    "📈 Events per day",
    "👥 Tokens per user",
    "🤖 Tokens by model",
])

with raw_data_tab:
    st.header("📊 Сырые данные")
    
    # Create filter controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        start_date = st.date_input(
            "📅 Дата начала",
            value=None,
            help="Выберите дату начала периода"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 Дата окончания",
            value=None,
            help="Выберите дату окончания периода"
        )
    
    # Get unique users and models for the filters
    all_raw_data = get_raw_data()  # Get all data to extract unique values
    unique_users = ["Все пользователи"] + sorted(all_raw_data["user"].unique().tolist()) if not all_raw_data.empty else ["Все пользователи"]
    unique_models = ["Все модели"] + sorted(all_raw_data["model"].unique().tolist()) if not all_raw_data.empty else ["Все модели"]
    
    with col3:
        selected_user = st.selectbox(
            "👤 Пользователь",
            options=unique_users,
            help="Выберите пользователя для фильтрации"
        )
    
    with col4:
        selected_model = st.selectbox(
            "🤖 Модель",
            options=unique_models,
            help="Выберите модель для фильтрации"
        )
    
    # Prepare filter parameters
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None
    user_filter = selected_user if selected_user != "Все пользователи" else None
    model_filter = selected_model if selected_model != "Все модели" else None
    
    # Fetch filtered data
    raw_df = get_raw_data(start_date=start_date_str, end_date=end_date_str, user=user_filter, model=model_filter)
    
    if not raw_df.empty:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Всего записей", len(raw_df))
        
        with col2:
            st.metric("👥 Пользователей", raw_df["user"].nunique())
        
        with col3:
            total_tokens = raw_df["total_tokens"].sum()
            st.metric("🔢 Всего токенов", f"{total_tokens:,}")
        
        with col4:
            total_requests = raw_df["requests"].sum()
            st.metric("📊 Всего запросов", f"{total_requests:,}")
        
        st.divider()
        
        # Format the dataframe for better display
        display_df = raw_df.copy()
        
        # Convert date to more readable format
        if "date" in display_df.columns:
            display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Rename columns to Russian
        column_mapping = {
            "date": "Дата",
            "user": "Пользователь",
            "kind": "Тип",
            "model": "Модель",
            "max_mode": "Макс. режим",
            "input_with_cache": "Ввод (с кэшем)",
            "input_without_cache": "Ввод (без кэша)",
            "cache_read": "Чтение кэша",
            "output_tokens": "Выходные токены",
            "total_tokens": "Всего токенов",
            "requests": "Запросы"
        }
        
        display_df = display_df.rename(columns=column_mapping)
        
        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Дата": st.column_config.TextColumn("Дата", width="medium"),
                "Пользователь": st.column_config.TextColumn("Пользователь", width="medium"),
                "Модель": st.column_config.TextColumn("Модель", width="small"),
                "Всего токенов": st.column_config.NumberColumn("Всего токенов", format="%d"),
                "Выходные токены": st.column_config.NumberColumn("Выходные токены", format="%d"),
                "Запросы": st.column_config.NumberColumn("Запросы", format="%d"),
            }
        )
    else:
        st.info("📭 Нет данных для отображения с выбранными фильтрами")

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
