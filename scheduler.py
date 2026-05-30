import schedule
import time
import threading
from datetime import datetime
import streamlit as st
from data_fetcher import DataFetcher
from database import Database
from prediction_model import PoissonPredictionModel

class Scheduler:
    def __init__(self):
        self.db = Database()
        self.fetcher = DataFetcher()
        self.model = PoissonPredictionModel()
        self.is_running = False
    
    def daily_update(self):
        """Ежедневное обновление данных в 10:00"""
        print(f"[{datetime.now()}] Начало ежедневного обновления...")
        
        # 1. Обновление результатов прошедших матчей
        self.update_past_matches_results()
        
        # 2. Удаление старых матчей
        self.db.cleanup_old_matches()
        
        # 3. Получение новых матчей
        self.fetch_new_matches()
        
        # 4. Обновление прогнозов
        self.update_predictions()
        
        # 5. Обновление статистики
        self.update_statistics()
        
        print(f"[{datetime.now()}] Ежедневное обновление завершено")
    
    def update_past_matches_results(self):
        """Обновление результатов прошедших матчей"""
        past_matches = self.db.get_past_matches(days_back=3)
        
        for _, match in past_matches.iterrows():
            # Здесь должен быть API-запрос к football-data.org для получения реального результата
            # Пока используем заглушку
            if match['status'] == 'upcoming':
                # Симуляция получения результата
                home_score = None  # В реальности получить из API
                away_score = None
                if home_score is not None:
                    self.db.update_match_result(match['match_id'], home_score, away_score)
    
    def fetch_new_matches(self):
        """Получение новых матчей на следующие дни"""
        new_matches = self.fetcher.fetch_upcoming_matches()
        
        if not new_matches.empty:
            # Сохраняем в БД
            self.db.save_matches(new_matches)
            
            # Получаем коэффициенты для каждого матча
            for _, match in new_matches.iterrows():
                odds_data = self.fetcher.fetch_odds_from_theoddsapi(
                    match['home_team'], match['away_team']
                )
                
                if odds_data:
                    avg_odds = self.fetcher.calculate_average_odds(odds_data)
                    if avg_odds:
                        # Сохраняем в БД
                        for bookmaker, stats in odds_data.items():
                            if bookmaker in avg_odds['full_data']:
                                self.db.save_bookmaker_stats(
                                    match['match_id'], bookmaker, stats
                            )
    
    def update_predictions(self):
        """Обновление прогнозов для всех предстоящих матчей"""
        upcoming_matches = self.db.get_upcoming_matches()
        
        for _, match in upcoming_matches.iterrows():
            # Получаем коэффициенты из БД
            # (упрощенно - в реальности нужно вытащить из bookmaker_stats)
            home_odds = match.get('home_odds', 2.5)
            draw_odds = match.get('draw_odds', 3.2)
            away_odds = match.get('away_odds', 2.8)
            total_line = match.get('total_line', 2.5)
            
            # Получаем дополнительные данные
            team_form = self.fetcher.get_team_form(match['home_team'], match['league'])
            h2h_stats = self.fetcher.get_h2h_stats(match['home_team'], match['away_team'], match['league'])
            motivation = self.fetcher.get_motivation_factor(match['home_team'], match['away_team'], match['league'])
            
            # Делаем прогноз
            prediction = self.model.simulate_matches(
                match['home_team'], match['away_team'], match['league'],
                home_odds, draw_odds, away_odds, total_line,
                team_form, h2h_stats, motivation
            )
            
            # Сохраняем прогноз
            self.db.save_prediction(match['match_id'], prediction)
    
    def update_statistics(self):
        """Обновление статистики прогнозов"""
        # Получаем завершенные матчи за последние дни
        past_matches = self.db.get_past_matches(days_back=2)
        
        for _, match in past_matches.iterrows():
            if match['status'] == 'finished':
                # Получаем прогноз для этого матча
                conn = self.db.db_path
                # (упрощенно - нужно вытащить прогноз из БД)
                # Сравниваем прогноз с фактическим результатом
                # Сохраняем в prediction_history
                pass
    
    def start(self):
        """Запуск планировщика в фоновом потоке"""
        # Запланировать ежедневное обновление в 10:00
        schedule.every().day.at("10:00").do(self.daily_update)
        
        # Также запускаем при старте
        self.daily_update()
        
        self.is_running = True
        
        def run_schedule():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
    
    def stop(self):
        """Остановка планировщика"""
        self.is_running = False
