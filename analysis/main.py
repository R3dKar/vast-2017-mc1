"""
============================================================
Boonsong Lekagul Nature Preserve
"Patterns of Life" — Comprehensive Analysis
VAST Challenge 2017, Mini-Challenge 1
============================================================

Требования:
    pip install pandas matplotlib seaborn networkx scipy

Запуск:
    python lekagul_patterns_of_life.py

Датасет:
    Положите файл "Lekagul Sensor Data.csv" рядом со скриптом,
    либо укажите путь в переменной DATA_PATH ниже.
============================================================
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from collections import Counter
import itertools

matplotlib.rcParams["figure.dpi"] = 130
matplotlib.rcParams["font.family"] = "DejaVu Sans"
sns.set_style("whitegrid")

# ──────────────────────────────────────────────
# 0.  КОНФИГУРАЦИЯ
# ──────────────────────────────────────────────
DATA_PATH = "../data/sensors.csv"

VEHICLE_LABELS = {
    "1":  "Type-1: 2-axle car/moto",
    "2":  "Type-2: 2-axle truck",
    "2P": "Type-2P: Park Service",
    "3":  "Type-3: 3-axle truck",
    "4":  "Type-4: 4-axle truck",
    "5":  "Type-5: 2-axle bus",
    "6":  "Type-6: 3-axle bus",
}

# Цвета для типов транспорта
VTYPE_COLORS = {
    "1":  "#4C9BE8",
    "2":  "#F5A623",
    "2P": "#7ED321",
    "3":  "#D0021B",
    "4":  "#9013FE",
    "5":  "#50E3C2",
    "6":  "#B8860B",
}

# Типы сенсоров по префиксу имени
SENSOR_TYPES = {
    "entrance":     "Entrance",
    "general-gate": "General-Gate",
    "gate":         "Gate (restricted)",
    "ranger-stop":  "Ranger-Stop",
    "camping":      "Camping",
}

# ──────────────────────────────────────────────
# 1.  ЗАГРУЗКА И ПРЕДОБРАБОТКА ДАННЫХ
# ──────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    print(f"[1/7] Загрузка данных из «{path}»...")
    df = pd.read_csv(path, parse_dates=["Timestamp"])
    df.columns = ["timestamp", "car_id", "car_type", "gate_name"]
    df["car_type"] = df["car_type"].astype(str).str.strip()
    df["gate_name"] = df["gate_name"].str.strip().str.lower()
    df.sort_values(["car_id", "timestamp"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Временные производные
    df["hour"]       = df["timestamp"].dt.hour
    df["dow"]        = df["timestamp"].dt.dayofweek   # 0=Mon … 6=Sun
    df["dow_name"]   = df["timestamp"].dt.day_name()
    df["month"]      = df["timestamp"].dt.month
    df["date"]       = df["timestamp"].dt.date
    df["is_weekend"] = df["dow"].isin([5, 6])

    # Тип сенсора
    def sensor_type(name):
        for prefix, stype in SENSOR_TYPES.items():
            if name.startswith(prefix):
                return stype
        return "Unknown"

    df["sensor_type"] = df["gate_name"].apply(sensor_type)

    print(f"    Загружено строк: {len(df):,}")
    print(f"    Уникальных машин: {df['car_id'].nunique():,}")
    print(f"    Временной диапазон: {df['timestamp'].min()} → {df['timestamp'].max()}")
    return df


def build_trip_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Для каждого car_id строим агрегированные признаки одной поездки:
    - первый и последний сенсор (= вход и выход)
    - продолжительность пребывания в парке
    - количество уникальных сенсоров
    - последовательность типов сенсоров
    - максимальный тип сенсора (camping / ranger-stop / gate)
    """
    print("[2/7] Вычисление trip-статистики...")
    grp = df.groupby("car_id")

    stats = pd.DataFrame({
        "car_type":          grp["car_type"].first(),
        "first_gate":        grp["gate_name"].first(),
        "last_gate":         grp["gate_name"].last(),
        "first_time":        grp["timestamp"].min(),
        "last_time":         grp["timestamp"].max(),
        "n_events":          grp.size(),
        "n_unique_gates":    grp["gate_name"].nunique(),
        "n_unique_sensors":  grp["sensor_type"].nunique(),
        "visited_camping":   grp["sensor_type"].apply(lambda x: "Camping" in x.values),
        "visited_ranger":    grp["sensor_type"].apply(lambda x: "Ranger-Stop" in x.values),
        "visited_gate_restr":grp["sensor_type"].apply(lambda x: "Gate (restricted)" in x.values),
        "entry_hour":        grp["hour"].first(),
        "entry_dow":         grp["dow"].first(),
        "is_weekend":        grp["is_weekend"].first(),
    })

    stats["duration_h"] = (stats["last_time"] - stats["first_time"]).dt.total_seconds() / 3600.0
    stats["is_thrutraffic"] = (
        (stats["first_gate"] != stats["last_gate"]) &
        (stats["first_gate"].str.startswith("entrance")) &
        (stats["last_gate"].str.startswith("entrance")) &
        (stats["duration_h"] < 2.0)
    )
    stats["is_dayvisit"] = (
        stats["visited_camping"] &
        (stats["duration_h"] <= 12) &
        (~stats["is_thrutraffic"])
    )
    stats["is_overnight"] = (stats["duration_h"] > 12) & stats["visited_camping"]
    stats["is_ranger"]    = stats["car_type"] == "2P"
    stats["is_heavy_truck"] = stats["car_type"].isin(["3", "4"])

    return stats


