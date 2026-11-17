import os

with open("map_data_uri.txt", "r") as f:
    b64_map = f.read().strip()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Typha Dispersal Simulator</title>
  
  <!-- Chart.js for Interactive Charts -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    .map-container {{
      position: relative;
      width: 100%;
      aspect-ratio: 2 / 1;
      max-height: 480px;
      overflow: hidden;
      border-radius: 0.875rem;
      cursor: crosshair;
      user-select: none;
    }}
    .map-img {{
      width: 100%;
      height: 100%;
      object-fit: fill;
      display: block;
    }}
    .map-grid-line-h {{
      position: absolute;
      left: 0;
      right: 0;
      height: 1px;
      border-top: 1px dashed rgba(255, 255, 255, 0.2);
      pointer-events: none;
    }}
    .map-grid-line-v {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 1px;
      border-left: 1px dashed rgba(255, 255, 255, 0.2);
      pointer-events: none;
    }}
    .map-label {{
      position: absolute;
      font-size: 10px;
      font-family: monospace;
      color: rgba(255, 255, 255, 0.6);
      pointer-events: none;
      padding: 1px 4px;
      background: rgba(15, 23, 42, 0.6);
      border-radius: 3px;
    }}
    .map-pin {{
      position: absolute;
      transform: translate(-50%, -100%);
      pointer-events: none;
      transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
      z-index: 30;
    }}
    .hover-tooltip {{
      position: absolute;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid rgba(245, 158, 11, 0.6);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      color: #fef08a;
      font-family: monospace;
      z-index: 40;
      display: none;
      transform: translate(12px, -24px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.6);
    }}
    details summary::-webkit-details-marker {{
      display: none;
    }}
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans antialiased p-4 md:p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    
    <!-- Header -->
    <header class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
      <div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-xl bg-amber-500/20 text-amber-400 font-bold text-lg">🌾</span>
          <div>
            <h1 class="text-xl md:text-2xl font-bold tracking-tight text-white" id="t-app-title">
              Typha Dispersal Simulator
            </h1>
            <p class="text-xs md:text-sm text-slate-400 mt-0.5" id="t-app-subtitle">
              Biomechanical simulation of cattail (<em>Typha</em> spp.) seed dispersal based on ERA5 climate reanalysis
            </p>
          </div>
        </div>
      </div>

      <!-- Right Controls: Language Selector & Hemisphere Badge -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Language Switcher -->
        <div class="inline-flex items-center bg-slate-800 p-1 rounded-xl border border-slate-700 shadow-sm">
          <button id="lang-btn-en" onclick="setLanguage('en')" 
                  class="px-3 py-1 text-xs font-bold rounded-lg transition bg-amber-500 text-slate-950 shadow-sm">
            EN
          </button>
          <button id="lang-btn-ru" onclick="setLanguage('ru')" 
                  class="px-3 py-1 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white">
            RU
          </button>
        </div>

        <div id="hemisphere-badge" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
          Northern Hemisphere (Aug – May)
        </div>
      </div>
    </header>

    <!-- Top Block: Map & Location Selector -->
    <section class="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 md:p-5 shadow-xl space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="text-amber-400 font-semibold text-sm" id="t-step1-badge">📍 Step 1:</span>
          <span class="text-sm font-medium text-slate-200" id="t-step1-text">Click anywhere on the world map to select coordinates</span>
        </div>
        <!-- Quick Presets -->
        <div class="flex flex-wrap items-center gap-1.5 text-xs">
          <span class="text-slate-400 mr-1" id="t-presets-label">Presets:</span>
          <button onclick="setCoords(55.65, 37.50)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-moscow">Moscow (SW)</button>
          <button onclick="setCoords(55.57, 39.54)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-shatura">Shatura (East)</button>
          <button onclick="setCoords(54.91, 37.42)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-serpukhov">Serpukhov (South)</button>
          <button onclick="setCoords(56.34, 37.52)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-dmitrov">Dmitrov (North)</button>
          <button onclick="setCoords(59.93, 30.33)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-spb">St. Petersburg</button>
          <button onclick="setCoords(55.03, 82.92)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-novosibirsk">Novosibirsk</button>
          <button onclick="setCoords(43.58, 39.72)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-sochi">Sochi</button>
          <button onclick="setCoords(51.50, -0.12)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-london">London</button>
          <button onclick="setCoords(40.71, -74.00)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-newyork">New York</button>
          <button onclick="setCoords(35.68, 139.69)" class="px-2.5 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition" id="p-tokyo">Tokyo</button>
          <button onclick="setCoords(-37.81, 144.96)" class="px-2.5 py-1 rounded bg-sky-900/60 hover:bg-sky-800 text-sky-200 border border-sky-700/60 transition" id="p-melbourne">Melbourne (South)</button>
          <button onclick="setCoords(-33.92, 18.42)" class="px-2.5 py-1 rounded bg-sky-900/60 hover:bg-sky-800 text-sky-200 border border-sky-700/60 transition" id="p-capetown">Cape Town (South)</button>
        </div>
      </div>

      <!-- Static Equirectangular World Map with Embedded Base64 Image -->
      <div id="map-box" class="map-container border border-slate-700 shadow-inner bg-slate-950">
        <img id="world-map-img" src="{b64_map}" alt="World Map" class="map-img" />

        <!-- Parallels Grid Lines -->
        <div class="map-grid-line-h" style="top: 16.66%;"></div>
        <div class="map-label" style="top: 16.66%; left: 6px;">60°N</div>
        
        <div class="map-grid-line-h" style="top: 33.33%;"></div>
        <div class="map-label" style="top: 33.33%; left: 6px;">30°N</div>

        <div class="map-grid-line-h" style="top: 50.0%; border-top: 1px solid rgba(245, 158, 11, 0.4);"></div>
        <div id="map-label-equator" class="map-label" style="top: 50.0%; left: 6px; color: #f59e0b;">0° Equator</div>

        <div class="map-grid-line-h" style="top: 66.66%;"></div>
        <div class="map-label" style="top: 66.66%; left: 6px;">30°S</div>

        <div class="map-grid-line-h" style="top: 83.33%;"></div>
        <div class="map-label" style="top: 83.33%; left: 6px;">60°S</div>

        <!-- Meridians Grid Lines -->
        <div class="map-grid-line-v" style="left: 16.66%;"></div>
        <div class="map-grid-line-v" style="left: 33.33%;"></div>
        <div class="map-grid-line-v" style="left: 50.0%; border-left: 1px solid rgba(56, 189, 248, 0.4);"></div>
        <div id="map-label-greenwich" class="map-label" style="top: 6px; left: 50.0%; transform: translateX(-50%); color: #38bdf8;">0° Greenwich</div>
        
        <div class="map-grid-line-v" style="left: 66.66%;"></div>
        <div class="map-grid-line-v" style="left: 83.33%;"></div>

        <!-- Active Location Pin Marker -->
        <div id="pin-marker" class="map-pin">
          <div class="relative flex items-center justify-center">
            <span class="absolute w-5 h-5 rounded-full bg-amber-400 opacity-75 animate-ping"></span>
            <div class="relative w-7 h-7 flex items-center justify-center filter drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="#ef4444" stroke="#ffffff" stroke-width="1.5">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Hover Tooltip -->
        <div id="hover-tip" class="hover-tooltip"></div>
      </div>

      <!-- Controls Row: Inputs & Species & Season -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 pt-2">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1" id="t-label-lat">Latitude (-90..90)</label>
          <input type="number" id="lat-input" step="0.0001" min="-90" max="90" value="55.6500" 
                 class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-amber-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1" id="t-label-lon">Longitude (-180..180)</label>
          <input type="number" id="lon-input" step="0.0001" min="-180" max="180" value="37.5000" 
                 class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-amber-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1" id="t-label-species">Typha Species</label>
          <select id="species-select" class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-amber-500">
            <option value="latifolia" selected>Typha latifolia (broadleaf cattail)</option>
            <option value="angustifolia">Typha angustifolia (narrowleaf cattail)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-1" id="t-label-season">Ripening Season</label>
          <select id="season-select" class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-amber-500">
            <!-- Populated via JS -->
          </select>
        </div>
        <div class="flex items-end">
          <button id="calc-btn" onclick="runSimulation()" 
                  class="w-full py-2.5 px-4 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-sm shadow-lg shadow-amber-500/20 transition flex items-center justify-center gap-2">
            <span id="btn-icon">⚡</span>
            <span id="btn-text">Run Simulation</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Status & Notification -->
    <div id="status-bar" class="hidden p-3 rounded-xl text-xs flex items-center gap-2"></div>

    <!-- Results Section: Charts & Tables -->
    <section id="results-section" class="hidden space-y-6">
      
      <!-- Key Metric Badges (5 Cards) -->
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3.5">
        <div class="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-md">
          <div class="text-[11px] text-slate-400 uppercase tracking-wider font-semibold" id="t-metric-fluff-label">Peak Fluffing</div>
          <div id="metric-peak-fluff" class="text-xl font-bold font-mono text-amber-400 mt-1">—</div>
          <div class="text-[10px] text-slate-500 mt-0.5" id="t-metric-fluff-sub">Max monthly spike opening</div>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-md">
          <div class="text-[11px] text-slate-400 uppercase tracking-wider font-semibold" id="t-metric-unfluffed-label">Intact Spikes</div>
          <div id="metric-unfluffed" class="text-xl font-bold font-mono text-amber-300 mt-1">—</div>
          <div class="text-[10px] text-slate-500 mt-0.5" id="t-metric-unfluffed-sub">Remaining unopened F(t)</div>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-md">
          <div class="text-[11px] text-slate-400 uppercase tracking-wider font-semibold" id="t-metric-dispersed-label">Season Seed Shedding</div>
          <div id="metric-total-dispersed" class="text-xl font-bold font-mono text-blue-400 mt-1">—</div>
          <div class="text-[10px] text-slate-500 mt-0.5" id="t-metric-dispersed-sub">Physical seed loss dS</div>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-md">
          <div class="text-[11px] text-slate-400 uppercase tracking-wider font-semibold" id="t-metric-remaining-label">Remaining Seeds S(t)</div>
          <div id="metric-remaining" class="text-xl font-bold font-mono text-emerald-400 mt-1">—</div>
          <div class="text-[10px] text-slate-500 mt-0.5" id="t-metric-remaining-sub">Seed mass on spike axis</div>
        </div>
        <div class="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-md col-span-2 md:col-span-4 lg:col-span-1">
          <div class="text-[11px] text-slate-400 uppercase tracking-wider font-semibold" id="t-metric-weathering-label">Weathering Index W</div>
          <div id="metric-weathering" class="text-xl font-bold font-mono text-purple-400 mt-1">—</div>
          <div class="text-[10px] text-slate-500 mt-0.5" id="t-metric-weathering-sub">Axis degradation [0..1]</div>
        </div>
      </div>

      <!-- Chart 1: Monthly Fluffing Prob, Seed Dispersal & Both Retention Curves -->
      <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-xl space-y-3">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h3 class="font-bold text-base text-white" id="t-chart1-title">1. Dynamics of Spike Fluffing, Seed Dispersal & Retention Curves</h3>
            <p class="text-xs text-slate-400" id="t-chart1-sub">Bars: monthly spikes fluffed (amber) and physical seed loss dS (blue). Lines: remaining seed mass S(t) (green) and intact spikes F(t) (amber dashed).</p>
          </div>
          <div class="flex flex-wrap items-center gap-3 text-xs">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 bg-amber-500 rounded-sm"></span> <span id="t-leg-fluffed">Fluffed dF (%)</span></span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 bg-blue-500 rounded-sm"></span> <span id="t-leg-dispersed">Seed Shedding dS (%)</span></span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-1 bg-emerald-400 rounded-sm"></span> <span id="t-leg-rem-seeds">Seeds S(t) (%)</span></span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-1 border-t-2 border-dashed border-amber-300"></span> <span id="t-leg-unfluffed">Intact F(t) (%)</span></span>
          </div>
        </div>
        <div class="relative h-72 md:h-84 w-full">
          <canvas id="chart-dispersal"></canvas>
        </div>
      </div>

      <!-- Chart 2: Cumulative Dispersal & Weathering Index W -->
      <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-xl space-y-3">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h3 class="font-bold text-base text-white" id="t-chart2-title">2. Cumulative Seed Shedding & Axis Weathering Index W</h3>
            <p class="text-xs text-slate-400" id="t-chart2-sub">Grey bars: cumulative percentage of shed seeds. Purple line: structural weathering index W [0..1].</p>
          </div>
          <div class="flex items-center gap-3 text-xs">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 bg-slate-400 rounded-sm"></span> <span id="t-leg-cum">Cumulative (%)</span></span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-1 bg-purple-400 rounded-sm"></span> <span id="t-leg-w">Weathering W</span></span>
          </div>
        </div>
        <div class="relative h-64 md:h-72 w-full">
          <canvas id="chart-weathering"></canvas>
        </div>
      </div>

      <!-- Detailed Simulation Table -->
      <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 shadow-xl space-y-3 overflow-x-auto">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-base text-white" id="t-table-title">3. Summary of Biomechanical Simulation</h3>
          <span class="text-xs text-slate-400" id="t-table-sub">Differential simulation step: 1 hour</span>
        </div>
        <table class="w-full text-xs text-left text-slate-300 min-w-[850px]">
          <thead class="bg-slate-900/60 uppercase font-semibold text-slate-400 border-b border-slate-700">
            <tr>
              <th class="py-2.5 px-3" id="th-month">Month</th>
              <th class="py-2.5 px-3" id="th-fluffed">Fluffed dF, %</th>
              <th class="py-2.5 px-3 text-amber-300" id="th-unfluffed">Intact F, %</th>
              <th class="py-2.5 px-3" id="th-dispersed">Seed Loss dS, %</th>
              <th class="py-2.5 px-3" id="th-cumulative">Cumulative, %</th>
              <th class="py-2.5 px-3 text-emerald-400" id="th-remaining">Remaining Seeds S(t), %</th>
              <th class="py-2.5 px-3" id="th-weathering">Index W</th>
              <th class="py-2.5 px-3" id="th-status">Spike Status</th>
            </tr>
          </thead>
          <tbody id="table-body" class="divide-y divide-slate-800 font-mono">
            <!-- Populated via JS -->
          </tbody>
        </table>
      </div>

    </section>

    <!-- Collapsible Mathematical Model Description Accordion -->
    <section class="bg-slate-800/60 border border-slate-700 rounded-2xl overflow-hidden shadow-lg">
      <details class="group">
        <summary class="flex items-center justify-between p-4 md:p-5 cursor-pointer hover:bg-slate-800/80 transition list-none">
          <div class="flex items-center gap-3">
            <span class="text-amber-400 text-lg">📐</span>
            <span class="font-bold text-sm md:text-base text-white tracking-tight" id="t-accordion-title">
              Mathematical Model Formulation of Cattail Spikes (<em>Typha</em> spp.)
            </span>
          </div>
          <div class="flex items-center gap-2 text-xs text-amber-400 font-medium">
            <span class="group-open:hidden" id="t-acc-expand">Expand equations</span>
            <span class="hidden group-open:inline" id="t-acc-collapse">Collapse</span>
            <svg class="w-4 h-4 transform group-open:rotate-180 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </summary>

        <!-- English Mathematical Model Container -->
        <div id="model-desc-en" class="p-5 md:p-6 border-t border-slate-700/80 bg-slate-900/60 space-y-5 text-xs md:text-sm text-slate-300 leading-relaxed font-sans">
          <p>
            Based on established biophysical mechanisms, this phenomenological dynamic model (with an hourly time step) simulates spike mechanics: pistillody wetting/drying inertia, winter weathering and weakening of achene pedicel bonds, and aerodynamic wind stripping.
          </p>

          <div class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200/90 text-xs">
            <strong class="text-amber-300 font-semibold">Important methodological note:</strong> 
            The structural equations are strictly grounded in physical experiments (<em>Yeo, 1964; Krattinger, 1975; Lozada-Gobilard et al., 2021</em>), while rate coefficients (<em>k</em><sub>base</sub>, RH<sub>crit</sub> threshold shift) represent calibrational parameters that can be further refined via laboratory wind tunnel assays or iNaturalist image archives.
          </div>

          <div class="space-y-4">
            <h4 class="font-bold text-white text-sm border-b border-slate-700 pb-1">
              1. Mathematical Formulation
            </h4>
            <p>
              The model tracks spike state variables from the onset of seed maturation (<em>t</em><sub>0</sub>, mid-August in northern temperate latitudes; mid-February in the Southern Hemisphere):
            </p>
            <ul class="list-disc list-inside space-y-1 pl-2 text-slate-300">
              <li><span class="font-mono text-emerald-400 font-semibold">S(t) ∈ [0, 1]</span> — fraction of seeds retained on the spike axis (starts at <em>S</em>(0) = 1.0).</li>
              <li><span class="font-mono text-amber-300 font-semibold">F(t) ∈ [0, 1]</span> — fraction of intact (unopened) spikes in the population (starts at <em>F</em>(0) = 1.0).</li>
              <li><span class="font-mono text-purple-400 font-semibold">W(t) ∈ [0, 1]</span> — structural weathering index of the spike (weakening of pedicel attachment; starts at <em>W</em>(0) = 0.05 for fresh spikes).</li>
            </ul>
            <p>
              At each hourly step Δ<em>t</em> = 1 h, four processes are evaluated:
            </p>
          </div>

          <!-- Section A -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">A. Dynamic Asymmetric Moisture Inertia (RH<sub>tissue</sub>)</h5>
            <p>
              Pistillodies swell rapidly during dew or rain (τ<sub>wet</sub> ≈ 0.4 h), whereas core desiccation proceeds slower (τ<sub>dry0</sub> ≈ 3.5 h in still cold air) and accelerates under warmer temperatures and wind ventilation:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-amber-200 overflow-x-auto">
              f<sub>T</sub>(T) = 0.6 + 0.8 · ((clamp(T, -15, 30) + 15) / 45)<br>
              f<sub>U</sub>(U) = 1.0 + 0.15 · min(10, U)<br>
              τ<sub>dry</sub>(t) = 3.5 / (f<sub>T</sub>(T) · f<sub>U</sub>(U))<br>
              RH<sub>tissue</sub>(t) = 100%, &nbsp;&nbsp;if P(t) &gt; 0.1 mm<br>
              RH<sub>tissue</sub>(t) = RH<sub>tissue</sub>(t-1) + min(1, Δt / τ<sub>wet</sub>) · (RH(t) - RH<sub>tissue</sub>(t-1)), &nbsp;&nbsp;if RH(t) ≥ RH<sub>tissue</sub>(t-1)<br>
              RH<sub>tissue</sub>(t) = RH<sub>tissue</sub>(t-1) + min(1, Δt / τ<sub>dry</sub>) · (RH(t) - RH<sub>tissue</sub>(t-1)), &nbsp;&nbsp;if RH(t) &lt; RH<sub>tissue</sub>(t-1)
            </div>
          </div>

          <!-- Section B -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">B. Structural Weathering & Senescence Accumulation (W) and Maturation Gate M(W)</h5>
            <p>
              Thermal oscillations across 0 °C (freeze-thaw fatigue) and temperature-dependent autumnal tissue senescence weaken the mechanical cohesion of pedicels and pistillodia:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-purple-200 overflow-x-auto">
              ΔW(t) = w<sub>ft</sub> · 𝕀(T(t) · T(t-1) &lt; 0) + w<sub>age</sub>(T(t)) · Δt<br>
              w<sub>age</sub>(T) = 0.00035 h<sup>-1</sup> &nbsp;if T &lt; 11.0 °C (autumn cooling); &nbsp;0.00005 h<sup>-1</sup> &nbsp;if T ≥ 11.0 °C<br>
              M(W) = 1 / (1 + exp(-16.0 · (W - 0.22))) &nbsp;&nbsp;[sigmoidal maturation / brittleness barrier]
            </div>
            <p class="text-xs text-slate-400">
              where 𝕀 is the 0 °C zero-crossing indicator (<em>w</em><sub>ft</sub> = 0.018 per cycle). The sigmoidal gate <em>M</em>(<em>W</em>) suppresses premature fluffing in hot, dry August afternoons (<em>W</em> &lt; 0.15) and unlocks explosive opening in October as tissues undergo senescence (<em>W</em> &gt; 0.22).
            </p>
          </div>

          <!-- Section C -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">C. Hygroscopic Pistillody Valve (H) & Threshold Spike Opening (H<sub>fluff</sub>)</h5>
            <p>
              Critical opening thresholds shift upward as the spike weathers. Seed shedding (<em>H</em>) and outer spike cracking (<em>H</em><sub>fluff</sub>) follow separate physical pathways:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-sky-200 overflow-x-auto">
              RH<sub>crit</sub>(t) = 52 + 22 · W(t) &nbsp;&nbsp;[for seed shedding dS; 48 for angustifolia]<br>
              H(t) = max(0, &nbsp;(RH<sub>crit</sub>(t) - RH<sub>tissue</sub>(t)) / (RH<sub>crit</sub>(t) - 20))<br>
              RH<sub>fluff_crit</sub>(t) = 55 + 16 · W(t) &nbsp;&nbsp;[for spike fluffing dF; 51 for angustifolia]<br>
              x<sub>dry</sub>(t) = min(1.5, &nbsp;max(0, RH<sub>fluff_crit</sub>(t) - RH<sub>tissue</sub>(t)) / 20)<br>
              H<sub>fluff</sub>(t) = (x<sub>dry</sub>(t))<sup>2.1</sup> &nbsp;&nbsp;[nonlinear "popcorn" threshold]
            </div>
          </div>

          <!-- Section D -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">D. Aerodynamic Detachment, Seed Loss (ΔS) and Spike Fluffing (ΔF)</h5>
            <p>
              Seed shedding (Δ<em>S</em>) is governed by axis weathering <em>W</em> and wind above <em>U</em><sub>crit</sub> = 1.5 m/s. Outer spike fluffing (Δ<em>F</em>) is activated by autumnal senescence <em>M</em>(<em>W</em>) and surges nonlinearly during anticyclonic dry spells:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-blue-200 overflow-x-auto">
              A(t) = 1 - exp(-k<sub>u</sub> · max(0, U(t) - U<sub>crit</sub>))<br>
              ΔS(t) = -k<sub>base</sub> · (0.15 + 0.85 · W(t)) · H(t) · A(t) · S(t) · Δt<br>
              dryBoost(t) = 1 + 0.08 · max(0, RH<sub>tissue</sub>(t-1) - RH<sub>tissue</sub>(t))<br>
              ΔF(t) = -k<sub>fluff</sub> · M(W(t)) · H<sub>fluff</sub>(t) · dryBoost(t) · F(t) · Δt
            </div>
            <p class="text-xs text-slate-400">
              where <em>k</em><sub>u</sub> = 0.35, <em>k</em><sub>base</sub> = 0.015 (0.011 for <em>angustifolia</em>), <em>k</em><sub>fluff</sub> = 0.110 (0.070 for <em>angustifolia</em>). Unopened spike loss Δ<em>F</em>(<em>t</em>) is strictly gated by valve opening and ceases under humid conditions.
            </p>
          </div>

          <!-- Scientific References -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">2. Scientific References / Literature</h5>
            <ol class="list-decimal list-inside space-y-1.5 pl-2 text-xs text-slate-300">
              <li><strong class="text-white">Yeo, R. R. (1964)</strong>. <em>Life history of common cattail</em>. Weed Science, 12(4), 284–288.</li>
              <li><strong class="text-white">Krattinger, K. (1975)</strong>. <em>Genetic mobility in Typha</em>. New Phytologist, 74(2), 333–340.</li>
              <li><strong class="text-white">Lozada-Gobilard, S., Stang, M., & Tielbörger, K. (2021)</strong>. <em>Dispersal syndromes and the role of humidity in wind-dispersed plants: hygroscopic seed release</em>. Perspectives in Plant Ecology, Evolution and Systematics, 53, 125642.</li>
              <li><strong class="text-white">Schwendener, S. (1896)</strong>. <em>Die Spaltöffnungen der Typha-Arten und die hygroskopischen Bewegungen der Pistillodien</em>. Sitzungsberichte der Königlich Preussischen Akademie der Wissenschaften zu Berlin.</li>
            </ol>
          </div>
        </div>

        <!-- Russian Mathematical Model Container -->
        <div id="model-desc-ru" class="hidden p-5 md:p-6 border-t border-slate-700/80 bg-slate-900/60 space-y-5 text-xs md:text-sm text-slate-300 leading-relaxed font-sans">
          <p>
            На основе описанных биофизических механизмов построена феноменологическая динамическая модель (с часовым шагом по времени), имитирующая физику початка: инерцию увлажнения/высыхания пистиллодиев, ослабление крепления плодиков за зиму и аэродинамический срыв ветром.
          </p>

          <div class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200/90 text-xs">
            <strong class="text-amber-300 font-semibold">Важное методологическое примечание:</strong> 
            Сама структура уравнений строго опирается на физику процесса (работы <em>Yeo, 1964; Krattinger, 1975; Lozada-Gobilard et al., 2021</em>), но численные коэффициенты скорости (<em>k</em><sub>base</sub>, сдвиг порога RH<sub>crit</sub>) являются калибровочными — их можно уточнить по результатам лабораторного опыта или фотоархива iNaturalist.
          </div>

          <div class="space-y-4">
            <h4 class="font-bold text-white text-sm border-b border-slate-700 pb-1">
              1. Математическая формулировка модели
            </h4>
            <p>
              Модель отслеживает состояния початка с момента созревания семян (<em>t</em><sub>0</sub>, для средних широт Северного полушария — середина августа; для Южного полушария — середина февраля):
            </p>
            <ul class="list-disc list-inside space-y-1 pl-2 text-slate-300">
              <li><span class="font-mono text-emerald-400 font-semibold">S(t) ∈ [0, 1]</span> — доля семян, оставшихся в початке (в начале сезона <em>S</em>(0) = 1,0).</li>
              <li><span class="font-mono text-amber-300 font-semibold">F(t) ∈ [0, 1]</span> — доля нераспущённых (целых) початков в популяции (в начале сезона <em>F</em>(0) = 1,0).</li>
              <li><span class="font-mono text-purple-400 font-semibold">W(t) ∈ [0, 1]</span> — индекс структурного выветривания початка (ослабление связи плодиков с осью; стартует с <em>W</em>(0) = 0,05 для свежих початков).</li>
            </ul>
            <p>
              На каждом часовом шаге Δ<em>t</em> = 1 ч рассчитываются четыре процесса:
            </p>
          </div>

          <!-- Section A -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">А. Динамическая асимметричная инерция влажности тканей (RH<sub>tissue</sub>)</h5>
            <p>
              Пистиллодии набухают при росе или дожде очень быстро (τ<sub>wet</sub> ≈ 0,4 ч), в то время как отдача влаги плотной сердцевиной идёт значительно медленнее (τ<sub>dry0</sub> ≈ 3,5 ч в штиль на холоде) и ускоряется при повышенной температуре и ветре:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-amber-200 overflow-x-auto">
              f<sub>T</sub>(T) = 0.6 + 0.8 · ((clamp(T, -15, 30) + 15) / 45)<br>
              f<sub>U</sub>(U) = 1.0 + 0.15 · min(10, U)<br>
              τ<sub>dry</sub>(t) = 3.5 / (f<sub>T</sub>(T) · f<sub>U</sub>(U))<br>
              RH<sub>tissue</sub>(t) = 100%, &nbsp;&nbsp;если P(t) &gt; 0.1 мм<br>
              RH<sub>tissue</sub>(t) = RH<sub>tissue</sub>(t-1) + min(1, Δt / τ<sub>wet</sub>) · (RH(t) - RH<sub>tissue</sub>(t-1)), &nbsp;&nbsp;если RH(t) ≥ RH<sub>tissue</sub>(t-1)<br>
              RH<sub>tissue</sub>(t) = RH<sub>tissue</sub>(t-1) + min(1, Δt / τ<sub>dry</sub>) · (RH(t) - RH<sub>tissue</sub>(t-1)), &nbsp;&nbsp;если RH(t) &lt; RH<sub>tissue</sub>(t-1)
            </div>
          </div>

          <!-- Section B -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">Б. Накопление выветривания и старения (W) и сигмоидный барьер созревания M(W)</h5>
            <p>
              Переходы температуры через 0 °C (циклы «замерзание — оттаивание») и сезонное осеннее старение разрушают механическую связь плодиков с осью:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-purple-200 overflow-x-auto">
              ΔW(t) = w<sub>ft</sub> · 𝕀(T(t) · T(t-1) &lt; 0) + w<sub>age</sub>(T(t)) · Δt<br>
              w<sub>age</sub>(T) = 0.00035 ч<sup>-1</sup> &nbsp;если T &lt; 11.0 °C (осеннее похолодание); &nbsp;0.00005 ч<sup>-1</sup> &nbsp;если T ≥ 11.0 °C<br>
              M(W) = 1 / (1 + exp(-16.0 · (W - 0.22))) &nbsp;&nbsp;[сигмоидный фактор физиологической зрелости / охрупчивания]
            </div>
            <p class="text-xs text-slate-400">
              где 𝕀 — индикатор перехода через 0 °C (<em>w</em><sub>ft</sub> = 0,018 за цикл). Сигмоида <em>M</em>(<em>W</em>) надёжно блокирует раскрытие початков при летней жаре и низкой влажности августа (<em>W</em> &lt; 0,15) и активируется по мере осеннего старения тканей (<em>W</em> &gt; 0,22).
            </p>
          </div>

          <!-- Section C -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">В. Гигроскопический замок (H) и пороговое вскрытие оболочки (H<sub>fluff</sub>)</h5>
            <p>
              Пороги вскрытия разделены по физическим механизмам: сход семян (<em>H</em>) сдерживается плотным креплением плодиков к оси, тогда как визуальное растрескивание оболочки (<em>H</em><sub>fluff</sub>) подчиняется нелинейному пороговому «эффекту попкорна»:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-sky-200 overflow-x-auto">
              RH<sub>crit</sub>(t) = 52 + 22 · W(t) &nbsp;&nbsp;[для схода семян dS; 48 для angustifolia]<br>
              H(t) = max(0, &nbsp;(RH<sub>crit</sub>(t) - RH<sub>tissue</sub>(t)) / (RH<sub>crit</sub>(t) - 20))<br>
              RH<sub>fluff_crit</sub>(t) = 55 + 16 · W(t) &nbsp;&nbsp;[для распушения початков dF; 51 для angustifolia]<br>
              x<sub>dry</sub>(t) = min(1.5, &nbsp;max(0, RH<sub>fluff_crit</sub>(t) - RH<sub>tissue</sub>(t)) / 20)<br>
              H<sub>fluff</sub>(t) = (x<sub>dry</sub>(t))<sup>2.1</sup> &nbsp;&nbsp;[нелинейный степенной порог]
            </div>
          </div>

          <!-- Section D -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">Г. Ветровой срыв, убыль семян (ΔS) и распушение початков (ΔF)</h5>
            <p>
              Унос семян (Δ<em>S</em>) требует выветривания оси <em>W</em> и ветра выше <em>U</em><sub>crit</sub> = 1,5 м/с. Визуальное распушение (Δ<em>F</em>) активируется осенним созреванием <em>M</em>(<em>W</em>) и лавинообразно нарастает в периоды сухих антициклонов:
            </p>
            <div class="p-2.5 bg-slate-950 rounded-lg font-mono text-xs text-blue-200 overflow-x-auto">
              A(t) = 1 - exp(-k<sub>u</sub> · max(0, U(t) - U<sub>crit</sub>))<br>
              ΔS(t) = -k<sub>base</sub> · (0.15 + 0.85 · W(t)) · H(t) · A(t) · S(t) · Δt<br>
              dryBoost(t) = 1 + 0.08 · max(0, RH<sub>tissue</sub>(t-1) - RH<sub>tissue</sub>(t))<br>
              ΔF(t) = -k<sub>fluff</sub> · M(W(t)) · H<sub>fluff</sub>(t) · dryBoost(t) · F(t) · Δt
            </div>
            <p class="text-xs text-slate-400">
              где <em>k</em><sub>u</sub> = 0,35, <em>k</em><sub>base</sub> = 0,015 (0,011 для <em>angustifolia</em>), <em>k</em><sub>fluff</sub> = 0,110 (0,070 для <em>angustifolia</em>). Убыль нераспущённых початков Δ<em>F</em>(<em>t</em>) строго привязана к открытию замка и прекращается при сырости.
            </p>
          </div>

          <!-- Научные публикации -->
          <div class="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80 space-y-2">
            <h5 class="font-bold text-amber-300 text-xs md:text-sm">2. Научные публикации и литература</h5>
            <ol class="list-decimal list-inside space-y-1.5 pl-2 text-xs text-slate-300">
              <li><strong class="text-white">Yeo, R. R. (1964)</strong>. <em>Life history of common cattail</em>. Weed Science, 12(4), 284–288.</li>
              <li><strong class="text-white">Krattinger, K. (1975)</strong>. <em>Genetic mobility in Typha</em>. New Phytologist, 74(2), 333–340.</li>
              <li><strong class="text-white">Lozada-Gobilard, S., Stang, M., & Tielbörger, K. (2021)</strong>. <em>Dispersal syndromes and the role of humidity in wind-dispersed plants: hygroscopic seed release</em>. Perspectives in Plant Ecology, Evolution and Systematics, 53, 125642.</li>
              <li><strong class="text-white">Schwendener, S. (1896)</strong>. <em>Die Spaltöffnungen der Typha-Arten und die hygroskopischen Bewegungen der Pistillodien</em>. Sitzungsberichte der Königlich Preussischen Akademie der Wissenschaften zu Berlin.</li>
            </ol>
          </div>
        </div>
        </div>
      </details>
    </section>

  </div>

  <script>
    // ----------------------------------------------------
    // Internationalization (i18n) Data & Logic
    // Default language: English ('en')
    // ----------------------------------------------------
    let currentLang = 'en';

    const I18N = {{
      en: {{
        appTitle: "Typha Dispersal Simulator",
        appSubtitle: "Biomechanical simulation of cattail (<em>Typha</em> spp.) seed dispersal based on ERA5 climate reanalysis",
        step1Badge: "📍 Step 1:",
        step1Text: "Click anywhere on the world map to select coordinates",
        presetsLabel: "Presets:",
        pMoscow: "Moscow (SW)",
        pShatura: "Shatura (East)",
        pSerpukhov: "Serpukhov (South)",
        pDmitrov: "Dmitrov (North)",
        pSpb: "St. Petersburg",
        pNovosibirsk: "Novosibirsk",
        pSochi: "Sochi",
        pLondon: "London",
        pNewYork: "New York",
        pTokyo: "Tokyo",
        pMelbourne: "Melbourne (South)",
        pCapeTown: "Cape Town (South)",
        equator: "0° Equator",
        greenwich: "0° Greenwich",
        labelLat: "Latitude (-90..90)",
        labelLon: "Longitude (-180..180)",
        labelSpecies: "Typha Species",
        optLatifolia: "Typha latifolia (broadleaf cattail)",
        optAngustifolia: "Typha angustifolia (narrowleaf cattail)",
        labelSeason: "Ripening Season",
        seasonFormat: (y) => `Season ${{y}}–${{y + 1}}`,
        btnRun: "Run Simulation",
        btnRunning: "Simulating...",
        hemisphereNorth: "Northern Hemisphere (Aug – May)",
        hemisphereSouth: "Southern Hemisphere (Feb – Nov)",
        metricPeakFluff: "Peak Fluffing",
        metricPeakFluffSub: "Max monthly spike opening",
        metricUnfluffed: "Intact Spikes",
        metricUnfluffedSub: "Remaining unopened F(t)",
        metricDispersed: "Season Seed Shedding",
        metricDispersedSub: "Physical seed loss dS",
        metricRemaining: "Remaining Seeds S(t)",
        metricRemainingSub: "Seed mass on spike axis",
        metricWeathering: "Weathering Index W",
        metricWeatheringSub: "Axis degradation [0..1]",
        chart1Title: "1. Dynamics of Spike Fluffing, Seed Dispersal & Retention Curves",
        chart1Sub: "Bars: monthly spikes fluffed (amber) and physical seed loss dS (blue). Lines: remaining seed mass S(t) (green) and intact spikes F(t) (amber dashed).",
        legFluffed: "Fluffed dF (%)",
        legDispersed: "Seed Shedding dS (%)",
        legRemSeeds: "Seeds S(t) (%)",
        legUnfluffed: "Intact F(t) (%)",
        chart1YLeft: "Monthly Rates (%)",
        chart1YRight: "Remaining Retentions (%)",
        chart2Title: "2. Cumulative Seed Shedding & Axis Weathering Index W",
        chart2Sub: "Grey bars: cumulative percentage of shed seeds. Purple line: structural weathering index W [0..1].",
        legCum: "Cumulative (%)",
        legW: "Weathering W",
        chart2YLeft: "Cumulative Shedding (%)",
        chart2YRight: "Weathering Index W",
        tableTitle: "3. Summary of Biomechanical Simulation",
        tableSub: "Differential simulation step: 1 hour",
        thMonth: "Month",
        thFluffed: "Fluffed dF, %",
        thUnfluffed: "Intact F, %",
        thDispersed: "Seed Loss dS, %",
        thCumulative: "Cumulative, %",
        thRemaining: "Remaining Seeds S(t), %",
        thWeathering: "Index W",
        thStatus: "Spike Status",
        statusActiveFluff: "Active fluffing",
        statusMassDispersal: "Mass seed shedding",
        statusMoistureLock: "Humidity lock (valve closed)",
        statusSpringOpening: "Spring spike opening",
        statusAutumnRipening: "Autumn ripening",
        accordionTitle: "Mathematical Model Formulation of Cattail Spikes (<em>Typha</em> spp.)",
        accExpand: "Expand equations",
        accCollapse: "Collapse",
        loadingMsg: (species, lat, lon) => `⏳ Loading hourly ERA5 weather data for ${{species}} [${{lat}}, ${{lon}}]...`,
        successMsg: (count, species) => `✅ Simulation completed successfully! Calculated ${{count}} months for ${{species}}.`,
        errNaN: "⚠️ Please enter valid numeric coordinates for latitude and longitude, or click on the map.",
        errRange: "⚠️ Coordinates out of bounds: latitude [-90..90], longitude [-180..180]."
      }},
      ru: {{
        appTitle: "Typha Dispersal Simulator",
        appSubtitle: "Моделирование динамики облетания рогоза (<em>Typha</em> spp.) по климатическим данным ERA5",
        step1Badge: "📍 Шаг 1:",
        step1Text: "Кликните мышью по карте мира для выбора точки",
        presetsLabel: "Быстрый выбор:",
        pMoscow: "Москва (ЮЗАО)",
        pShatura: "Шатура (Восток)",
        pSerpukhov: "Серпухов (Юг)",
        pDmitrov: "Дмитров (Север)",
        pSpb: "СПб",
        pNovosibirsk: "Новосибирск",
        pSochi: "Сочи",
        pLondon: "Лондон",
        pNewYork: "Нью-Йорк",
        pTokyo: "Токио",
        pMelbourne: "Мельбурн (Юг)",
        pCapeTown: "Кейптаун (Юг)",
        equator: "0° Экватор",
        greenwich: "0° Гринвич",
        labelLat: "Широта (Latitude, -90..90)",
        labelLon: "Долгота (Longitude, -180..180)",
        labelSpecies: "Вид рогоза",
        optLatifolia: "Typha latifolia (широколистный)",
        optAngustifolia: "Typha angustifolia (узколистный)",
        labelSeason: "Сезон созревания",
        seasonFormat: (y) => `Сезон ${{y}}–${{y + 1}} гг.`,
        btnRun: "Запустить симуляцию",
        btnRunning: "Симуляция...",
        hemisphereNorth: "Северное полушарие (авг — май)",
        hemisphereSouth: "Южное полушарие (фев — ноя)",
        metricPeakFluff: "Пик распушения",
        metricPeakFluffSub: "Максимальный сброс початков",
        metricUnfluffed: "Нераспущённых початков",
        metricUnfluffedSub: "Остаток целых початков F(t)",
        metricDispersed: "Сброс семян за сезон",
        metricDispersedSub: "Физическая убыль dS",
        metricRemaining: "Остаток семян S(t)",
        metricRemainingSub: "Масса семян на оси",
        metricWeathering: "Индекс выветривания W",
        metricWeatheringSub: "Деградация оси [0..1]",
        chart1Title: "1. Динамика распушения початков, схода семян и кривые остатков",
        chart1Sub: "Столбики: распушилось початков за месяц (желтый) и физический сход семян dS (синий). Линии: остаток семян S(t) (зеленая) и доля целых початков F(t) (янтарная пунктирная).",
        legFluffed: "Распушилось dF (%)",
        legDispersed: "Сход семян dS (%)",
        legRemSeeds: "Остаток семян S(t) (%)",
        legUnfluffed: "Нераспущённых F(t) (%)",
        chart1YLeft: "Показатели месяца (%)",
        chart1YRight: "Кривые остатка (%)",
        chart2Title: "2. Кумулятивный сброс семян и выветривание оси соцветия W",
        chart2Sub: "Серые столбики: накопленный процент осыпавшихся плодиков. Фиолетовая линия: индекс выветривания W [0..1].",
        legCum: "Накоплено (%)",
        legW: "Индекс W",
        chart2YLeft: "Кумулятивный сброс (%)",
        chart2YRight: "Индекс выветривания W",
        tableTitle: "3. Сводные результаты биомеханического моделирования",
        tableSub: "Шаг дифференциального моделирования: 1 час",
        thMonth: "Месяц",
        thFluffed: "Распушилось dF, %",
        thUnfluffed: "Нераспущённых F, %",
        thDispersed: "Физический сход dS, %",
        thCumulative: "Кумулятивно, %",
        thRemaining: "Остаток семян S(t), %",
        thWeathering: "Индекс W",
        thStatus: "Статус соцветия",
        statusActiveFluff: "Активное распушение",
        statusMassDispersal: "Массовый сход семян",
        statusMoistureLock: "Блокировка сыростью (замок закрыт)",
        statusSpringOpening: "Весеннее раскрытие соцветий",
        statusAutumnRipening: "Осеннее созревание",
        accordionTitle: "Описание математической модели початков рогоза (<em>Typha</em> spp.)",
        accExpand: "Развернуть формулы",
        accCollapse: "Свернуть",
        loadingMsg: (species, lat, lon) => `⏳ Загрузка метеоданных для ${{species}} [${{lat}}, ${{lon}}]...`,
        successMsg: (count, species) => `✅ Симуляция успешно выполнена! Рассчитано ${{count}} месяцев для ${{species}}.`,
        errNaN: "⚠️ Пожалуйста, введите корректные числовые координаты широты и долготы или кликните по карте.",
        errRange: "⚠️ Координаты выходят за допустимые пределы: широта [-90..90], долгота [-180..180]."
      }}
    }};

    // State preservation for instant re-translation
    let lastResults = null;
    let lastLat = 55.65;
    let lastLon = 37.50;
    let lastSeasonYear = 2026;
    let lastSpecies = 'latifolia';

    function setLanguage(lang) {{
      currentLang = lang;
      const dict = I18N[lang];

      // Update toggle buttons
      const btnEn = document.getElementById('lang-btn-en');
      const btnRu = document.getElementById('lang-btn-ru');
      if (lang === 'en') {{
        btnEn.className = "px-3 py-1 text-xs font-bold rounded-lg transition bg-amber-500 text-slate-950 shadow-sm";
        btnRu.className = "px-3 py-1 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white";
        document.documentElement.lang = "en";
      }} else {{
        btnRu.className = "px-3 py-1 text-xs font-bold rounded-lg transition bg-amber-500 text-slate-950 shadow-sm";
        btnEn.className = "px-3 py-1 text-xs font-bold rounded-lg transition text-slate-400 hover:text-white";
        document.documentElement.lang = "ru";
      }}

      // Header & Steps
      document.getElementById('t-app-title').innerHTML = dict.appTitle;
      document.getElementById('t-app-subtitle').innerHTML = dict.appSubtitle;
      document.getElementById('t-step1-badge').textContent = dict.step1Badge;
      document.getElementById('t-step1-text').textContent = dict.step1Text;
      document.getElementById('t-presets-label').textContent = dict.presetsLabel;

      // Presets
      document.getElementById('p-moscow').textContent = dict.pMoscow;
      document.getElementById('p-shatura').textContent = dict.pShatura;
      document.getElementById('p-serpukhov').textContent = dict.pSerpukhov;
      document.getElementById('p-dmitrov').textContent = dict.pDmitrov;
      document.getElementById('p-spb').textContent = dict.pSpb;
      document.getElementById('p-novosibirsk').textContent = dict.pNovosibirsk;
      document.getElementById('p-sochi').textContent = dict.pSochi;
      document.getElementById('p-london').textContent = dict.pLondon;
      document.getElementById('p-newyork').textContent = dict.pNewYork;
      document.getElementById('p-tokyo').textContent = dict.pTokyo;
      document.getElementById('p-melbourne').textContent = dict.pMelbourne;
      document.getElementById('p-capetown').textContent = dict.pCapeTown;

      // Map Labels
      document.getElementById('map-label-equator').textContent = dict.equator;
      document.getElementById('map-label-greenwich').textContent = dict.greenwich;

      // Form Controls
      document.getElementById('t-label-lat').textContent = dict.labelLat;
      document.getElementById('t-label-lon').textContent = dict.labelLon;
      document.getElementById('t-label-species').textContent = dict.labelSpecies;

      const spSelect = document.getElementById('species-select');
      const curSpeciesVal = spSelect.value;
      spSelect.options[0].text = dict.optLatifolia;
      spSelect.options[1].text = dict.optAngustifolia;
      spSelect.value = curSpeciesVal;

      document.getElementById('t-label-season').textContent = dict.labelSeason;
      document.getElementById('btn-text').textContent = dict.btnRun;

      // Refresh season options preserving selected year
      const seasonSelect = document.getElementById('season-select');
      const curSeasonVal = seasonSelect.value;
      Array.from(seasonSelect.options).forEach(opt => {{
        const y = parseInt(opt.value);
        opt.textContent = dict.seasonFormat(y);
      }});
      seasonSelect.value = curSeasonVal;

      // Metrics Labels
      document.getElementById('t-metric-fluff-label').textContent = dict.metricPeakFluff;
      document.getElementById('t-metric-fluff-sub').textContent = dict.metricPeakFluffSub;
      document.getElementById('t-metric-unfluffed-label').textContent = dict.metricUnfluffed;
      document.getElementById('t-metric-unfluffed-sub').textContent = dict.metricUnfluffedSub;
      document.getElementById('t-metric-dispersed-label').textContent = dict.metricDispersed;
      document.getElementById('t-metric-dispersed-sub').textContent = dict.metricDispersedSub;
      document.getElementById('t-metric-remaining-label').textContent = dict.metricRemaining;
      document.getElementById('t-metric-remaining-sub').textContent = dict.metricRemainingSub;
      document.getElementById('t-metric-weathering-label').textContent = dict.metricWeathering;
      document.getElementById('t-metric-weathering-sub').textContent = dict.metricWeatheringSub;

      // Chart 1 Text
      document.getElementById('t-chart1-title').textContent = dict.chart1Title;
      document.getElementById('t-chart1-sub').textContent = dict.chart1Sub;
      document.getElementById('t-leg-fluffed').textContent = dict.legFluffed;
      document.getElementById('t-leg-dispersed').textContent = dict.legDispersed;
      document.getElementById('t-leg-rem-seeds').textContent = dict.legRemSeeds;
      document.getElementById('t-leg-unfluffed').textContent = dict.legUnfluffed;

      // Chart 2 Text
      document.getElementById('t-chart2-title').textContent = dict.chart2Title;
      document.getElementById('t-chart2-sub').textContent = dict.chart2Sub;
      document.getElementById('t-leg-cum').textContent = dict.legCum;
      document.getElementById('t-leg-w').textContent = dict.legW;

      // Table Headers
      document.getElementById('t-table-title').textContent = dict.tableTitle;
      document.getElementById('t-table-sub').textContent = dict.tableSub;
      document.getElementById('th-month').textContent = dict.thMonth;
      document.getElementById('th-fluffed').textContent = dict.thFluffed;
      document.getElementById('th-unfluffed').textContent = dict.thUnfluffed;
      document.getElementById('th-dispersed').textContent = dict.thDispersed;
      document.getElementById('th-cumulative').textContent = dict.thCumulative;
      document.getElementById('th-remaining').textContent = dict.thRemaining;
      document.getElementById('th-weathering').textContent = dict.thWeathering;
      document.getElementById('th-status').textContent = dict.thStatus;

      // Accordion Description
      document.getElementById('t-accordion-title').innerHTML = dict.accordionTitle;
      document.getElementById('t-acc-expand').textContent = dict.accExpand;
      document.getElementById('t-acc-collapse').textContent = dict.accCollapse;

      const descEn = document.getElementById('model-desc-en');
      const descRu = document.getElementById('model-desc-ru');
      if (lang === 'en') {{
        descEn.classList.remove('hidden');
        descRu.classList.add('hidden');
      }} else {{
        descEn.classList.add('hidden');
        descRu.classList.remove('hidden');
      }}

      // Update Hemisphere Badge with current lat
      const latVal = parseFloat(latInput.value);
      if (!isNaN(latVal)) {{
        updateHemisphereBadge(latVal);
      }}

      // If results already exist, re-render charts & table with new localized labels
      if (lastResults) {{
        renderResults(lastResults, lastLat, lastLon, lastSeasonYear, lastSpecies);
      }}
    }}

    // ----------------------------------------------------
    // Map Interaction
    // ----------------------------------------------------
    const mapBox = document.getElementById('map-box');
    const pinMarker = document.getElementById('pin-marker');
    const hoverTip = document.getElementById('hover-tip');
    const latInput = document.getElementById('lat-input');
    const lonInput = document.getElementById('lon-input');
    const hemisphereBadge = document.getElementById('hemisphere-badge');

    let chartDispersalInstance = null;
    let chartWeatheringInstance = null;

    function coordsToPercent(lat, lon) {{
      const x = ((lon + 180.0) / 360.0) * 100.0;
      const y = ((90.0 - lat) / 180.0) * 100.0;
      return {{ x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) }};
    }}

    function pointToCoords(e) {{
      const rect = mapBox.getBoundingClientRect();
      const xClamped = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
      const yClamped = Math.max(0, Math.min(rect.height, e.clientY - rect.top));

      const xNorm = xClamped / rect.width;
      const yNorm = yClamped / rect.height;

      const lon = xNorm * 360.0 - 180.0;
      const lat = 90.0 - yNorm * 180.0;

      return {{
        lat: parseFloat(lat.toFixed(4)),
        lon: parseFloat(lon.toFixed(4))
      }};
    }}

    function updatePin(lat, lon) {{
      const p = coordsToPercent(lat, lon);
      pinMarker.style.left = `${{p.x}}%`;
      pinMarker.style.top = `${{p.y}}%`;
      updateHemisphereBadge(lat);
    }}

    function updateHemisphereBadge(lat) {{
      const dict = I18N[currentLang];
      if (lat < 0) {{
        hemisphereBadge.textContent = dict.hemisphereSouth;
        hemisphereBadge.className = "text-xs px-3 py-1.5 rounded-lg bg-sky-950 border border-sky-700 text-sky-300";
      }} else {{
        hemisphereBadge.textContent = dict.hemisphereNorth;
        hemisphereBadge.className = "text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300";
      }}
    }}

    function setCoords(lat, lon) {{
      lat = parseFloat(lat.toFixed(4));
      lon = parseFloat(lon.toFixed(4));
      latInput.value = lat;
      lonInput.value = lon;
      updatePin(lat, lon);
    }}

    mapBox.addEventListener('click', function(e) {{
      const c = pointToCoords(e);
      setCoords(c.lat, c.lon);
    }});

    mapBox.addEventListener('mousemove', function(e) {{
      const c = pointToCoords(e);
      const latLabel = c.lat >= 0 ? `${{c.lat}}° N` : `${{Math.abs(c.lat)}}° S`;
      const lonLabel = c.lon >= 0 ? `${{c.lon}}° E` : `${{Math.abs(c.lon)}}° W`;

      hoverTip.style.display = 'block';
      const rect = mapBox.getBoundingClientRect();
      hoverTip.style.left = `${{e.clientX - rect.left}}px`;
      hoverTip.style.top = `${{e.clientY - rect.top}}px`;
      hoverTip.textContent = `${{latLabel}}, ${{lonLabel}}`;
    }});

    mapBox.addEventListener('mouseleave', function() {{
      hoverTip.style.display = 'none';
    }});

    latInput.addEventListener('input', syncPinFromInputs);
    lonInput.addEventListener('input', syncPinFromInputs);

    function syncPinFromInputs() {{
      const lat = parseFloat(latInput.value);
      const lon = parseFloat(lonInput.value);
      if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {{
        updatePin(lat, lon);
      }}
    }}

    function populateSeasons() {{
      const seasonSelect = document.getElementById('season-select');
      seasonSelect.innerHTML = '';
      const now = new Date();
      const currentYear = now.getFullYear();
      
      const aug15 = new Date(`${{currentYear}}-08-15`);
      const defaultYear = (now < aug15) ? currentYear - 1 : currentYear;

      for (let y = currentYear; y >= 1950; y--) {{
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = I18N[currentLang].seasonFormat(y);
        if (y === defaultYear) opt.selected = true;
        seasonSelect.appendChild(opt);
      }}
    }}

    // ----------------------------------------------------
    // Fetch Hourly Data & Run Simulation
    // ----------------------------------------------------
    async function runSimulation() {{
      const dict = I18N[currentLang];
      const statusBar = document.getElementById('status-bar');
      const calcBtn = document.getElementById('calc-btn');
      const btnText = document.getElementById('btn-text');
      const btnIcon = document.getElementById('btn-icon');

      const lat = parseFloat(latInput.value);
      const lon = parseFloat(lonInput.value);

      if (isNaN(lat) || isNaN(lon)) {{
        statusBar.className = "p-3 rounded-xl text-xs flex items-center gap-2 bg-rose-500/10 text-rose-400 border border-rose-500/20";
        statusBar.innerHTML = `<span>${{dict.errNaN}}</span>`;
        statusBar.classList.remove('hidden');
        return;
      }}

      if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {{
        statusBar.className = "p-3 rounded-xl text-xs flex items-center gap-2 bg-rose-500/10 text-rose-400 border border-rose-500/20";
        statusBar.innerHTML = `<span>${{dict.errRange}}</span>`;
        statusBar.classList.remove('hidden');
        return;
      }}

      let seasonYear = parseInt(document.getElementById('season-select').value);
      const species = document.getElementById('species-select').value;
      const speciesTitle = species === 'latifolia' ? 'Typha latifolia' : 'Typha angustifolia';

      statusBar.className = "p-3 rounded-xl text-xs flex items-center gap-2 bg-blue-500/10 text-blue-400 border border-blue-500/20";
      statusBar.innerHTML = `<span>${{dict.loadingMsg(speciesTitle, lat.toFixed(2), lon.toFixed(2))}}</span>`;
      statusBar.classList.remove('hidden');

      calcBtn.disabled = true;
      btnText.textContent = dict.btnRunning;
      btnIcon.textContent = "⏳";

      try {{
        const isSouthern = lat < 0.0;
        let startDate, nominalEnd;
        if (isSouthern) {{
          startDate = `${{seasonYear}}-02-15`;
          nominalEnd = `${{seasonYear}}-11-30`;
        }} else {{
          startDate = `${{seasonYear}}-08-15`;
          nominalEnd = `${{seasonYear + 1}}-05-31`;
        }}

        const now = new Date();
        while (new Date(startDate) > now) {{
          seasonYear = seasonYear - 1;
          document.getElementById('season-select').value = seasonYear;
          if (isSouthern) {{
            startDate = `${{seasonYear}}-02-15`;
            nominalEnd = `${{seasonYear}}-11-30`;
          }} else {{
            startDate = `${{seasonYear}}-08-15`;
            nominalEnd = `${{seasonYear + 1}}-05-31`;
          }}
        }}

        let endDate = nominalEnd;
        const plannedEnd = new Date(nominalEnd);
        if (plannedEnd > now) {{
          const cutoff = new Date(now.getTime() - 5 * 24 * 3600 * 1000);
          const m = String(cutoff.getMonth() + 1).padStart(2, '0');
          const d = String(cutoff.getDate()).padStart(2, '0');
          endDate = `${{cutoff.getFullYear()}}-${{m}}-${{d}}`;
        }}

        while (new Date(startDate) > new Date(endDate)) {{
          seasonYear = seasonYear - 1;
          document.getElementById('season-select').value = seasonYear;
          if (isSouthern) {{
            startDate = `${{seasonYear}}-02-15`;
            nominalEnd = `${{seasonYear}}-11-30`;
          }} else {{
            startDate = `${{seasonYear}}-08-15`;
            nominalEnd = `${{seasonYear + 1}}-05-31`;
          }}
          endDate = nominalEnd;
        }}

        const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${{lat}}&longitude=${{lon}}&start_date=${{startDate}}&end_date=${{endDate}}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&wind_speed_unit=ms&timezone=auto`;

        const resp = await fetch(url);
        if (!resp.ok) {{
          throw new Error(`Open-Meteo API Error: HTTP ${{resp.status}}`);
        }}
        const data = await resp.json();
        if (!data.hourly) {{
          throw new Error("Invalid response format from weather server.");
        }}

        const results = simulateTyphaDispersalJS(data.hourly, species);
        lastResults = results;
        lastLat = lat;
        lastLon = lon;
        lastSeasonYear = seasonYear;
        lastSpecies = species;

        renderResults(results, lat, lon, seasonYear, species);

        statusBar.className = "p-3 rounded-xl text-xs flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
        statusBar.innerHTML = `<span>${{dict.successMsg(results.length, speciesTitle)}}</span>`;
      }} catch (err) {{
        statusBar.className = "p-3 rounded-xl text-xs flex items-center gap-2 bg-rose-500/10 text-rose-400 border border-rose-500/20";
        statusBar.innerHTML = `<span>❌ ${{err.message}}</span>`;
      }} finally {{
        calcBtn.disabled = false;
        btnText.textContent = dict.btnRun;
        btnIcon.textContent = "⚡";
      }}
    }}

    // ----------------------------------------------------
    // Exact Biological Model with Unified Hourly dF & dS
    // ----------------------------------------------------
    function simulateTyphaDispersalJS(hourly, species) {{
      const times = hourly.time;
      const temps = hourly.temperature_2m;
      const rhs = hourly.relative_humidity_2m;
      const precips = hourly.precipitation;
      const winds = hourly.wind_speed_10m;

      // Калибровочные параметры вида
      const rhCritBase = species === 'angustifolia' ? 48.0 : 52.0; // порог высыпания семян dS
      const rhFluffBase = species === 'angustifolia' ? 51.0 : 55.0; // порог распушения оболочки dF
      const kBase = species === 'angustifolia' ? 0.011 : 0.015;
      const kFluff = species === 'angustifolia' ? 0.070 : 0.110;
      const gammaFluff = 2.1;

      let S = 1.0;
      let F = 1.0;
      let W = 0.05; // в середине августа початок ещё свежий, начальное выветривание минимально
      let rhTissue = 85.0;

      const tau = 1.5;
      const uCrit = 1.5;
      const kU = 0.35;

      const monthlyDispersed = {{}};
      const monthlyFluffed = {{}};
      const monthlyWeathering = {{}};
      const monthlyUnfluffed = {{}};

      let prevTemp = null;

      for (let i = 0; i < times.length; i++) {{
        if (temps[i] === null || rhs[i] === null) continue;

        const tCur = temps[i];
        const rhCur = rhs[i];
        const pCur = precips[i] !== null ? precips[i] : 0.0;
        const uCur = winds[i] !== null ? winds[i] : 0.0;

        // А. Асимметричная инерция увлажнения и высыхания пистиллодиев
        const rhPrev = rhTissue;
        if (pCur > 0.1) {{
          rhTissue = 100.0;
        }} else if (rhCur >= rhTissue) {{
          // Набухание пистиллодиев при росе/тумане (tauWet = 0.4 ч)
          const tauWet = 0.4;
          rhTissue += Math.min(1.0, 1.0 / tauWet) * (rhCur - rhTissue);
        }} else {{
          // Скорость высыхания зависит от температуры и ветра
          const tClamped = Math.max(-15.0, Math.min(30.0, tCur));
          const fTemp = 0.6 + 0.8 * ((tClamped + 15.0) / 45.0);
          const fWind = 1.0 + 0.15 * Math.min(10.0, uCur);
          const tauDry = 3.5 / (fTemp * fWind);
          rhTissue += Math.min(1.0, 1.0 / tauDry) * (rhCur - rhTissue);
        }}

        const dryingRate = Math.max(0.0, rhPrev - rhTissue);

        // Б. Накопление выветривания и осеннего старения тканей W
        let freezeThaw = 0.0;
        if (prevTemp !== null) {{
          if ((tCur < 0.0 && prevTemp >= 0.0) || (tCur >= 0.0 && prevTemp < 0.0)) {{
            freezeThaw = 0.018;
          }}
        }}
        prevTemp = tCur;
        // В тёплую погоду (T >= 11 °C) ткани стареют медленно; при осеннем похолодании — ускоренно
        const ageRate = tCur < 11.0 ? 0.00035 : 0.00005;
        W = Math.min(1.0, W + freezeThaw + ageRate);

        // Сигмоидный фактор физиологического созревания/охрупчивания початка M(W) ∈ [0..1]
        // Блокирует вскрытие в августе-сентябре (W < 0.15) и открывает его в октябре (W > 0.22)
        const M = 1.0 / (1.0 + Math.exp(-16.0 * (W - 0.22)));

        const rhCrit = rhCritBase + 22.0 * W;
        let H = 0.0;
        if (rhTissue < rhCrit) {{
          H = (rhCrit - rhTissue) / Math.max(1.0, (rhCrit - 20.0));
        }}

        let dS = 0.0;
        if (H > 0.0 && uCur > uCrit && S > 0.0) {{
          const A = 1.0 - Math.exp(-kU * (uCur - uCrit));
          dS = kBase * (0.15 + 0.85 * W) * H * A * S;
          dS = Math.min(S, dS);
          S -= dS;
        }}

        // Г2. Нелинейное пороговое распушение початков dF
        const rhFluffCrit = rhFluffBase + 16.0 * W;
        let dF = 0.0;
        if (rhTissue < rhFluffCrit && F > 0.0) {{
          const xDry = Math.min(1.5, (rhFluffCrit - rhTissue) / 20.0);
          const H_fluff = Math.pow(xDry, gammaFluff);
          const dryBoost = 1.0 + 0.08 * dryingRate;

          dF = kFluff * M * H_fluff * dryBoost * F;
          dF = Math.min(F, dF);
          F -= dF;
        }}

        const monthKey = times[i].substring(0, 7);
        if (!monthlyDispersed[monthKey]) {{
          monthlyDispersed[monthKey] = 0.0;
          monthlyFluffed[monthKey] = 0.0;
        }}
        monthlyDispersed[monthKey] += dS * 100.0;
        monthlyFluffed[monthKey] += dF * 100.0;
        monthlyWeathering[monthKey] = W;
        monthlyUnfluffed[monthKey] = F * 100.0;
      }}

      const results = [];
      let cumulative = 0.0;
      const sortedMonths = Object.keys(monthlyDispersed).sort();

      sortedMonths.forEach(m => {{
        const disp = monthlyDispersed[m];
        cumulative += disp;
        const fluffed = monthlyFluffed[m];
        const unfluffed = monthlyUnfluffed[m];
        const wVal = monthlyWeathering[m];
        const remaining = Math.max(0.0, 100.0 - cumulative);

        results.push({{
          month: m,
          fluffProbPct: parseFloat(fluffed.toFixed(1)),
          unfluffedPct: parseFloat(unfluffed.toFixed(1)),
          dispersedPct: parseFloat(disp.toFixed(1)),
          cumulativePct: parseFloat(Math.min(100.0, cumulative).toFixed(1)),
          remainingPct: parseFloat(remaining.toFixed(1)),
          weatheringIndex: parseFloat(wVal.toFixed(2))
        }});
      }});

      return results;
    }}

    // ----------------------------------------------------
    // Render Results & Localized Charts/Table
    // ----------------------------------------------------
    function renderResults(results, lat, lon, seasonYear, species) {{
      const dict = I18N[currentLang];
      const resultsSection = document.getElementById('results-section');
      resultsSection.classList.remove('hidden');

      if (!results || results.length === 0) return;

      const lastRow = results[results.length - 1];
      const totalDispersed = lastRow.cumulativePct;
      const finalRemaining = lastRow.remainingPct;
      const finalUnfluffed = lastRow.unfluffedPct;
      const finalWeathering = lastRow.weatheringIndex;

      let peakFluff = results[0];
      results.forEach(r => {{
        if (r.fluffProbPct > peakFluff.fluffProbPct) peakFluff = r;
      }});

      document.getElementById('metric-peak-fluff').textContent = `${{peakFluff.month}} (${{peakFluff.fluffProbPct}}%)`;
      document.getElementById('metric-unfluffed').textContent = `${{finalUnfluffed}}%`;
      document.getElementById('metric-total-dispersed').textContent = `${{totalDispersed}}%`;
      document.getElementById('metric-remaining').textContent = `${{finalRemaining}}%`;
      document.getElementById('metric-weathering').textContent = `${{finalWeathering}}`;

      const tbody = document.getElementById('table-body');
      tbody.innerHTML = '';
      results.forEach(r => {{
        let status = dict.statusAutumnRipening;
        if (r.fluffProbPct > 10.0) {{
          status = dict.statusActiveFluff;
        }} else if (r.dispersedPct > 15.0) {{
          status = dict.statusMassDispersal;
        }} else if (r.fluffProbPct === 0 && r.dispersedPct === 0) {{
          status = dict.statusMoistureLock;
        }} else if (r.weatheringIndex >= 0.7) {{
          status = dict.statusSpringOpening;
        }}

        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-800/50 transition";
        tr.innerHTML = `
          <td class="py-2 px-3 font-bold text-white">${{r.month}}</td>
          <td class="py-2 px-3 text-amber-400 font-bold">${{r.fluffProbPct}}%</td>
          <td class="py-2 px-3 text-amber-300 font-semibold">${{r.unfluffedPct}}%</td>
          <td class="py-2 px-3 text-blue-400 font-semibold">${{r.dispersedPct}}%</td>
          <td class="py-2 px-3 text-slate-300">${{r.cumulativePct}}%</td>
          <td class="py-2 px-3 text-emerald-400 font-bold">${{r.remainingPct}}%</td>
          <td class="py-2 px-3 text-purple-400">${{r.weatheringIndex}}</td>
          <td class="py-2 px-3 text-slate-400 font-sans">${{status}}</td>
        `;
        tbody.appendChild(tr);
      }});

      // Chart 1
      if (chartDispersalInstance) chartDispersalInstance.destroy();
      const ctx1 = document.getElementById('chart-dispersal').getContext('2d');
      chartDispersalInstance = new Chart(ctx1, {{
        data: {{
          labels: results.map(r => r.month),
          datasets: [
            {{
              type: 'line',
              label: dict.legRemSeeds,
              data: results.map(r => r.remainingPct),
              borderColor: '#10b981',
              backgroundColor: '#10b981',
              borderWidth: 2.8,
              pointRadius: 5,
              yAxisID: 'y1',
              tension: 0.2
            }},
            {{
              type: 'line',
              label: dict.legUnfluffed,
              data: results.map(r => r.unfluffedPct),
              borderColor: '#f59e0b',
              backgroundColor: '#f59e0b',
              borderDash: [5, 4],
              borderWidth: 2.4,
              pointRadius: 4,
              yAxisID: 'y1',
              tension: 0.2
            }},
            {{
              type: 'bar',
              label: dict.legFluffed,
              data: results.map(r => r.fluffProbPct),
              backgroundColor: '#f59e0b',
              borderRadius: 4,
              yAxisID: 'y'
            }},
            {{
              type: 'bar',
              label: dict.legDispersed,
              data: results.map(r => r.dispersedPct),
              backgroundColor: '#3b82f6',
              borderRadius: 4,
              yAxisID: 'y'
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'index', intersect: false }},
          scales: {{
            y: {{
              beginAtZero: true,
              max: 100,
              grid: {{ color: 'rgba(51, 65, 85, 0.4)' }},
              ticks: {{ color: '#cbd5e1' }},
              title: {{ display: true, text: dict.chart1YLeft, color: '#f59e0b' }}
            }},
            y1: {{
              beginAtZero: true,
              max: 105,
              position: 'right',
              grid: {{ drawOnChartArea: false }},
              ticks: {{ color: '#10b981' }},
              title: {{ display: true, text: dict.chart1YRight, color: '#10b981' }}
            }},
            x: {{
              grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
              ticks: {{ color: '#cbd5e1' }}
            }}
          }},
          plugins: {{
            legend: {{
              labels: {{ color: '#cbd5e1', font: {{ size: 11 }} }},
              position: 'top'
            }}
          }}
        }}
      }});

      // Chart 2
      if (chartWeatheringInstance) chartWeatheringInstance.destroy();
      const ctx2 = document.getElementById('chart-weathering').getContext('2d');
      chartWeatheringInstance = new Chart(ctx2, {{
        data: {{
          labels: results.map(r => r.month),
          datasets: [
            {{
              type: 'bar',
              label: dict.legCum,
              data: results.map(r => r.cumulativePct),
              backgroundColor: '#64748b',
              borderRadius: 4,
              yAxisID: 'y'
            }},
            {{
              type: 'line',
              label: dict.legW,
              data: results.map(r => r.weatheringIndex),
              borderColor: '#a855f7',
              backgroundColor: '#a855f7',
              borderDash: [5, 5],
              borderWidth: 2.5,
              tension: 0.2,
              yAxisID: 'y1'
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{ mode: 'index', intersect: false }},
          scales: {{
            y: {{
              beginAtZero: true,
              max: 100,
              grid: {{ color: 'rgba(51, 65, 85, 0.4)' }},
              ticks: {{ color: '#cbd5e1' }},
              title: {{ display: true, text: dict.chart2YLeft, color: '#cbd5e1' }}
            }},
            y1: {{
              beginAtZero: true,
              max: 1.1,
              position: 'right',
              grid: {{ drawOnChartArea: false }},
              ticks: {{ color: '#a855f7' }},
              title: {{ display: true, text: dict.chart2YRight, color: '#a855f7' }}
            }},
            x: {{
              grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
              ticks: {{ color: '#cbd5e1' }}
            }}
          }},
          plugins: {{
            legend: {{
              labels: {{ color: '#cbd5e1', font: {{ size: 11 }} }},
              position: 'top'
            }}
          }}
        }}
      }});
    }}

    // Initialize on load: Default English ('en')
    window.onload = function() {{
      setLanguage('en');
      populateSeasons();
      updatePin(55.65, 37.50);
      runSimulation();
    }};
  </script>
</body>
</html>
"""

with open("typha_map_app.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated bilingual typha_map_app.html: {{len(html_content)}} characters")
