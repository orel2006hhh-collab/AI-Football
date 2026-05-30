import numpy as np
from scipy.stats import poisson
import pandas as pd
from datetime import datetime

class PoissonPredictionModel:
    """Модель Пуассона для предсказания футбольных матчей"""
    
    def __init__(self):
        self.league_averages = {
            'PL': {'home_avg': 1.52, 'away_avg': 1.18},
            'BL1': {'home_avg': 1.65, 'away_avg': 1.25},
            'SA': {'home_avg': 1.48, 'away_avg': 1.12},
            'PD': {'home_avg': 1.50, 'away_avg': 1.15},
            'FL1': {'home_avg': 1.45, 'away_avg': 1.10}
        }
    
    def simulate_matches(self, home_team, away_team, league, 
                        home_odds, draw_odds, away_odds, total_line,
                        team_form=None, h2h_stats=None, motivation=None):
        """
        Симуляция матча на основе модели Пуассона и дополнительных факторов
        
        Возвращает словарь с вероятностями исходов и детальным обоснованием
        """
        
        # Базовые вероятности из коэффициентов букмекеров
        base_home_prob = 1 / home_odds if home_odds > 0 else 0.33
        base_draw_prob = 1 / draw_odds if draw_odds > 0 else 0.33
        base_away_prob = 1 / away_odds if away_odds > 0 else 0.33
        
        # Нормализация
        total_prob = base_home_prob + base_draw_prob + base_away_prob
        base_home_prob /= total_prob
        base_draw_prob /= total_prob
        base_away_prob /= total_prob
        
        # Факторы для корректировки
        home_advantage = 1.15  # Базовая домашняя фора
        
        # Учет формы команд
        if team_form:
            if 'home_advantage' in team_form:
                home_advantage += team_form['home_advantage']
        
        # Учет мотивации
        if motivation:
            home_advantage *= motivation.get('home_motivation', 1.0)
            away_advantage = motivation.get('away_motivation', 1.0)
        else:
            away_advantage = 1.0
        
        # Расчет ожидаемых голов через модель Пуассона
        league_stats = self.league_averages.get(league, self.league_averages['PL'])
        
        lambda_home = league_stats['home_avg'] * home_advantage
        lambda_away = league_stats['away_avg'] * away_advantage
        
        # Симуляция 15 матчей
        simulations = []
        for _ in range(15):
            home_goals = np.random.poisson(lambda_home)
            away_goals = np.random.poisson(lambda_away)
            simulations.append({
                'home_goals': home_goals,
                'away_goals': away_goals,
                'total_goals': home_goals + away_goals,
                'winner': 'home' if home_goals > away_goals else ('away' if away_goals > home_goals else 'draw')
            })
        
        # Анализ результатов симуляций
        home_wins = sum(1 for s in simulations if s['winner'] == 'home')
        draws = sum(1 for s in simulations if s['winner'] == 'draw')
        away_wins = sum(1 for s in simulations if s['winner'] == 'away')
        over_total = sum(1 for s in simulations if s['total_goals'] > total_line)
        under_total = sum(1 for s in simulations if s['total_goals'] < total_line)
        
        sim_home_prob = home_wins / 15
        sim_draw_prob = draws / 15
        sim_away_prob = away_wins / 15
        sim_over_prob = over_total / 15
        sim_under_prob = under_total / 15
        
        # Финальные вероятности (смешиваем букмекерские и симуляционные)
        final_home_prob = (base_home_prob * 0.4 + sim_home_prob * 0.6)
        final_draw_prob = (base_draw_prob * 0.4 + sim_draw_prob * 0.6)
        final_away_prob = (base_away_prob * 0.4 + sim_away_prob * 0.6)
        final_over_prob = sim_over_prob
        final_under_prob = sim_under_prob
        
        # Определение уверенности
        max_prob = max(final_home_prob, final_draw_prob, final_away_prob)
        if max_prob > 0.55:
            confidence = "high"
        elif max_prob > 0.45:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Определение самого вероятного исхода
        outcomes = {
            'home_win': final_home_prob,
            'draw': final_draw_prob,
            'away_win': final_away_prob
        }
        most_likely = max(outcomes, key=outcomes.get)
        
        # Генерация обоснования
        reasoning = self.generate_reasoning(
            most_likely, final_home_prob, final_draw_prob, final_away_prob,
            final_over_prob, final_under_prob, total_line,
            home_advantage, team_form, h2h_stats, motivation,
            base_home_prob, sim_home_prob
        )
        
        return {
            'home_win': final_home_prob,
            'draw': final_draw_prob,
            'away_win': final_away_prob,
            'over': final_over_prob,
            'under': final_under_prob,
            'confidence': confidence,
            'most_likely': most_likely,
            'total_line': total_line,
            'expected_total': (final_over_prob * (total_line + 0.5) + final_under_prob * (total_line - 0.5)),
            'reasoning': reasoning,
            'simulations': simulations
        }
    
    def generate_reasoning(self, most_likely, home_prob, draw_prob, away_prob,
                          over_prob, under_prob, total_line,
                          home_advantage, team_form, h2h_stats, motivation,
                          bookmaker_prob, simulation_prob):
        """Генерация подробного обоснования прогноза"""
        
        reasoning_parts = []
        
        # Основной прогноз
        if most_likely == 'home_win':
            reasoning_parts.append(f"🏠 **Прогноз: Победа хозяев** с вероятностью {home_prob:.1%}")
        elif most_likely == 'away_win':
            reasoning_parts.append(f"✈️ **Прогноз: Победа гостей** с вероятностью {away_prob:.1%}")
        else:
            reasoning_parts.append(f"🤝 **Прогноз: Ничья** с вероятностью {draw_prob:.1%}")
        
        # Прогноз тотала
        if over_prob > under_prob:
            reasoning_parts.append(f"⚽ **Тотал: Больше {total_line}** (вероятность {over_prob:.1%})")
        else:
            reasoning_parts.append(f"⚽ **Тотал: Меньше {total_line}** (вероятность {under_prob:.1%})")
        
        # Обоснование
        reasoning_parts.append("\n**📊 Детальный анализ:**")
        
        if team_form:
            reasoning_parts.append(f"• Форма хозяев: {team_form.get('last_5', 'средняя')}")
        
        if h2h_stats:
            reasoning_parts.append(f"• Личные встречи: {h2h_stats.get('home_wins', 0)} побед хозяев, {h2h_stats.get('away_wins', 0)} побед гостей")
        
        if motivation:
            reasoning_parts.append(f"• Мотивация: {motivation.get('reason', 'Стандартная мотивация')}")
        
        reasoning_parts.append(f"• Домашнее преимущество: {home_advantage:.0%} к силе хозяев")
        
        reasoning_parts.append(f"\n**🎲 Результаты симуляции 15 матчей:**")
        reasoning_parts.append(f"• Победа хозяев: {home_prob:.1%}")
        reasoning_parts.append(f"• Ничья: {draw_prob:.1%}")
        reasoning_parts.append(f"• Победа гостей: {away_prob:.1%}")
        
        reasoning_parts.append(f"\n**💰 Анализ букмекеров:**")
        reasoning_parts.append(f"• Средние коэффициенты дают вероятность победы хозяев {bookmaker_prob:.1%}")
        reasoning_parts.append(f"• После учета дополнительных факторов вероятность изменилась до {simulation_prob:.1%}")
        
        return "\n".join(reasoning_parts)
    
    def get_top_prediction(self, predictions):
        """Определение самого надежного прогноза из всех матчей"""
        best_match = None
        best_score = 0
        
        for match_id, pred in predictions.items():
            # Оценка надежности на основе вероятности самого вероятного исхода
            max_prob = max(pred['home_win'], pred['draw'], pred['away_win'])
            score = max_prob
            
            # Дополнительный бонус за высокую уверенность
            if pred['confidence'] == 'high':
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = match_id
        
        return best_match, best_score
