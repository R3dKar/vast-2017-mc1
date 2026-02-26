import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IMG_DIR = os.path.join(PROJECT_ROOT, "imgs")
DATA_FILE = os.path.join(DATA_DIR, "sensors.csv")

os.makedirs(IMG_DIR, exist_ok=True)

df = pd.read_csv(
    DATA_FILE,
    names=['Timestamp', 'car_id', 'car_type', 'gate_name'],
    skiprows=1, header=None
)

df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
df = df.sort_values(['car_id', 'Timestamp']).reset_index(drop=True)

df['date'] = df['Timestamp'].dt.date
df['hour'] = df['Timestamp'].dt.hour
df['weekday'] = df['Timestamp'].dt.weekday
df['time_bin'] = df['hour'] + df['Timestamp'].dt.minute/60

# Heatmap: Дни недели × Часы
pivot_week_hour = df.pivot_table(index='weekday', columns='hour',
                                 values='car_id', aggfunc='size', fill_value=0)

plt.figure(figsize=(20,10))
sns.heatmap(pivot_week_hour, annot=True, cmap='YlGnBu', fmt='d', annot_kws={"size":12})
plt.title('Heatmap: Дни недели × Часы', fontsize=16)
plt.ylabel('День недели (0=Пн, 6=Вс)', fontsize=14)
plt.xlabel('Час', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.savefig(os.path.join(IMG_DIR, "weekday_hour_heatmap.png"), dpi=400, bbox_inches='tight')
plt.close()

# Heatmap: Ворота × Время суток
df['time_bin_halfhour'] = (df['time_bin'] * 2).astype(int) / 2.0
pivot_gate_time = df.pivot_table(index='gate_name', columns='time_bin_halfhour',
                                 values='car_id', aggfunc='size', fill_value=0)

plt.figure(figsize=(14,6))
sns.heatmap(pivot_gate_time, cmap='OrRd')
plt.title('Heatmap: Ворота × Время суток (шаг 30 мин)')
plt.ylabel('Ворота')
plt.xlabel('Время суток (часы)')
plt.savefig(os.path.join(IMG_DIR, "gate_time_heatmap.png"), dpi=300, bbox_inches='tight')
plt.close()
