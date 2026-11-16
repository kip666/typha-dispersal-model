#!/usr/bin/env python3
"""
Скрипт расчета и визуализации динамики облетания рогоза (Typha spp.)
с одновременным расчетом вероятности распушения, доли нераспущённых початков
и физического уноса семян (на основе typha_model.py).

Использование:
    cmd /c python typha_monthly_forecast.py --lat 55.65 --lon 37.50 --season 2026 --species latifolia
"""

import argparse
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

try:
    from typha_model import simulate_typha_dispersal
except ImportError:
    print("Ошибка: файл typha_model.py должен находиться в той же директории!")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Моделирование динамики облетания рогоза (Typha) по сезонам (август - май)."
    )
    parser.add_argument("--lat", type=float, default=55.65, help="Широта (latitude), по умолчанию 55.65")
    parser.add_argument("--lon", type=float, default=37.50, help="Долгота (longitude), по умолчанию 37.50")
    parser.add_argument("--season", type=int, default=2026, help="Начальный год сезона созревания (например, 2026 или 2025)")
    parser.add_argument("--species", type=str, default="latifolia", choices=["latifolia", "angustifolia"],
                        help="Вид рогоза: 'latifolia' (широколистный) или 'angustifolia' (узколистный)")
    parser.add_argument("--output", type=str, default=None, help="Имя выходного графического файла (PNG)")
    return parser.parse_args()


