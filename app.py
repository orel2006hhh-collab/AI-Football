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
    
    # Обновление данных вручную
    if st.button("🔄 Обновить данные сейчас"):
        with st.spinner("Обновление данных..."):
            scheduler.daily_update()
        st.success("Данные обновлены!")
        st.rerun()
    
    st.divider()
    
    # Фильтр по лигам
    st.subheader("🏆 Фильтр по лигам")
    all_leagues = ["Все лиги", "PL", "BL1", "SA", "PD", "FL1"]
    selected_league = st.selectbox("Выберите лигу", all_leagues)
    
    st.divider()
    
    # Статистика
    st.subheader("📈 Статистика прогнозов")
    stats = db.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего прогнозов", stats['total'])
    with col2:
        st.metric("Верных", stats['correct'])
    with col3:
        st.metric("Точность", f"{stats['accuracy']:.1f}%")
    
    # График точности
    if stats['total'] > 0:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = stats['accuracy'],
            title = {'text': "Точность прогнозов"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 66
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

# Получение предстоящих матчей
upcoming_matches = db.get_upcoming_matches()

if selected_league != "Все лиги":
    upcoming_matches = upcoming_matches[upcoming_matches['league'] == selected_league]

if upcoming_matches.empty:
    st.info("📭 Нет предстоящих матчей. Нажмите 'Обновить данные' для загрузки.")
    st.stop()

# Получение прогнозов для всех матчей
predictions = {}
for _, match in upcoming_matches.iterrows():
    # Здесь нужно получить прогноз из БД
    # Для демонстрации создаем заглушку
    prediction = {
        'home_win': 0.45,
        'draw': 0.28,
        'away_win': 0.27,
        'over': 0.52,
        'under': 0.48,
        'confidence': 'medium',
        'most_likely': 'home_win',
        'total_line': 2.5,
        'reasoning': "Пример обоснования прогноза..."
    }
    predictions[match['match_id']] = prediction

# Определение самого надежного прогноза
best_match_id, best_score = model.get_top_prediction(predictions)

# Отображение матчей
st.header(f"📅 Предстоящие матчи ({len(upcoming_matches)})")

for idx, match in upcoming_matches.iterrows():
    pred = predictions.get(match['match_id'], {})
    
    # Определяем CSS класс для уверенности
    confidence_class = ""
    if pred.get('confidence') == 'high':
        confidence_class = "high-confidence"
    elif pred.get('confidence') == 'medium':
        confidence_class = "medium-confidence"
    else:
        confidence_class = "low-confidence"
    
    # Отметка о надежном прогнозе
    is_top_prediction = (match['match_id'] == best_match_id)
    
    with st.container():
        st.markdown(f'<div class="prediction-card {confidence_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            # Информация о матче
            match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
            st.markdown(f"### {match['home_team']} 🆚 {match['away_team']}")
            st.caption(f"🏆 {match['league']} | 📅 {match_date.strftime('%d.%m.%Y %H:%M')}")
            
            if is_top_prediction:
                st.markdown("⭐ **НАДЕЖНЫЙ ПРОГНОЗ** ⭐")
        
        with col2:
            # Прогноз
            most_likely = pred.get('most_likely', 'unknown')
            if most_likely == 'home_win':
                outcome_text = f"🏠 **Победа {match['home_team']}**"
            elif most_likely == 'away_win':
                outcome_text = f"✈️ **Победа {match['away_team']}**"
            else:
                outcome_text = "🤝 **Ничья**"
            
            st.markdown(outcome_text)
            
            # Вероятности
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Хозяева", f"{pred.get('home_win', 0):.1%}")
            with col_b:
                st.metric("Ничья", f"{pred.get('draw', 0):.1%}")
            with col_c:
                st.metric("Гости", f"{pred.get('away_win', 0):.1%}")
            
            # Тотал
            total_pred = "OVER" if pred.get('over', 0) > pred.get('under', 0) else "UNDER"
            st.metric(f"Тотал {pred.get('total_line', 2.5)}", 
                     f"{total_pred} ({max(pred.get('over', 0), pred.get('under', 0)):.1%})")
        
        with col3:
            # Уверенность
            confidence = pred.get('confidence', 'low')
            if confidence == 'high':
                st.success("🎯 Высокая уверенность")
            elif confidence == 'medium':
                st.warning("📊 Средняя уверенность")
            else:
                st.error("⚠️ Низкая уверенность")
            
            # Кнопка деталей
            if st.button("📊 Детали", key=f"details_{match['match_id']}"):
                st.session_state[f"show_details_{match['match_id']}"] = not st.session_state.get(f"show_details_{match['match_id']}", False)
        
        # Детальное обоснование
        if st.session_state.get(f"show_details_{match['match_id']}", False):
            st.markdown("---")
            st.markdown("### 📋 Детальный анализ прогноза")
            st.markdown(pred.get('reasoning', "Нет подробного анализа"))
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Кнопка обновления внизу
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Обновить страницу", use_container_width=True):
        st.rerun()

# Автообновление каждые 5 минут (опционально)
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:  # 5 минут
    st.session_state.last_refresh = time.time()
    st.rerun()

# Footer
st.divider()
st.caption("⚽ Прогнозы основаны на статистическом анализе и модели Пуассона. Данные обновляются ежедневно в 10:00.")