# ──────────────────────────────────────────────
# 2.  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ПОСТРОЕНИЯ ГРАФИКОВ
# ──────────────────────────────────────────────

def _vtype_legend(ax, vtypes, title="Vehicle type"):
    patches = [mpatches.Patch(color=VTYPE_COLORS.get(v, "grey"),
                               label=VEHICLE_LABELS.get(v, v))
               for v in vtypes]
    ax.legend(handles=patches, title=title, fontsize=8, title_fontsize=8,
              loc="upper right", framealpha=0.85)


def save_and_show(fig, fname):
    fig.tight_layout()
    fig.savefig(fname, bbox_inches="tight")
    print(f"    → Сохранено: {fname}")
    plt.show()
    plt.close(fig)


# ───────────────────────���──────────────────────
# 3.  PATTERN 1 — COMMUTER / THROUGH-TRAFFIC
# ──────────────────────────────────────────────

def plot_pattern_throughtraffic(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 1: Быстрый транзит (вход через один Entrance, выход через другой,
    время < 2ч). Преобладают Type-1 машины. Пик утро/вечер в будни.
    """
    print("[3/7] Pattern 1 — Through-Traffic / Commuters...")

    tt = stats[stats["is_thrutraffic"]]
    subset = df[df["car_id"].isin(tt.index)]

    fig = plt.figure(figsize=(16, 9))
    fig.suptitle(
        "PATTERN 1 — Commuter / Through-Traffic\n"
        "Vehicles: mostly Type-1 (cars)  |  Route: Entrance → [minimal gates] → different Entrance  |  Duration < 2 h",
        fontsize=12, fontweight="bold", y=1.01
    )
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # --- (A) Hourly distribution
    ax1 = fig.add_subplot(gs[0, 0])
    hourly = tt.groupby("entry_hour").size()
    hourly.plot(kind="bar", ax=ax1, color="#4C9BE8", edgecolor="white")
    ax1.set_title("(A) Entry hour distribution", fontsize=10)
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("# trips")
    ax1.axvspan(-0.5, 3.5, alpha=0.07, color="navy", label="Night 0–3h")
    ax1.axvspan(6.5, 9.5, alpha=0.12, color="orange", label="Morning peak")
    ax1.axvspan(15.5, 18.5, alpha=0.12, color="red", label="Evening peak")
    ax1.legend(fontsize=7)

    # --- (B) Weekday vs Weekend
    ax2 = fig.add_subplot(gs[0, 1])
    dow_counts = tt.groupby("entry_dow").size()
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    colors_dow = ["#4C9BE8"]*5 + ["#F5A623"]*2
    ax2.bar(days, [dow_counts.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax2.set_title("(B) Day-of-week distribution", fontsize=10)
    ax2.set_ylabel("# trips")
    blue_p = mpatches.Patch(color="#4C9BE8", label="Weekday")
    ora_p  = mpatches.Patch(color="#F5A623", label="Weekend")
    ax2.legend(handles=[blue_p, ora_p], fontsize=8)

    # --- (C) Vehicle type breakdown
    ax3 = fig.add_subplot(gs[0, 2])
    vt_counts = tt["car_type"].value_counts()
    colors_vt = [VTYPE_COLORS.get(v, "grey") for v in vt_counts.index]
    ax3.bar(vt_counts.index, vt_counts.values, color=colors_vt, edgecolor="white")
    ax3.set_title("(C) Vehicle types", fontsize=10)
    ax3.set_ylabel("# trips")
    _vtype_legend(ax3, vt_counts.index)

    # --- (D) Entry–Exit gate pair heatmap
    ax4 = fig.add_subplot(gs[1, :2])
    pair_counts = tt.groupby(["first_gate", "last_gate"]).size().unstack(fill_value=0)
    sns.heatmap(pair_counts, annot=True, fmt="d", cmap="Blues", ax=ax4,
                linewidths=0.5, cbar_kws={"label": "# trips"})
    ax4.set_title("(D) Entry → Exit gate pairs", fontsize=10)
    ax4.set_xlabel("Exit gate")
    ax4.set_ylabel("Entry gate")
    ax4.tick_params(axis="x", rotation=35, labelsize=8)
    ax4.tick_params(axis="y", rotation=0,  labelsize=8)

    # --- (E) Duration distribution
    ax5 = fig.add_subplot(gs[1, 2])
    tt["duration_h"].clip(0, 2).hist(bins=30, ax=ax5, color="#50E3C2", edgecolor="white")
    ax5.set_title("(E) Trip duration (h)", fontsize=10)
    ax5.set_xlabel("Hours in park")
    ax5.set_ylabel("# trips")

    save_and_show(fig, "pattern1_through_traffic.png")


# ──────────────────────────────────────────────
# 4.  PATTERN 2 — DAY VISITORS
# ──────────────────────────────────────────────

def plot_pattern_dayvisitors(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 2: Дневные посетители. Приезжают утром, уходят днём/вечером,
    посещают кемпинг/природные зоны, не ночуют.
    """
    print("[4/7] Pattern 2 — Day Visitors...")

    dv = stats[stats["is_dayvisit"]]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "PATTERN 2 — Day Visitors (Recreational)\n"
        "Vehicles: Type-1/5/6  |  Route: Entrance → Camping sensors → same/different Entrance  |  Duration ≤ 12 h",
        fontsize=12, fontweight="bold"
    )

    # (A) Hour of entry
    ax = axes[0, 0]
    dv.groupby("entry_hour").size().plot(kind="bar", ax=ax, color="#4C9BE8", edgecolor="white")
    ax.set_title("(A) Entry hour")
    ax.set_xlabel("Hour"); ax.set_ylabel("# trips")

    # (B) Month distribution (seasonality)
    ax = axes[0, 1]
    dv_with_month = dv.copy()
    dv_with_month["month"] = dv["first_time"].dt.month
    dv_with_month.groupby("month").size().plot(kind="bar", ax=ax, color="#F5A623", edgecolor="white")
    ax.set_title("(B) Month (seasonality)")
    ax.set_xlabel("Month"); ax.set_ylabel("# trips")
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    ax.set_xticklabels([month_names.get(int(t.get_text()), t.get_text())
                        for t in ax.get_xticklabels()], rotation=45, fontsize=8)

    # (C) Weekday pattern
    ax = axes[0, 2]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_c = dv.groupby("entry_dow").size()
    colors_dow = ["#4C9BE8"]*5 + ["#F5A623"]*2
    ax.bar(days, [dow_c.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax.set_title("(C) Day of week")
    ax.set_ylabel("# trips")

    # (D) Vehicle type
    ax = axes[1, 0]
    vt = dv["car_type"].value_counts()
    ax.bar(vt.index, vt.values,
           color=[VTYPE_COLORS.get(v, "grey") for v in vt.index], edgecolor="white")
    ax.set_title("(D) Vehicle types")
    ax.set_ylabel("# trips")

    # (E) Duration distribution
    ax = axes[1, 1]
    dv["duration_h"].clip(0, 12).hist(bins=30, ax=ax, color="#9013FE", edgecolor="white")
    ax.set_title("(E) Duration (h)")
    ax.set_xlabel("Hours in park"); ax.set_ylabel("# trips")

    # (F) Most visited camping gates
    ax = axes[1, 2]
    camping_df = df[df["car_id"].isin(dv.index) & (df["sensor_type"] == "Camping")]
    top_camps = camping_df["gate_name"].value_counts().head(10)
    top_camps.plot(kind="barh", ax=ax, color="#50E3C2", edgecolor="white")
    ax.set_title("(F) Most visited camping gates")
    ax.set_xlabel("# visits")
    ax.invert_yaxis()

    save_and_show(fig, "pattern2_day_visitors.png")


# ──────────────────────────────────────────────
# 5.  PATTERN 3 — OVERNIGHT CAMPERS
# ──────────────────────────────────────────────

def plot_pattern_overnight(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 3: Многодневные кемперы. Продолжительность > 12ч,
    посещают camping-сенсоры. Пик — пятница/суббота прибытие.
    """
    print("[5/7] Pattern 3 — Overnight Campers...")

    oc = stats[stats["is_overnight"]]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "PATTERN 3 — Overnight / Extended Campers\n"
        "Vehicles: Type-1/2/5  |  Route: Entrance → Camping (extended stay)  |  Duration > 12 h",
        fontsize=12, fontweight="bold"
    )

    # (A) Duration distribution (capped at 120h)
    ax = axes[0, 0]
    oc["duration_h"].clip(0, 120).hist(bins=40, ax=ax, color="#D0021B", edgecolor="white")
    ax.axvline(24, color="navy", linestyle="--", label="24h")
    ax.axvline(48, color="green", linestyle="--", label="48h")
    ax.axvline(72, color="orange", linestyle="--", label="72h")
    ax.set_title("(A) Stay duration (h)")
    ax.set_xlabel("Hours"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    # (B) Entry hour
    ax = axes[0, 1]
    oc.groupby("entry_hour").size().plot(kind="bar", ax=ax, color="#4C9BE8", edgecolor="white")
    ax.set_title("(B) Arrival hour")
    ax.set_xlabel("Hour"); ax.set_ylabel("# trips")

    # (C) Day of week
    ax = axes[0, 2]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_c = oc.groupby("entry_dow").size()
    colors_dow = ["#4C9BE8"]*5 + ["#F5A623"]*2
    ax.bar(days, [dow_c.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax.set_title("(C) Arrival day of week")
    ax.set_ylabel("# trips")

    # (D) Month
    ax = axes[1, 0]
    oc_month = oc.copy()
    oc_month["month"] = oc["first_time"].dt.month
    oc_month.groupby("month").size().plot(kind="bar", ax=ax, color="#F5A623", edgecolor="white")
    ax.set_title("(D) Month (seasonality)")
    ax.set_xlabel("Month"); ax.set_ylabel("# trips")

    # (E) Vehicle type
    ax = axes[1, 1]
    vt = oc["car_type"].value_counts()
    ax.bar(vt.index, vt.values,
           color=[VTYPE_COLORS.get(v, "grey") for v in vt.index], edgecolor="white")
    ax.set_title("(E) Vehicle types")
    ax.set_ylabel("# trips")

    # (F) Camping gates visited
    ax = axes[1, 2]
    camp_df = df[df["car_id"].isin(oc.index) & (df["sensor_type"] == "Camping")]
    top = camp_df["gate_name"].value_counts().head(10)
    top.plot(kind="barh", ax=ax, color="#50E3C2", edgecolor="white")
    ax.set_title("(F) Most visited camping gates")
    ax.set_xlabel("# events")
    ax.invert_yaxis()

    save_and_show(fig, "pattern3_overnight_campers.png")


# ──────────────────────────────────────────────
# 6.  PATTERN 4 — PARK RANGERS (2P)
# ──────────────────────────────────────────────

def plot_pattern_rangers(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 4: Патрули рейнджеров (2P).
    Используют ограниченные gates, ranger-stops.
    Активны каждый день, весь день.
    """
    print("[6/7] Pattern 4 — Park Rangers (2P)...")

    rng = stats[stats["is_ranger"]]
    rng_df = df[df["car_type"] == "2P"]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "PATTERN 4 — Park Service / Rangers (Type-2P)\n"
        "Vehicles: Type-2P only  |  Route: Ranger-base → restricted Gates → Ranger-Stops  |  All year, daily",
        fontsize=12, fontweight="bold"
    )

    # (A) Hourly activity (all 2P events)
    ax = axes[0, 0]
    rng_df.groupby("hour").size().plot(kind="bar", ax=ax, color="#7ED321", edgecolor="white")
    ax.set_title("(A) Activity by hour")
    ax.set_xlabel("Hour"); ax.set_ylabel("# sensor events")

    # (B) Day of week
    ax = axes[0, 1]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_c = rng_df.groupby("dow").size()
    ax.bar(days, [dow_c.get(i, 0) for i in range(7)],
           color="#7ED321", edgecolor="white")
    ax.set_title("(B) Day of week")
    ax.set_ylabel("# sensor events")

    # (C) Sensor type usage
    ax = axes[0, 2]
    st = rng_df["sensor_type"].value_counts()
    colors_s = {"Entrance":"green","General-Gate":"blue",
                "Gate (restricted)":"red","Ranger-Stop":"gold","Camping":"orange"}
    ax.bar(st.index, st.values,
           color=[colors_s.get(s, "grey") for s in st.index], edgecolor="white")
    ax.set_title("(C) Sensor type usage")
    ax.set_ylabel("# events")
    ax.tick_params(axis="x", rotation=35, labelsize=8)

    # (D) Most visited gates
    ax = axes[1, 0]
    top_g = rng_df["gate_name"].value_counts().head(15)
    top_g.plot(kind="barh", ax=ax, color="#7ED321", edgecolor="white")
    ax.set_title("(D) Top 15 gates visited")
    ax.set_xlabel("# events"); ax.invert_yaxis()

    # (E) Duration per trip
    ax = axes[1, 1]
    rng["duration_h"].clip(0, 24).hist(bins=30, ax=ax, color="#50E3C2", edgecolor="white")
    ax.axvline(8, color="red", linestyle="--", label="8h shift")
    ax.set_title("(E) Trip duration (h)")
    ax.set_xlabel("Hours"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    # (F) Monthly activity
    ax = axes[1, 2]
    rng_df["month"].value_counts().sort_index().plot(kind="bar",
           ax=ax, color="#7ED321", edgecolor="white")
    ax.set_title("(F) Monthly activity")
    ax.set_xlabel("Month"); ax.set_ylabel("# events")

    save_and_show(fig, "pattern4_park_rangers.png")


# ──────────────────────────────────────────────
# 7.  PATTERN 5 — SUSPICIOUS HEAVY TRUCKS (NIGHT)
# ──────────────────────────────────────────────

def plot_pattern_heavy_trucks(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 5: Тяжёлые грузовики (Type-3/4) в ночное время
    в нетипичных местах. Потенциально — незаконный сброс химикатов.
    """
    print("[7/7] Pattern 5 — Suspicious Heavy Trucks (Night)...")

    ht = stats[stats["is_heavy_truck"]]
    ht_df = df[df["car_type"].isin(["3", "4"])]

    # Ночные поездки: въезд с 20:00 до 05:00
    ht_night = ht[(ht["entry_hour"] >= 20) | (ht["entry_hour"] <= 5)]
    ht_day   = ht[~((ht["entry_hour"] >= 20) | (ht["entry_hour"] <= 5))]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "PATTERN 5 — Heavy Trucks (Type-3/4): Night Intrusions ⚠️\n"
        "Vehicles: Type-3/4  |  Route: unusual deep routes  |  Night 20:00–05:00, weekdays",
        fontsize=12, fontweight="bold"
    )

    # (A) Hourly entry: night vs day
    ax = axes[0, 0]
    all_hourly = ht.groupby("entry_hour").size()
    colors_h = ["#D0021B" if (h >= 20 or h <= 5) else "#4C9BE8" for h in range(24)]
    ax.bar(range(24), [all_hourly.get(h, 0) for h in range(24)],
           color=colors_h, edgecolor="white")
    ax.set_title("(A) Entry hour (red = suspicious night)")
    ax.set_xlabel("Hour"); ax.set_ylabel("# trips")
    r_p = mpatches.Patch(color="#D0021B", label="Night (20–05)")
    b_p = mpatches.Patch(color="#4C9BE8", label="Day")
    ax.legend(handles=[r_p, b_p], fontsize=8)

    # (B) Night vs Day split pie
    ax = axes[0, 1]
    sizes = [len(ht_night), len(ht_day)]
    labels = [f"Night 20–05\n({len(ht_night)} trips)",
              f"Day 05–20\n({len(ht_day)} trips)"]
    ax.pie(sizes, labels=labels, colors=["#D0021B", "#4C9BE8"],
           autopct="%1.1f%%", startangle=90,
           textprops={"fontsize": 9})
    ax.set_title("(B) Night vs Day split")

    # (C) Day of week for NIGHT trips
    ax = axes[0, 2]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_night = ht_night.groupby("entry_dow").size()
    colors_dow = ["#D0021B"]*5 + ["#9013FE"]*2
    ax.bar(days, [dow_night.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax.set_title("(C) Night trips — day of week")
    ax.set_ylabel("# night trips")

    # (D) Type-3 vs Type-4 comparison
    ax = axes[1, 0]
    type_counts = ht.groupby(["car_type", "entry_hour"]).size().unstack(fill_value=0)
    for ct in type_counts.index:
        ax.plot(range(24), [type_counts.loc[ct].get(h, 0) for h in range(24)],
                label=VEHICLE_LABELS.get(ct, ct),
                color=VTYPE_COLORS.get(ct, "grey"), linewidth=2, marker="o", markersize=4)
    ax.set_title("(D) Hourly: Type-3 vs Type-4")
    ax.set_xlabel("Hour"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    # (E) Gates visited by NIGHT heavy trucks
    ax = axes[1, 1]
    night_ids = ht_night.index
    night_gates = ht_df[ht_df["car_id"].isin(night_ids)]["gate_name"].value_counts().head(12)
    night_gates.plot(kind="barh", ax=ax, color="#D0021B", edgecolor="white")
    ax.set_title("(E) Gates visited by night trucks")
    ax.set_xlabel("# events"); ax.invert_yaxis()

    # (F) Duration distribution night vs day
    ax = axes[1, 2]
    ht_night["duration_h"].clip(0, 24).hist(bins=25, ax=ax, color="#D0021B",
                                             alpha=0.7, label="Night", edgecolor="white")
    ht_day["duration_h"].clip(0, 24).hist(bins=25, ax=ax, color="#4C9BE8",
                                           alpha=0.7, label="Day", edgecolor="white")
    ax.set_title("(F) Duration: night vs day")
    ax.set_xlabel("Hours in park"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    save_and_show(fig, "pattern5_heavy_trucks_night.png")


# ──────────────────────────────────────────────
# 8.  PATTERN 6 — GROUP / BUS TOURS
# ──────────────────────────────────────────────

def plot_pattern_bus_tours(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Pattern 6: Автобусные/групповые туры (Type-5/6).
    Приезжают утром в будние дни, уходят днём. Пик весна/осень (школьный сезон).
    """
    buses = stats[stats["car_type"].isin(["5", "6"])]
    bus_df = df[df["car_type"].isin(["5", "6"])]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "PATTERN 6 — Group / Bus Tours (Type-5/6)\n"
        "Vehicles: 2-axle and 3-axle buses  |  Route: Entrance → Camping/nature areas  |  Weekday mornings",
        fontsize=12, fontweight="bold"
    )

    # (A) Entry hour
    ax = axes[0, 0]
    buses.groupby("entry_hour").size().plot(kind="bar", ax=ax, color="#50E3C2", edgecolor="white")
    ax.set_title("(A) Entry hour")
    ax.set_xlabel("Hour"); ax.set_ylabel("# bus trips")

    # (B) Day of week
    ax = axes[0, 1]
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_c = buses.groupby("entry_dow").size()
    colors_dow = ["#50E3C2"]*5 + ["#B8860B"]*2
    ax.bar(days, [dow_c.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax.set_title("(B) Day of week")
    ax.set_ylabel("# bus trips")

    # (C) Monthly
    ax = axes[0, 2]
    buses_month = buses.copy()
    buses_month["month"] = buses["first_time"].dt.month
    buses_month.groupby("month").size().plot(kind="bar", ax=ax, color="#B8860B", edgecolor="white")
    ax.set_title("(C) Month (school calendar effect?)")
    ax.set_xlabel("Month"); ax.set_ylabel("# bus trips")

    # (D) Duration
    ax = axes[1, 0]
    buses["duration_h"].clip(0, 24).hist(bins=30, ax=ax, color="#50E3C2", edgecolor="white")
    ax.axvline(8, color="red", ls="--", label="8h")
    ax.set_title("(D) Trip duration (h)")
    ax.set_xlabel("Hours"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    # (E) Type-5 vs Type-6
    ax = axes[1, 1]
    type_counts = buses.groupby(["car_type", "entry_hour"]).size().unstack(fill_value=0)
    for ct in type_counts.index:
        ax.plot(range(24), [type_counts.loc[ct].get(h, 0) for h in range(24)],
                label=VEHICLE_LABELS.get(ct, ct),
                color=VTYPE_COLORS.get(ct, "grey"), linewidth=2, marker="o", markersize=4)
    ax.set_title("(E) Hourly: Type-5 vs Type-6")
    ax.set_xlabel("Hour"); ax.set_ylabel("# trips")
    ax.legend(fontsize=8)

    # (F) Gates most used by buses
    ax = axes[1, 2]
    top_g = bus_df["gate_name"].value_counts().head(12)
    top_g.plot(kind="barh", ax=ax, color="#50E3C2", edgecolor="white")
    ax.set_title("(F) Top gates used by buses")
    ax.set_xlabel("# events"); ax.invert_yaxis()

    save_and_show(fig, "pattern6_bus_tours.png")


# ──────────────────────────────────────────────
# 9.  ИТОГОВЫЙ ОБЗОРНЫЙ ДАШБОРД
# ──────────────────────────────────────────────

def plot_overview_dashboard(df: pd.DataFrame, stats: pd.DataFrame):
    """
    Сводный дашборд: общая картина всего трафика.
    """
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle(
        "Boonsong Lekagul Preserve — Overall Traffic Dashboard\n"
        "All vehicle types | Full dataset overview",
        fontsize=14, fontweight="bold"
    )
    gs = gridspec.GridSpec(2, 4, figure=fig, hspace=0.5, wspace=0.4)

    # (A) Total events per sensor type
    ax = fig.add_subplot(gs[0, 0])
    st = df["sensor_type"].value_counts()
    colors_s = {"Entrance":"#2ecc71","General-Gate":"#3498db",
                "Gate (restricted)":"#e74c3c","Ranger-Stop":"#f1c40f","Camping":"#e67e22"}
    ax.barh(st.index, st.values,
            color=[colors_s.get(s, "grey") for s in st.index], edgecolor="white")
    ax.set_title("(A) Events per sensor type", fontsize=9)
    ax.set_xlabel("# events")
    ax.invert_yaxis()

    # (B) Traffic by hour of day
    ax = fig.add_subplot(gs[0, 1])
    df.groupby("hour").size().plot(kind="bar", ax=ax, color="#4C9BE8", edgecolor="white")
    ax.set_title("(B) All events by hour", fontsize=9)
    ax.set_xlabel("Hour"); ax.set_ylabel("# events")

    # (C) Vehicle type breakdown
    ax = fig.add_subplot(gs[0, 2])
    vt = df["car_type"].value_counts()
    ax.bar(vt.index, vt.values,
           color=[VTYPE_COLORS.get(v, "grey") for v in vt.index], edgecolor="white")
    ax.set_title("(C) Events by vehicle type", fontsize=9)
    ax.set_ylabel("# events")
    _vtype_legend(ax, vt.index)

    # (D) Day of week
    ax = fig.add_subplot(gs[0, 3])
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow_c = df.groupby("dow").size()
    colors_dow = ["#4C9BE8"]*5 + ["#F5A623"]*2
    ax.bar(days, [dow_c.get(i, 0) for i in range(7)], color=colors_dow, edgecolor="white")
    ax.set_title("(D) Events by day of week", fontsize=9)
    ax.set_ylabel("# events")

    # (E) Monthly total traffic
    ax = fig.add_subplot(gs[1, :2])
    monthly = df.groupby("month").size()
    monthly.plot(kind="bar", ax=ax, color="#9013FE", edgecolor="white")
    ax.set_title("(E) Monthly traffic volume", fontsize=9)
    ax.set_xlabel("Month"); ax.set_ylabel("# events")

    # (F) Heatmap: hour × dow for ALL events
    ax = fig.add_subplot(gs[1, 2:])
    pivot = df.groupby(["dow", "hour"]).size().unstack(fill_value=0)
    pivot.index = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][:len(pivot)]
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.3,
                cbar_kws={"label": "# events"}, xticklabels=2)
    ax.set_title("(F) Traffic heatmap: Hour × Day-of-week", fontsize=9)
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Day of week")

    save_and_show(fig, "overview_dashboard.png")


# ──────────────────────────────────────────────
# 10.  SUMMARY STATISTICS PRINT
# ──────────────────────────────────────────────

def print_summary(df: pd.DataFrame, stats: pd.DataFrame):
    print("\n" + "═"*60)
    print("  PATTERNS OF LIFE — SUMMARY STATISTICS")
    print("═"*60)

    total_trips = len(stats)
    tt   = stats["is_thrutraffic"].sum()
    dv   = stats["is_dayvisit"].sum()
    oc   = stats["is_overnight"].sum()
    rng  = stats["is_ranger"].sum()
    ht   = stats["is_heavy_truck"].sum()
    ht_n = ((stats["is_heavy_truck"]) &
            ((stats["entry_hour"] >= 20) | (stats["entry_hour"] <= 5))).sum()
    bus  = stats["car_type"].isin(["5","6"]).sum()

    print(f"  Total unique vehicles (trips):    {total_trips:>8,}")
    print(f"  Total sensor events:              {len(df):>8,}")
    print()
    print(f"  Pattern 1 — Through-traffic:      {tt:>8,}  ({100*tt/total_trips:.1f}%)")
    print(f"  Pattern 2 — Day visitors:         {dv:>8,}  ({100*dv/total_trips:.1f}%)")
    print(f"  Pattern 3 — Overnight campers:    {oc:>8,}  ({100*oc/total_trips:.1f}%)")
    print(f"  Pattern 4 — Park rangers (2P):    {rng:>8,}  ({100*rng/total_trips:.1f}%)")
    print(f"  Pattern 5 — Heavy trucks:         {ht:>8,}  ({100*ht/total_trips:.1f}%)")
    print(f"    of which NIGHT (20–05h):        {ht_n:>8,}  ({100*ht_n/max(ht,1):.1f}% of heavy)")
    print(f"  Pattern 6 — Bus/group tours:      {bus:>8,}  ({100*bus/total_trips:.1f}%)")
    print("═"*60)


# ───────────────────────���──────────────────────
# 11.  MAIN
# ──────────────────────────────────────────────

def main():
    df    = load_data(DATA_PATH)
    stats = build_trip_stats(df)

    print_summary(df, stats)

    plot_overview_dashboard(df, stats)
    plot_pattern_throughtraffic(df, stats)
    plot_pattern_dayvisitors(df, stats)
    plot_pattern_overnight(df, stats)
    plot_pattern_rangers(df, stats)
    plot_pattern_heavy_trucks(df, stats)
    plot_pattern_bus_tours(df, stats)

    print("\n✅ Все графики сохранены. Анализ завершён.")


if __name__ == "__main__":
    main()
