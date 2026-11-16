#!/usr/bin/env python3
"""
Биомеханическая феноменологическая модель диссеминации семян рогоза (Typha spp.).
Отслеживает динамику двух связанных параметров:
1. S(t) in [0, 1] - доля семян, оставшихся в початке (масса).
2. F(t) in [0, 1] - доля нераспущённых початков в популяции.
3. W(t) in [0, 1] - структурное выветривание и ослабление крепления плодиков.

Поддерживает Северное (август - май) и Южное (февраль - ноябрь) полушария,
пропуск отсутствующих значений в лаге архива ERA5 и защиту от будущих дат.
"""

import urllib.request
import json
import math
from datetime import datetime, timedelta
from collections import defaultdict


def fetch_open_meteo_hourly(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&wind_speed_unit=ms&timezone=auto"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "TyphaDispersalModel/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["hourly"]


def simulate_typha_dispersal(
    lat: float,
    lon: float,
    season_start_year: int = 2025,
    species: str = "latifolia",
) -> list[dict]:
    """
    Моделирует динамику облетания и распушения початков рогоза.
    Для Северного полушария (lat >= 0): 15 августа YYYY - 31 мая YYYY+1.
    Для Южного полушария (lat < 0): 15 февраля YYYY - 30 ноября YYYY.
    """
    if math.isnan(lat) or math.isnan(lon):
        raise ValueError("Координаты lat и lon должны быть действительными числами.")

    is_southern = lat < 0.0
    if is_southern:
        start_date = f"{season_start_year}-02-15"
        nominal_end = f"{season_start_year}-11-30"
    else:
        start_date = f"{season_start_year}-08-15"
        nominal_end = f"{season_start_year + 1}-05-31"

    now = datetime.now()
    # Защита от будущей даты старта (если передан год из будущего)
    while datetime.strptime(start_date, "%Y-%m-%d") > now:
        season_start_year -= 1
        if is_southern:
            start_date = f"{season_start_year}-02-15"
            nominal_end = f"{season_start_year}-11-30"
        else:
            start_date = f"{season_start_year}-08-15"
            nominal_end = f"{season_start_year + 1}-05-31"

    # Срез с учётом 5-дневного лага архива ERA5
    cutoff_date = now - timedelta(days=5)
    planned_end = datetime.strptime(nominal_end, "%Y-%m-%d")
    if planned_end > now:
        end_date = min(nominal_end, cutoff_date.strftime("%Y-%m-%d"))
    else:
        end_date = nominal_end

    # Если срез архива всё ещё раньше даты старта (сезон начался менее 5 дней назад)
    while datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
        season_start_year -= 1
        if is_southern:
            start_date = f"{season_start_year}-02-15"
            nominal_end = f"{season_start_year}-11-30"
        else:
            start_date = f"{season_start_year}-08-15"
            nominal_end = f"{season_start_year + 1}-05-31"
        end_date = nominal_end

    hourly = fetch_open_meteo_hourly(lat, lon, start_date, end_date)

    times = hourly["time"]
    temps = hourly["temperature_2m"]
    rhs = hourly["relative_humidity_2m"]
    precips = hourly["precipitation"]
    winds = hourly["wind_speed_10m"]

    # Калиброванные видовые параметры
    if species == "angustifolia":
        rh_crit_base = 48.0
        k_base = 0.011
        k_fluff = 0.008
    else:  # Typha latifolia
        rh_crit_base = 52.0
        k_base = 0.015
        k_fluff = 0.012

    # Начальные состояния
    S = 1.0          # Доля оставшихся семян [0..1]
    F = 1.0          # Доля нераспущённых початков в популяции [0..1]
    W = 0.10         # Индекс выветривания початка [0..1]
    rh_tissue = 85.0 # Влажность тканей пистиллодиев (%)

    tau = 1.5        # Постоянная времени влагообмена (часы)
    u_crit = 1.5     # Порог скорости ветра (м/с)
    k_u = 0.35       # Аэродинамический коэффициент

    monthly_dispersed = defaultdict(float)
    monthly_fluffed = defaultdict(float)
    monthly_weathering = {}
    monthly_unfluffed = {}

    prev_temp = None

    for i in range(len(times)):
        # Пропуск пропущенных часов из-за лага архива
        if temps[i] is None or rhs[i] is None:
            continue

        t_cur = temps[i]
        rh_cur = rhs[i]
        p_cur = precips[i] if precips[i] is not None else 0.0
        u_cur = winds[i] if winds[i] is not None else 0.0

        # А. Инерция влажности тканей пистиллодиев
        if p_cur > 0.1:
            rh_tissue = 100.0
        else:
            rh_tissue += (1.0 / tau) * (rh_cur - rh_tissue)

        # Б. Накопление структурного выветривания
        freeze_thaw = 0.0
        if prev_temp is not None:
            if (t_cur < 0.0 <= prev_temp) or (t_cur >= 0.0 > prev_temp):
                freeze_thaw = 0.015
        prev_temp = t_cur

        W = min(1.0, W + freeze_thaw + 0.00012)

        # В. Гигроскопический замок
        rh_crit = rh_crit_base + 22.0 * W
        if rh_tissue < rh_crit:
            H = (rh_crit - rh_tissue) / max(1.0, (rh_crit - 20.0))
        else:
            H = 0.0

        # Г. Физический унос семян (только при открытом замке H > 0 и ветре > u_crit)
        if H > 0.0 and u_cur > u_crit and S > 0.0:
            A = 1.0 - math.exp(-k_u * (u_cur - u_crit))
            dS = k_base * (0.15 + 0.85 * W) * H * A * S
            dS = min(S, dS)
            S -= dS
        else:
            dS = 0.0

        # Д. Визуальное распушение соцветий (только при H > 0)
        if H > 0.0 and F > 0.0:
            dF = k_fluff * (0.30 + 0.70 * W) * H * F
            dF = min(F, dF)
            F -= dF
        else:
            dF = 0.0

        month_key = times[i][:7]  # YYYY-MM
        monthly_dispersed[month_key] += dS * 100.0
        monthly_fluffed[month_key] += dF * 100.0
        monthly_weathering[month_key] = W
        monthly_unfluffed[month_key] = F * 100.0

    # Формирование результатов
    results = []
    cumulative = 0.0

    for month in sorted(monthly_dispersed.keys()):
        disp = monthly_dispersed[month]
        cumulative += disp
        fluff = monthly_fluffed[month]
        unfluff = monthly_unfluffed[month]
        w_val = monthly_weathering[month]

        results.append({
            "month": month,
            "fluff_prob_pct": round(fluff, 1),
            "unfluffed_pct": round(unfluff, 1),
            "dispersed_pct": round(disp, 1),
            "cumulative_pct": round(min(100.0, cumulative), 1),
            "weathering_index": round(w_val, 2),
        })

    return results


if __name__ == "__main__":
    LAT, LON = 55.65, 37.50
    print(f"Тест для Москвы (55.65, 37.50):\n")
    for season in [2025, 2026]:
        print(f"=== Сезон {season}–{season+1} ===")
        forecast = simulate_typha_dispersal(LAT, LON, season_start_year=season, species="latifolia")
        print(f"{'Месяц':<8} | {'Распушение, %':<15} | {'Нераспущ., %':<14} | {'Сход dS, %':<12} | {'Остаток S, %':<13} | {'W'}")
        print("-" * 84)
        for row in forecast:
            rem_s = round(max(0.0, 100.0 - row["cumulative_pct"]), 1)
            print(
                f"{row['month']:<8} | "
                f"{row['fluff_prob_pct']:>13.1f}% | "
                f"{row['unfluffed_pct']:>12.1f}% | "
                f"{row['dispersed_pct']:>10.1f}% | "
                f"{rem_s:>11.1f}% | "
                f"{row['weathering_index']:>4.2f}"
            )
        print()
