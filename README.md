# Typha Dispersal Simulator & Biophysical Model

An open-source biomechanical simulation framework and interactive offline map application modeling the seed dispersal dynamics and hygroscopic locking of cattails (*Typha latifolia* and *Typha angustifolia*) driven by hourly ERA5 climate reanalysis data.

---

## Language / Язык
- [English Documentation](#english)
- [Русская документация](#русский)

---

<a name="english"></a>
## English

### Overview
Cattail spikes (*Typha* spp.) exhibit a distinct hygroscopic valve mechanism driven by modified sterile flowers (pistillodies). During rain or humid conditions, pistillodies absorb moisture and swell, sealing the inflorescence. Under low ambient humidity, the tissues desorb water, opening the spike and allowing wind to detach the plumose achenes.

This project implements:
1. **Dynamic hourly model (`typha_model.py`)**: Tracks seed retention $S(t)$, intact spike proportion $F(t)$, and structural weathering $W(t)$ across seasons.
2. **Interactive single-file web app (`typha_map_app.html`)**: An offline-capable, zero-dependency browser application featuring an embedded world map, bilingual UI (EN/RU), and interactive Chart.js visualizations.
3. **CLI tool (`typha_monthly_forecast.py`)**: Command-line simulation tool with high-resolution Matplotlib graphs.

### Mathematical Formulation
The model evaluates four key biophysical mechanisms on an hourly time step ($\Delta t = 1\text{ h}$):

1. **Tissue Moisture Inertia ($\text{RH}_{\text{tissue}}$)**:
   Accounts for delayed drying of inner spike layers ($\tau \approx 1.5\text{ h}$):
   $$\text{RH}_{\text{tissue}}(t) = \begin{cases} 100\%, & P(t) > 0.1\text{ mm} \\ \text{RH}_{\text{tissue}}(t-1) + \frac{\Delta t}{\tau} \left(\text{RH}(t) - \text{RH}_{\text{tissue}}(t-1)\right), & P(t) \le 0.1\text{ mm} \end{cases}$$

2. **Weathering Accumulation ($W \in [0, 1]$)**:
   Structural breakdown of pedicel hairs via freeze-thaw cycles and aging:
   $$\Delta W(t) = w_{\text{ft}} \cdot \mathbb{I}(T(t) \cdot T(t-1) < 0) + w_{\text{age}} \cdot \Delta t$$

3. **Hygroscopic Valve State ($H \in [0, 1]$)**:
   Opening threshold shifts upward as the spike weathers:
   $$\text{RH}_{\text{crit}}(t) = \text{RH}_{\text{crit\_base}} + 22.0 \cdot W(t)$$
   $$H(t) = \max\left(0, \frac{\text{RH}_{\text{crit}}(t) - \text{RH}_{\text{tissue}}(t)}{\text{RH}_{\text{crit}}(t) - 20}\right)$$

4. **Seed Shedding ($\Delta S$) and Spike Opening ($\Delta F$)**:
   $$\Delta S(t) = -k_{\text{base}} \cdot (0.15 + 0.85 W) \cdot H \cdot A(t) \cdot S(t) \cdot \Delta t$$
   $$\Delta F(t) = -k_{\text{fluff}} \cdot (0.30 + 0.70 W) \cdot H \cdot F(t) \cdot \Delta t$$
   where $A(t) = 1 - \exp(-k_u \cdot \max(0, U(t) - U_{\text{crit}}))$.

### Installation & Quick Start
```bash
git clone https://github.com/<username>/typha-dispersal-model.git
cd typha-dispersal-model
pip install -r requirements.txt
```

#### Run Web App
Open `typha_map_app.html` directly in any web browser, or launch:
```bash
python run_gui.py
```

#### CLI Forecast
```bash
python typha_monthly_forecast.py --lat 55.65 --lon 37.50 --season 2026 --species latifolia
```

---

<a name="русский"></a>
## Русский

### Описание
Початки рогоза (*Typha* spp.) обладают гигроскопическим механизмом: видоизменённые бесплодные цветки (пистиллодии) разбухают во влажную погоду и при дожде, плотно герметизируя початок. При высыхании ткани сжимаются, открывая доступ ветру к созревшим плодикам.

Проект включает:
1. **Биомеханическую феноменологическую модель (`typha_model.py`)**: Часовой дифференциальный расчёт динамики массы оставшихся семян $S(t)$, доли целых початков $F(t)$ и индекса структурного выветривания $W(t)$.
2. **Автономное веб-приложение (`typha_map_app.html`)**: Работает офлайн без API-ключей, содержит встроенную карту мира и переключатель языка (EN/RU).
3. **Консольный скрипт визуализации (`typha_monthly_forecast.py`)**: Построение графиков высокого разрешения.

### Запуск
```bash
# Запуск веб-интерфейса
python run_gui.py

# Расчёт в консоли
python typha_monthly_forecast.py --lat 55.65 --lon 37.50 --season 2026
```

---

## Scientific References / Научные публикации

1. **Yeo, R. R. (1964)**. *Life history of common cattail*. Weed Science, 12(4), 284–288.
2. **Krattinger, K. (1975)**. *Genetic mobility in Typha*. New Phytologist, 74(2), 333–340.
3. **Lozada-Gobilard, S., Stang, M., & Tielbörger, K. (2021)**. *Dispersal syndromes and the role of humidity in wind-dispersed plants: hygroscopic seed release*. Perspectives in Plant Ecology, Evolution and Systematics, 53, 125642.
4. **Schwendener, S. (1896)**. *Die Spaltöffnungen der Typha-Arten und die hygroskopischen Bewegungen der Pistillodien*. Sitzungsberichte der Königlich Preussischen Akademie der Wissenschaften zu Berlin.
