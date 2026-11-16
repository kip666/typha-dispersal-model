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

#### 1. Tissue Moisture Inertia ($\text{RH}_{\text{tissue}}$)
Accounts for delayed drying of inner spike layers ($\tau \approx 1.5\text{ h}$). Under precipitation ($P(t) > 0.1\text{ mm}$), the spike seals immediately:

$$
\text{RH}_{\text{tissue}}(t) = 
\begin{cases} 
100\%, & \text{if } P(t) > 0.1\text{ mm} \\ 
\text{RH}_{\text{tissue}}(t-1) + \dfrac{\Delta t}{\tau} \left(\text{RH}(t) - \text{RH}_{\text{tissue}}(t-1)\right), & \text{if } P(t) \le 0.1\text{ mm} 
\end{cases}
$$

#### 2. Structural Weathering Accumulation ($W \in [0, 1]$)
Freeze-thaw temperature oscillations across $0^\circ\text{C}$ and background senescence weaken the mechanical cohesion of pedicel hairs:

$$
\Delta W(t) = w_{\text{ft}} \cdot \mathbb{I}(T(t) \cdot T(t-1) < 0) + w_{\text{age}} \cdot \Delta t
$$

where $\mathbb{I}$ is the $0^\circ\text{C}$ crossing indicator ($w_{\text{ft}} \approx 0.015$ per cycle), and $w_{\text{age}} \approx 1.2 \times 10^{-4}\text{ h}^{-1}$ represents slow background aging.

#### 3. Hygroscopic Valve State ($H \in [0, 1]$)
The critical opening threshold shifts upward as the spike weathers — from dense autumn spikes up to loose spring spikes:

$$
\text{RH}_{\text{crit}}(t) = \text{RH}_{\text{crit},0} + 22.0 \cdot W(t)
$$

$$
H(t) = \max\left(0, \frac{\text{RH}_{\text{crit}}(t) - \text{RH}_{\text{tissue}}(t)}{\text{RH}_{\text{crit}}(t) - 20}\right)
$$

where $\text{RH}_{\text{crit},0} = 52.0\%$ for *T. latifolia* and $48.0\%$ for *T. angustifolia*.

#### 4. Seed Shedding ($\Delta S$) and Spike Opening ($\Delta F$)
When the valve is open ($H > 0$), wind speeds $U(t)$ above the stalk sway threshold ($U_{\text{crit}} = 1.5\text{ m/s}$) strip achenes:

$$
A(t) = 1 - \exp\left(-k_u \cdot \max(0, U(t) - U_{\text{crit}})\right)
$$

$$
\Delta S(t) = -k_{\text{base}} \cdot (0.15 + 0.85 W(t)) \cdot H(t) \cdot A(t) \cdot S(t) \cdot \Delta t
$$

$$
\Delta F(t) = -k_{\text{fluff}} \cdot (0.30 + 0.70 W(t)) \cdot H(t) \cdot F(t) \cdot \Delta t
$$

where $k_u = 0.35$, $k_{\text{base}} = 0.015$ ($0.011$ for *angustifolia*), and $k_{\text{fluff}} = 0.012$ ($0.008$ for *angustifolia*).

---

### CLI Arguments & Options (`typha_monthly_forecast.py`)

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--lat` | `float` | `55.65` | Latitude in decimal degrees, range `[-90.0 .. 90.0]`. |
| `--lon` | `float` | `37.50` | Longitude in decimal degrees, range `[-180.0 .. 180.0]`. |
| `--season` | `int` | `2026` | Ripening start year. Northern Hemisphere: Aug–May; Southern: automatically shifted to Feb–Nov. |
| `--species` | `str` | `latifolia` | Cattail species: `latifolia` (broadleaf) or `angustifolia` (narrowleaf). |
| `--output` | `str` | `None` | Path to output PNG chart (auto-generated if omitted). |

#### Usage Examples:
```bash
# Default simulation (Moscow SW, 2026 season)
python typha_monthly_forecast.py --lat 55.65 --lon 37.50 --season 2026 --species latifolia

# Southern Hemisphere (Melbourne, Australia)
python typha_monthly_forecast.py --lat -37.81 --lon 144.96 --season 2026 --species latifolia --output melbourne_2026.png

