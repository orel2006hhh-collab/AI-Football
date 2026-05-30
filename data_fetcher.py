import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from config import FOOTBALL_DATA_API_KEY, THE_ODDS_API_KEY, BOOKMAKERS, LEAGUES

class DataFetcher:
    def __init__(self):
        self.football_headers = {
            'X-Auth-Token': FOOTBALL_DATA_API_KEY
        }
    
    def fetch_upcoming_matches(self):
        """Получение предстоящих матчей с Football-Data.org"""
        matches = []
        
        for league in LEAGUES:
            url = f"https://api.football-data.org/v4/competitions/{league}/matches"
            params = {
                'status': 'SCHEDULED',
                'dateFrom': datetime.now().strftime('%Y-%m-%d'),
                'dateTo': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            }
            
            try:
                response = requests.get(url, headers=self.football_headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for match in data.get('matches', []):
                        matches.append({
                            'match_id': f"{match['homeTeam']['id']}_{match['awayTeam']['id']}_{match['utcDate']}",
                            'home_team': match['homeTeam']['name'],
                            'away_team': match['awayTeam']['name'],
                            'league': league,
                            'match_date': match['utcDate'],
                            'status': 'upcoming'
                        })
                else:
                    print(f"Error fetching {league}: {response.status_code}")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Exception fetching {league}: {e}")
        
        return pd.DataFrame(matches)
    
    def fetch_odds_from_theoddsapi(self, match_home, match_away, sport='soccer_epl'):
        """Получение коэффициентов с The Odds API"""
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
        params = {
            'apiKey': THE_ODDS_API_KEY,
            'regions': 'eu',
            'markets': 'h2h,totals',
            'bookmakers': ','.join(BOOKMAKERS)
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                odds_data = {}
                
                for bookmaker_data in data:
                    bookmaker = bookmaker_data['bookmaker']
                    
                    # H2H (победа/ничья)
                    h2h_market = next((m for m in bookmaker_data['markets'] if m['key'] == 'h2h'), None)
                    totals_market = next((m for m in bookmaker_data['markets'] if m['key'] == 'totals'), None)
                    
                    if h2h_market:
                        odds_data[bookmaker] = {
                            'home': h2h_market['outcomes'][0]['price'],
                            'draw': h2h_market['outcomes'][1]['price'],
                            'away': h2h_market['outcomes'][2]['price']
                        }
                    
                    if totals_market:
                        outcomes = totals_market['outcomes']
                        over_outcome = next((o for o in outcomes if o['name'] == 'Over'), None)
                        under_outcome = next((o for o in outcomes if o['name'] == 'Under'), None)
                        if over_outcome and under_outcome:
                            odds_data[bookmaker]['over'] = over_outcome['price']
                            odds_data[bookmaker]['under'] = under_outcome['price']
                            odds_data[bookmaker]['total_line'] = over_outcome['point']
                
                return odds_data
            else:
                print(f"Error fetching odds: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Exception fetching odds: {e}")
            return {}
    
    def calculate_average_odds(self, odds_data):
        """Расчет среднестатистических коэффициентов"""
        if not odds_data:
            return None
        
        home_odds = []
        draw_odds = []
        away_odds = []
        over_odds = []
        under_odds = []
        total_lines = []
        
        for bookmaker, stats in odds_data.items():
            if 'home' in stats:
                home_odds.append(stats['home'])
                draw_odds.append(stats['draw'])
                away_odds.append(stats['away'])
            if 'over' in stats:
                over_odds.append(stats['over'])
                under_odds.append(stats['under'])
                total_lines.append(stats['total_line'])
        
        avg_odds = {
            'home': sum(home_odds) / len(home_odds) if home_odds else 0,
            'draw': sum(draw_odds) / len(draw_odds) if draw_odds else 0,
            'away': sum(away_odds) / len(away_odds) if away_odds else 0,
            'over': sum(over_odds) / len(over_odds) if over_odds else 0,
            'under': sum(under_odds) / len(under_odds) if under_odds else 0,
            'total_line': sum(total_lines) / len(total_lines) if total_lines else 2.5
        }
        
        # Поиск аномалий
        anomalies = []
        for bookmaker, stats in odds_data.items():
            if 'home' in stats and abs(stats['home'] - avg_odds['home']) / avg_odds['home'] > 0.2:
                anomalies.append(f"{bookmaker}: home={stats['home']}")
            if 'away' in stats and abs(stats['away'] - avg_odds['away']) / avg_odds['away'] > 0.2:
                anomalies.append(f"{bookmaker}: away={stats['away']}")
        
        return {
            'average': avg_odds,
            'anomalies': anomalies,
            'full_data': odds_data
        }
    
    def get_team_form(self, team_name, league):
        """Получение формы команды (последние 5 матчей)"""
        # Здесь нужен API для получения истории матчей
        # Пока возвращаем заглушку
        return {
            'last_5': [1, 1, 0, 1, 0],  # 1 - победа, 0 - поражение
            'goals_scored': 8,
            'goals_conceded': 5,
            'home_advantage': 0.15  # +15% силы дома
        }
    
    def get_h2h_stats(self, home_team, away_team, league):
        """Получение истории личных встреч"""
        # Заглушка
        return {
            'total_matches': 10,
            'home_wins': 4,
            'draws': 3,
            'away_wins': 3,
            'last_match': 'home_win'
        }
    
    def get_motivation_factor(self, home_team, away_team, league):
        """Оценка мотивации команд в турнире"""
        # Заглушка - в реальности нужно получать турнирное положение
        return {
            'home_motivation': 1.0,  # коэффициент мотивации
            'away_motivation': 1.0,
            'reason': "Обычный матч турнира"
        }
    
    def get_player_form(self, team_name):
        """Получение формы ключевых игроков"""
        # Заглушка
        return {
            'key_players_available': 0.9,  # % доступных ключевых игроков
            'injuries': []
        }
