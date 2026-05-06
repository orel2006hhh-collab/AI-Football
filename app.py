from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Данные оружия
WEAPONS = {
    'pistol': {'name': 'P250', 'damage': 25, 'fire_rate': 400, 'price': 300, 'reload_time': 1.5},
    'rifle': {'name': 'AK-47', 'damage': 40, 'fire_rate': 600, 'price': 2700, 'reload_time': 2.5},
    'sniper': {'name': 'AWP', 'damage': 100, 'fire_rate': 48, 'price': 4750, 'reload_time': 3.5},
    'shotgun': {'name': 'XM1014', 'damage': 70, 'fire_rate': 120, 'price': 2000, 'reload_time': 2.0}
}

# Данные карт
MAPS = {
    'dust2': {'name': 'Dust II', 'background': '#8B6914', 'cover_spots': 5},
    'mirage': {'name': 'Mirage', 'background': '#4169E1', 'cover_spots': 4},
    'inferno': {'name': 'Inferno', 'background': '#8B0000', 'cover_spots': 6}
}

@app.route('/')
def index():
    return render_template('index.html', weapons=WEAPONS, maps=MAPS)

@app.route('/api/weapons')
def get_weapons():
    return jsonify(WEAPONS)

@app.route('/api/maps')
def get_maps():
    return jsonify(MAPS)

if __name__ == '__main__':
    app.run(debug=True)