# Narrowleaf cattail in London
python typha_monthly_forecast.py --lat 51.51 --lon -0.12 --season 2025 --species angustifolia
```

#### Run Web App
Open `typha_map_app.html` directly in any web browser, or launch:
```bash
python run_gui.py
```

---

<a name="русский"></a>
## Русский

### Описание
Початки рогоза (*Typha* spp.) обладают гигроскопическим запорным механизмом: видоизменённые бесплодные цветки (пистиллодии) разбухают во влажную погоду и при дожде, плотно герметизируя початок. При снижении влажности воздуха ткани высыхают, открывая доступ ветру к созревшим плодикам.

Проект включает:
1. **Биомеханическую феноменологическую модель (`typha_model.py`)**: Часовой дифференциальный расчёт динамики массы оставшихся семян $S(t)$, доли целых початков $F(t)$ и индекса структурного выветривания $W(t)$.
2. **Автономное веб-приложение (`typha_map_app.html`)**: Работает офлайн без сторонних библиотек и API-ключей, содержит встроенную карту мира и переключатель языка (EN/RU).
3. **Консольный скрипт визуализации (`typha_monthly_forecast.py`)**: Построение двухпанельных графиков высокого разрешения через Matplotlib.

---

### Математическая модель процессов

Модель выполняет пошаговый расчёт с часовым интервалом ($\Delta t = 1\text{ ч}$):

#### 1. Инерция влажности тканей початка ($\text{RH}_{\text{tissue}}$)
Отражает запаздывание высыхания внутренних слоёв початка ($\tau \approx 1{,}5\text{ ч}$). При осадках ($P(t) > 0{,}1\text{ мм}$) початок герметизируется мгновенно:

$$
\text{RH}_{\text{tissue}}(t) = 
\begin{cases} 
100\%, & \text{если } P(t) > 0{,}1\text{ мм} \\ 
\text{RH}_{\text{tissue}}(t-1) + \dfrac{\Delta t}{\tau} \left(\text{RH}(t) - \text{RH}_{\text{tissue}}(t-1)\right), & \text{если } P(t) \le 0{,}1\text{ мм} 
\end{cases}
$$

#### 2. Накопление структурного выветривания ($W \in [0, 1]$)
Переходы температуры через $0^\circ\text{C}$ (циклы «замерзание — оттаивание») и фоновое старение разрушают механическое сцепление волосков плодиков с осью:

$$
\Delta W(t) = w_{\text{ft}} \cdot \mathbb{I}(T(t) \cdot T(t-1) < 0) + w_{\text{age}} \cdot \Delta t
$$

где $\mathbb{I}$ — индикатор перехода через $0^\circ\text{C}$ ($w_{\text{ft}} \approx 0{,}015$ за переход), а $w_{\text{age}} \approx 1{,}2 \times 10^{-4}\text{ ч}^{-1}$ — скорость фонового старения.

#### 3. Гигроскопический замок пистиллодиев ($H \in [0, 1]$)
Критическая влажность вскрытия линейно возрастает по мере выветривания:

$$
\text{RH}_{\text{crit}}(t) = \text{RH}_{\text{crit},0} + 22{,}0 \cdot W(t)
$$

$$
H(t) = \max\left(0, \frac{\text{RH}_{\text{crit}}(t) - \text{RH}_{\text{tissue}}(t)}{\text{RH}_{\text{crit}}(t) - 20}\right)
$$

где $\text{RH}_{\text{crit},0} = 52{,}0\%$ для *T. latifolia* и $48{,}0\%$ для *T. angustifolia*.

#### 4. Унос семян ($\Delta S$) и распушение початков ($\Delta F$)
При приоткрытом замке ($H > 0$) ветер со скоростью $U(t)$ выше порога раскачивания стебля ($U_{\text{crit}} = 1{,}5\text{ м/с}$) срывает плодики:

$$
A(t) = 1 - \exp\left(-k_u \cdot \max(0, U(t) - U_{\text{crit}})\right)
$$

$$
\Delta S(t) = -k_{\text{base}} \cdot (0{,}15 + 0{,}85 W(t)) \cdot H(t) \cdot A(t) \cdot S(t) \cdot \Delta t
$$

$$
\Delta F(t) = -k_{\text{fluff}} \cdot (0{,}30 + 0{,}70 W(t)) \cdot H(t) \cdot F(t) \cdot \Delta t
$$

где $k_u = 0{,}35$, $k_{\text{base}} = 0{,}015$ ($0{,}011$ для *angustifolia*), $k_{\text{fluff}} = 0{,}012$ ($0{,}008$ для *angustifolia*). Убыль нераспущённых початков $\Delta F(t)$ строго привязана к раскрытию замка ($H > 0$) и прекращается в периоды влажности.

---

### Параметры командной строки (`typha_monthly_forecast.py`)

| Параметр | Тип | По умолчанию | Описание |
| :--- | :--- | :--- | :--- |
| `--lat` | `float` | `55.65` | Географическая широта в градусах, диапазон `[-90.0 .. 90.0]`. |
| `--lon` | `float` | `37.50` | Географическая долгота в градусах, диапазон `[-180.0 .. 180.0]`. |
| `--season` | `int` | `2026` | Год начала сезона созревания (для Северного полушария: авг–май; для Южного автоматически: фев–ноя). |
| `--species` | `str` | `latifolia` | Вид рогоза: `latifolia` (широколистный) или `angustifolia` (узколистный). |
| `--output` | `str` | `None` | Путь к сохраняемому графику PNG (по умолчанию формируется автоматически). |

#### Примеры запуска:
```bash
# Базовый расчёт (Москва, сезон 2026 г.)
python typha_monthly_forecast.py --lat 55.65 --lon 37.50 --season 2026 --species latifolia

# Южное полушарие (Мельбурн, Австралия)
python typha_monthly_forecast.py --lat -37.81 --lon 144.96 --season 2026 --output melbourne.png

# Запуск графического веб-интерфейса
python run_gui.py
```

---

## Scientific References / Научные публикации

1. **Yeo, R. R. (1964)**. *Life history of common cattail*. Weed Science, 12(4), 284–288.
2. **Krattinger, K. (1975)**. *Genetic mobility in Typha*. New Phytologist, 74(2), 333–340.
3. **Lozada-Gobilard, S., Stang, M., & Tielbörger, K. (2021)**. *Dispersal syndromes and the role of humidity in wind-dispersed plants: hygroscopic seed release*. Perspectives in Plant Ecology, Evolution and Systematics, 53, 125642.
4. **Schwendener, S. (1896)**. *Die Spaltöffnungen der Typha-Arten und die hygroskopischen Bewegungen der Pistillodien*. Sitzungsberichte der Königlich Preussischen Akademie der Wissenschaften zu Berlin.
