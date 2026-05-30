import os
from dotenv import load_dotenv

load_dotenv()

# API ключи (получить бесплатно на https://www.football-data.org/)
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "ваш_ключ_здесь")
THE_ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY", "ваш_ключ_здесь")

# Букмекеры для анализа
BOOKMAKERS = ["bet365", "pinnacle", "williamhill", "unibet"]

# Настройки обновления
UPDATE_HOUR = 10
UPDATE_MINUTE = 0

# Лиги для отслеживания
LEAGUES = [
    "PL",   # АПЛ
    "BL1",  # Бундеслига
    "SA",   # Серия А
    "PD",   # Ла Лига
    "FL1"   # Лига 1
]
