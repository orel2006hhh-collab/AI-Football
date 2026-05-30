import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self, db_path="football_predictions.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создание всех таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица матчей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE,
                home_team TEXT,
                away_team TEXT,
                league TEXT,
                match_date TEXT,
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                over_odds REAL,
                under_odds REAL,
                total_line REAL,
                status TEXT DEFAULT 'upcoming',
                home_score INTEGER,
                away_score INTEGER
            )
        ''')
        
        # Таблица прогнозов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                prediction_home_win REAL,
                prediction_draw REAL,
                prediction_away_win REAL,
                prediction_over REAL,
                prediction_under REAL,
                confidence TEXT,
                reasoning TEXT,
                created_at TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        # Таблица статистики букмекеров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmaker_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                bookmaker TEXT,
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                over_odds REAL,
                under_odds REAL,
                total_line REAL,
                scraped_at TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        # Таблица истории прогнозов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                predicted_outcome TEXT,
                actual_outcome TEXT,
                predicted_total TEXT,
                actual_total TEXT,
                was_correct TEXT,
                match_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_matches(self, matches_df):
        """Сохранение матчей в БД"""
        conn = sqlite3.connect(self.db_path)
        matches_df.to_sql('matches', conn, if_exists='append', index=False)
        conn.close()
    
    def get_upcoming_matches(self):
        """Получение предстоящих матчей"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM matches 
            WHERE status = 'upcoming' 
            AND datetime(match_date) > datetime('now')
            ORDER BY match_date ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_past_matches(self, days_back=7):
        """Получение прошедших матчей за последние N дней"""
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT * FROM matches 
            WHERE datetime(match_date) < datetime('now')
            AND datetime(match_date) > datetime('now', '-{days_back} days')
            ORDER BY match_date DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_match_result(self, match_id, home_score, away_score):
        """Обновление результата матча"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE matches 
            SET status = 'finished', home_score = ?, away_score = ?
            WHERE match_id = ?
        ''', (home_score, away_score, match_id))
        conn.commit()
        conn.close()
    
    def save_prediction(self, match_id, prediction_data):
        """Сохранение прогноза"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO predictions 
            (match_id, prediction_home_win, prediction_draw, 
             prediction_away_win, prediction_over, prediction_under, 
             confidence, reasoning, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            prediction_data['home_win'],
            prediction_data['draw'],
            prediction_data['away_win'],
            prediction_data['over'],
            prediction_data['under'],
            prediction_data['confidence'],
            prediction_data['reasoning'],
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    def save_bookmaker_stats(self, match_id, bookmaker, stats):
        """Сохранение коэффициентов букмекеров"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookmaker_stats 
            (match_id, bookmaker, home_odds, draw_odds, away_odds, 
             over_odds, under_odds, total_line, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id, bookmaker, stats['home'], stats['draw'],
            stats['away'], stats['over'], stats['under'],
            stats['total_line'], datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    def update_prediction_history(self, match_id, predicted_outcome, actual_outcome, 
                                  predicted_total, actual_total, was_correct, match_date):
        """Обновление истории прогнозов для статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prediction_history 
            (match_id, predicted_outcome, actual_outcome, 
             predicted_total, actual_total, was_correct, match_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, predicted_outcome, actual_outcome, 
              predicted_total, actual_total, was_correct, match_date))
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Получение статистики успешности прогнозов"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN was_correct = 'yes' THEN 1 ELSE 0 END) as correct,
                AVG(CASE WHEN was_correct = 'yes' THEN 1.0 ELSE 0.0 END) as accuracy
            FROM prediction_history
            WHERE datetime(match_date) > datetime('now', '-30 days')
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) > 0 and df.iloc[0]['total'] > 0:
            return {
                'total': int(df.iloc[0]['total']),
                'correct': int(df.iloc[0]['correct']),
                'accuracy': float(df.iloc[0]['accuracy']) * 100
            }
        return {'total': 0, 'correct': 0, 'accuracy': 0}
    
    def cleanup_old_matches(self):
        """Удаление старых завершенных матчей (кроме истории)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Удаляем матчи старше 7 дней из основной таблицы
        cursor.execute('''
            DELETE FROM matches 
            WHERE status = 'finished' 
            AND datetime(match_date) < datetime('now', '-7 days')
        ''')
        conn.commit()
        conn.close()
