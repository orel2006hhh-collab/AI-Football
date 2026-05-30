# test.py
import pandas as pd
import numpy as np
import json
import datetime

print('Pandas version:', pd.__version__)
print('NumPy version:', np.__version__)
print('Python works!')

# Создаем файл с данными
data = {
    'status': 'ok', 
    'timestamp': datetime.datetime.now().isoformat()
}

with open('data.json', 'w') as f:
    json.dump(data, f)

print('data.json created successfully!')
