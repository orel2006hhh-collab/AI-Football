import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from database import Database
from data_fetcher import DataFetcher
from prediction_model import PoissonPredictionModel
from scheduler import Scheduler
import time

# Настройка страницы
st.set_page_config(
    page_title="⚽ Футбольные прогнозы | AI Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилизация
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .high-confidence {
        border-left: 5px solid #00ff00;
        background-color: #e8f5e9;
    }
    .medium-confidence {
        border-left: 5px solid #ffa500;
    }
    .low-confidence {
        border-left: 5px solid #ff0000;
    }
    </style>
""", unsafe_allow_html=True)

# Инициализация компонентов
@st.cache_resource
def init_components():
    db = Database()
    fetcher = DataFetcher()
    model = PoissonPredictionModel()
    scheduler = Scheduler()
    return db, fetcher, model, scheduler

db, fetcher, model, scheduler = init_components()

# Запуск планировщика (только один раз)
if 'scheduler_started' not in st.session_state:
    scheduler.start()
    st.session_state.scheduler_started = True

# Заголовок
st.title("⚽ Футбольный AI Predictor")
st.markdown("*Прогнозы футбольных матчей на основе статистического анализа и симуляции*")

# Боковая панель с фильтрами
with st.sidebar:
    st.header("🔧 Настройки")