def plot_simulation_results(results: list[dict], lat: float, lon: float, season_year: int, species: str, output_file: str):
    """Строит двухпанельный график с вероятностью распушения, сходом семян и кривыми остатков."""
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10.2), dpi=300, sharex=True, gridspec_kw={'height_ratios': [1.3, 0.85]})

    months = [r["month"] for r in results]
    fluff_prob = [r["fluff_prob_pct"] for r in results]
    unfluffed = [r["unfluffed_pct"] for r in results]
    dispersed = [r["dispersed_pct"] for r in results]
    cumulative = [r["cumulative_pct"] for r in results]
    remaining = [round(max(0.0, 100.0 - c), 1) for c in cumulative]
    weathering = [r["weathering_index"] for r in results]

    x = np.arange(len(months))
    width = 0.36

    # ------------------ Панель 1: Распушение, Сход семян и Кривые остатков ------------------
    ax1_ret = ax1.twinx()

    # Столбики: 1) Вероятность распушения, 2) Физический сброс семян
    b_fluff = ax1.bar(x - width/2, fluff_prob, width, label="Вероятность распушения соцветия (%) [визуальный фенотип]",
                      color="#f59e0b", alpha=0.9, edgecolor="black", linewidth=0.6, zorder=2)
    b_disp = ax1.bar(x + width/2, dispersed, width, label="Физический унос семян за месяц (%) [массовая доля dS]",
                     color="#3b82f6", alpha=0.85, edgecolor="black", linewidth=0.6, zorder=2)

    # Две кривые остатка:
    # 1. Зеленая линия: Остаток семян в початке S(t) (%)
    line_rem = ax1_ret.plot(x, remaining, color="#059669", linewidth=2.8, marker="o", markersize=6,
                            label="Остаток семян в початке S(t) (%) [масса семян]", zorder=5)
    # 2. Янтарная пунктирная линия: Доля нераспущённых початков в популяции (%)
    line_unfluff = ax1_ret.plot(x, unfluffed, color="#d97706", linewidth=2.4, marker="s", markersize=6, linestyle="--",
                                label="Доля нераспущённых початков (%) [целые початки]", zorder=5)

    # Подписи значений над столбиками
    for rect in b_fluff:
        h = rect.get_height()
        if h >= 4.0:
            ax1.annotate(f"{h:.0f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2),
                         textcoords="offset points", ha="center", va="bottom",
                         fontsize=8.5, fontweight="bold", color="#b45309")
            
    for rect in b_disp:
        h = rect.get_height()
        if h >= 1.0:
            ax1.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 2),
                         textcoords="offset points", ha="center", va="bottom",
                         fontsize=8.0, fontweight="bold", color="#1d4ed8")

    species_title = "Typha latifolia (Рогоз широколистный)" if species == "latifolia" else "Typha angustifolia (Рогоз узколистный)"
    ax1.set_ylabel("Показатели месяца (%)", fontsize=11, fontweight="bold", color="#92400e")
    ax1_ret.set_ylabel("Кривые остатка (%)", fontsize=11, fontweight="bold", color="#047857")
    ax1.set_ylim(0, 110)
    ax1_ret.set_ylim(-5, 115)

    # Объединенная верхняя легенда (2 ряда по 2 элемента)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1_ret.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, 1.30),
               ncol=2, frameon=True, facecolor="white", edgecolor="#cbd5e1", framealpha=0.98, fontsize=9.2)

    lat_str = f"{abs(lat):.2f}° {'с.ш.' if lat >= 0 else 'ю.ш.'}"
    lon_str = f"{abs(lon):.2f}° {'в.д.' if lon >= 0 else 'з.д.'}"
    season_str = f"{season_year} г. (февраль – ноябрь)" if lat < 0 else f"{season_year}–{season_year + 1} гг. (август – май)"
    ax1.set_title(f"Моделирование облетания {species_title} (сезон {season_str})\n"
                  f"Координаты: {lat_str}, {lon_str}",
                  fontsize=12.5, fontweight="bold", pad=45)

    # ------------------ Панель 2: Кумулятивный сброс и Выветривание ------------------
    ax2_twin = ax2.twinx()

    b_cum = ax2.bar(x, cumulative, width=0.45, color="#64748b", alpha=0.75, edgecolor="black", linewidth=0.5,
                    label="Накопленная доля облетевших семян (%)")
    ax2.set_ylabel("Кумулятивный сброс (%)", fontsize=10, fontweight="bold", color="#334155")
    ax2.set_ylim(0, 105)

    l_w = ax2_twin.plot(x, weathering, color="#7c3aed", marker="s", linewidth=2.4, linestyle="--",
                        label="Индекс выветривания соцветия W [0..1]")
    ax2_twin.set_ylabel("Индекс выветривания W", fontsize=10, fontweight="bold", color="#7c3aed")
    ax2_twin.set_ylim(0, 1.15)

    ax2.set_xlabel("Месяц сезона", fontsize=11, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(months, fontsize=11, fontweight="bold")

    lines_a, labels_a = ax2.get_legend_handles_labels()
    lines_b, labels_b = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_a + lines_b, labels_a + labels_b, loc="upper left", frameon=True, facecolor="white", framealpha=0.9, fontsize=9.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nГрафик успешно сохранен: {output_file}")


def main():
    args = parse_args()
    if args.output is None:
        args.output = f"typha_simulation_{args.species}_{args.season}_{args.lat:.2f}_{args.lon:.2f}.png"

    lat_str = f"{abs(args.lat):.2f}° {'с.ш.' if args.lat >= 0 else 'ю.ш.'}"
    lon_str = f"{abs(args.lon):.2f}° {'в.д.' if args.lon >= 0 else 'з.д.'}"
    season_str = f"{args.season} г. (февраль – ноябрь)" if args.lat < 0 else f"{args.season}–{args.season + 1} гг. (август – май)"
    print(f"Запуск биомеханической модели typha_model.py:")
    print(f"-> Координаты: {lat_str}, {lon_str}")
    print(f"-> Сезон: {season_str}")
    print(f"-> Вид: {args.species}\n")

    results = simulate_typha_dispersal(
        lat=args.lat,
        lon=args.lon,
        season_start_year=args.season,
        species=args.species
    )

    print(f"{'Месяц':<8} | {'Распушение, %':<15} | {'Нераспущ., %':<14} | {'Сход dS, %':<13} | {'Остаток S, %':<13} | {'Индекс W'}")
    print("-" * 88)
    for row in results:
        rem_s = round(max(0.0, 100.0 - row["cumulative_pct"]), 1)
        print(
            f"{row['month']:<8} | "
            f"{row['fluff_prob_pct']:>13.1f}% | "
            f"{row['unfluffed_pct']:>12.1f}% | "
            f"{row['dispersed_pct']:>11.1f}% | "
            f"{rem_s:>11.1f}% | "
            f"{row['weathering_index']:>8.2f}"
        )

    plot_simulation_results(results, args.lat, args.lon, args.season, args.species, args.output)


if __name__ == "__main__":
    main()
