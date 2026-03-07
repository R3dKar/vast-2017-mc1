import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as pltly
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
IMG_DIR = os.path.join(PROJECT_ROOT, "imgs", "rangers")
DATA_FILE = os.path.join(DATA_DIR, "sensors.csv")

os.makedirs(IMG_DIR, exist_ok=True)

# Загрузка данных
df = pd.read_csv(DATA_FILE, names=['Timestamp', 'car_id', 'car_type', 'gate_name'], skiprows=1, header=None)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
df = df.sort_values(['car_id', 'Timestamp']).reset_index(drop=True)

# Фильтрация только рейнджеров (2P)
ranger_df = df[df['car_type'] == '2P'].copy()
print(f"Найдено записей 2P машин: {len(ranger_df)}")
print(f"Уникальных машин-рейнджеров: {ranger_df['car_id'].nunique()}")

# Добавление временных признаков
ranger_df['hour'] = ranger_df['Timestamp'].dt.hour
ranger_df['day_of_week'] = ranger_df['Timestamp'].dt.dayofweek
ranger_df['date'] = ranger_df['Timestamp'].dt.date

# 1. Гистограмма по всем типам ворот в алфавитном порядке
print("\nСтроим гистограмму всех ворот...")
all_gate_types = sorted(df['gate_name'].unique())
gate_counts_full = ranger_df['gate_name'].value_counts().reindex(all_gate_types, fill_value=0)

plt.figure(figsize=(18, 8))
bars = plt.bar(range(len(all_gate_types)), gate_counts_full.values, color='steelblue', alpha=0.8)
plt.title('Попадание рейнджерами (2P) на датчики', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Датчик')
plt.ylabel('Количество проходов')
plt.xticks(range(len(all_gate_types)), all_gate_types, rotation=45, ha='right')

# Добавление значений над столбцами
for i, (bar, val) in enumerate(zip(bars, gate_counts_full.values)):
    if val > 0:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(gate_counts_full.values)*0.01,
                f'{int(val)}', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'ranger_all_gates_histogram.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Сохранено: ranger_all_gates_histogram.png")

# 2. Активность по времени и дням недели + длительность маршрутов
print("\nСтроим графики активности и длительности маршрутов...")

route_durations = []
for car_id, car_group in ranger_df.groupby('car_id'):
    car_group = car_group.sort_values('Timestamp')
    if len(car_group) > 1:
        duration = (car_group['Timestamp'].iloc[-1] - car_group['Timestamp'].iloc[0]).total_seconds() / 60  # в минутах
        route_durations.append(duration)

fig = plt.figure(figsize=(18, 14))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.2], hspace=0.3, wspace=0.25)

# По часам (верхний левый)
ax1 = fig.add_subplot(gs[0, 0])
hour_counts = ranger_df['hour'].value_counts().sort_index()
bars1 = ax1.bar(hour_counts.index, hour_counts.values, color='orange', alpha=0.8)
ax1.set_title('Активность по часам', fontweight='bold', fontsize=14)
ax1.set_xlabel('Час дня', fontsize=12)
ax1.set_ylabel('Количество проходов', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(0, 24, 2))

# По дням недели (верхний средний)
ax2 = fig.add_subplot(gs[0, 1])
day_counts = ranger_df['day_of_week'].value_counts().sort_index()
days_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
days_ru_full = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
bars2 = ax2.bar(range(len(day_counts)), day_counts.values, color='green', alpha=0.8)
ax2.set_title('Активность по дням недели', fontweight='bold', fontsize=14)
ax2.set_xlabel('День недели', fontsize=12)
ax2.set_ylabel('Количество проходов', fontsize=12)
ax2.set_xticks(range(len(day_counts)))
ax2.set_xticklabels([days_ru[i] for i in day_counts.index], rotation=0)
ax2.grid(True, alpha=0.3)

# Длительность маршрутов (верхний правый)
ax3 = fig.add_subplot(gs[0, 2])
if route_durations:
    bins = 20
    n, bins, patches = ax3.hist(route_durations, bins=bins, color='purple', alpha=0.7, edgecolor='black')
    ax3.set_title('Длительность маршрутов', fontweight='bold', fontsize=14)
    ax3.set_xlabel('Длительность (минуты)', fontsize=12)
    ax3.set_ylabel('Количество маршрутов', fontsize=12)
    ax3.grid(True, alpha=0.3)

    mean_duration = np.mean(route_durations)
    median_duration = np.median(route_durations)
    ax3.axvline(mean_duration, color='red', linestyle='--', linewidth=2, label=f'Среднее: {mean_duration:.1f} мин')
    ax3.axvline(median_duration, color='blue', linestyle='--', linewidth=2, label=f'Медиана: {median_duration:.1f} мин')
    ax3.legend(fontsize=10)

    print(f"\nСтатистика длительности маршрутов:")
    print(f"  Средняя длительность: {mean_duration:.2f} минут")
    print(f"  Медианная длительность: {median_duration:.2f} минут")
    print(f"  Минимальная длительность: {min(route_durations):.2f} минут")
    print(f"  Максимальная длительность: {max(route_durations):.2f} минут")
    print(f"  Стандартное отклонение: {np.std(route_durations):.2f} минут")
else:
    ax3.text(0.5, 0.5, 'Нет данных для анализа длительности', 
            ha='center', va='center', transform=ax3.transAxes, fontsize=12)
    ax3.set_title('Длительность маршрутов', fontweight='bold', fontsize=14)

# Тепловая карта (нижняя)
ax4 = fig.add_subplot(gs[1, :])  
heatmap_data = pd.crosstab(ranger_df['day_of_week'], ranger_df['hour'])
heatmap_data = heatmap_data.reindex(index=range(7), columns=range(24), fill_value=0)

sns.heatmap(heatmap_data, ax=ax4, cmap='YlOrRd', annot=True, fmt='d', 
            cbar_kws={'label': 'Количество проходов', 'shrink': 0.8},
            annot_kws={'size': 9}, square=False)
ax4.set_title('Тепловая карта активности (день недели x час)', fontweight='bold', fontsize=14, pad=15)
ax4.set_xlabel('Час дня', fontsize=12)
ax4.set_ylabel('День недели', fontsize=12)
ax4.set_yticklabels(days_ru_full, rotation=0)
ax4.set_xticks(np.arange(24) + 0.5)
ax4.set_xticklabels(range(24), rotation=0)


fig.suptitle('Анализ активности и маршрутов рейнджеров (2P)', fontsize=16, fontweight='bold', y=0.98)
plt.savefig(os.path.join(IMG_DIR, 'ranger_time_analysis.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Сохранено: ranger_time_analysis.png")

