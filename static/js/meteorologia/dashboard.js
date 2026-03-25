(function () {
  let rows = [], timerInterval = null, nextFetchIn = 0;
  const INTERVAL = 30 * 60 * 10000;

  // ── Helpers meteorológicos ────────────────────────────────────────────────

  function degToDir(deg) {
    const d = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSO','SO','OSO','O','ONO','NO','NNO'];
    return d[Math.round((deg || 0) / 22.5) % 16];
  }

  function dewPoint(t, h) {
    const a = 17.27, b = 237.7;
    const alpha = (a * t) / (b + t) + Math.log(h / 100);
    return +((b * alpha) / (a - alpha)).toFixed(1);
  }

  function heatIndex(t, h) {
    if (t < 27) return null;
    const c = [-8.78469475556, 1.61139411, 2.33854883889, -0.14611605, -0.012308094,
               -0.0164248277778, 0.002211732, 0.00072546, -0.000003582];
    const hi = c[0]+c[1]*t+c[2]*h+c[3]*t*h+c[4]*t*t+c[5]*h*h+c[6]*t*t*h+c[7]*t*h*h+c[8]*t*t*h*h;
    return +hi.toFixed(1);
  }

  function windChill(t, ws) {
    if (t > 10 || ws < 4.8) return null;
    return +(13.12 + 0.6215*t - 11.37*Math.pow(ws, 0.16) + 0.3965*t*Math.pow(ws, 0.16)).toFixed(1);
  }

  function fmtDate(ts) {
    return new Date(ts * 1000).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  function fmtTime(ts) {
    return new Date(ts * 1000).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
  }

  // ── UI helpers ────────────────────────────────────────────────────────────

  function setStatus(type, msg, extra) {
    const bar = document.getElementById('wx-status-bar');
    const colors = { ok: '#166534', error: '#7f1d1d', loading: '#1e3a5f' };
    const bgs    = { ok: '#052e16', error: '#1c0a0a', loading: '#0c1e32' };
    const txts   = { ok: '#22c55e', error: '#ef4444', loading: '#60a5fa' };
    bar.style.borderColor = colors[type] || 'var(--border)';
    bar.style.background  = bgs[type]    || 'var(--bg)';
    document.getElementById('wx-status-text').style.color = txts[type] || 'var(--text-muted)';
    document.getElementById('wx-status-text').textContent = msg;
    document.getElementById('wx-last-update').textContent = extra || '';
    const pulse = document.getElementById('wx-pulse');
    pulse.style.background = type === 'ok' ? '#22c55e' : type === 'error' ? '#ef4444' : 'var(--border)';
    document.getElementById('wx-header-status').textContent =
      type === 'ok' ? 'online' : type === 'loading' ? 'consultando...' : type === 'error' ? 'error' : 'offline';
  }

  function set(id, v) {
    const el = document.getElementById(id);
    if (el) el.textContent = v;
  }

  // ── Fetch OpenWeather ─────────────────────────────────────────────────────

  async function fetchWeather() {
    const key  = window.WX_API_KEY || document.getElementById('wx-apikey')?.value.trim() || '';
    const city = document.getElementById('wx-city').value.trim();
    if (!key)  { setStatus('error', 'API key no configurada'); return; }
    if (!city) { setStatus('error', 'Falta el nombre de la ciudad'); return; }

    setStatus('loading', 'Consultando OpenWeather...');

    const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${encodeURIComponent(key)}&units=metric&lang=es`;

    try {
      const res  = await fetch(url);
      const data = await res.json();

      if (data.cod && String(data.cod) !== '200') {
        setStatus('error', 'Error API (' + data.cod + '): ' + (data.message || 'desconocido'));
        return;
      }

      const ts     = data.dt;
      const temp   = data.main.temp, tmax = data.main.temp_max, tmin = data.main.temp_min;
      const hum    = data.main.humidity, press = data.main.pressure;
      const ws     = +(data.wind.speed * 3.6).toFixed(1);
      const gust   = data.wind.gust ? +(data.wind.gust * 3.6).toFixed(1) : null;
      const wdir   = degToDir(data.wind.deg);
      const clouds = data.clouds ? data.clouds.all : null;
      const vis    = data.visibility || null;
      const rain   = data.rain ? (data.rain['1h'] || (data.rain['3h'] ? data.rain['3h'] / 3 : 0)) : 0;
      const snow   = data.snow ? (data.snow['1h'] || (data.snow['3h'] ? data.snow['3h'] / 3 : 0)) : 0;
      const cond   = data.weather[0].description;
      const dew    = dewPoint(temp, hum);
      const hi     = heatIndex(temp, hum);
      const wc     = windChill(temp, ws);
      const wr     = +((ws * INTERVAL) / 3600000).toFixed(2);

      set('wx-temp',   temp.toFixed(1));
      set('wx-range',  tmax.toFixed(1) + ' / ' + tmin.toFixed(1));
      set('wx-hum',    hum);
      set('wx-press',  press);
      set('wx-wind',   ws);
      set('wx-gust',   gust !== null ? gust : '--');
      set('wx-wdir',   wdir);
      set('wx-clouds', clouds !== null ? clouds : '--');
      set('wx-vis',    vis !== null ? vis.toLocaleString() : '--');
      set('wx-rain',   rain > 0 ? rain.toFixed(1) : '0');
      set('wx-dew',    dew);
      set('wx-hi',     hi !== null ? hi : temp.toFixed(1));
      set('wx-wc',     wc !== null ? wc : temp.toFixed(1));
      set('wx-wr',     wr);
      set('wx-footer-city', 'Estación: ' + data.name + (data.sys.country ? ', ' + data.sys.country : ''));

      rows.unshift({ ts, temp, tmax, tmin, hum, press, ws, gust, wdir, clouds, vis, rain, snow, cond, dew, hi, wc, wr });
      if (rows.length > 500) rows.pop();

      renderTable();
      setStatus('ok',
        'Conectado — ' + data.name + (data.sys.country ? ', ' + data.sys.country : ''),
        'Última actualización: ' + fmtTime(ts)
      );
    } catch (e) {
      setStatus('error', 'Error de red: ' + e.message);
    }
  }

  // ── Tabla ─────────────────────────────────────────────────────────────────

  function renderTable() {
    const count = rows.length;
    const txt = count + ' registro' + (count !== 1 ? 's' : '');
    set('wx-count',  txt);
    set('wx-count2', txt + ' · máx 500 en memoria');

    const tb = document.getElementById('wx-tbody');
    if (!count) {
      tb.innerHTML = '<tr><td colspan="19" style="text-align:center;padding:3rem;color:var(--text-muted)">Sin registros</td></tr>';
      return;
    }
    tb.innerHTML = rows.map(r => `<tr>
      <td>${fmtDate(r.ts)}</td>
      <td style="color:var(--text-muted)">${fmtTime(r.ts)}</td>
      <td style="color:var(--text-green);font-weight:600">${r.temp.toFixed(1)}</td>
      <td>${r.tmax.toFixed(1)}</td>
      <td>${r.tmin.toFixed(1)}</td>
      <td>${r.hum}</td>
      <td>${r.press}</td>
      <td style="color:var(--text-green)">${r.ws}</td>
      <td>${r.wdir}</td>
      <td>${r.gust !== null ? r.gust : '—'}</td>
      <td>${r.clouds !== null ? r.clouds : '—'}</td>
      <td>${r.vis !== null ? r.vis.toLocaleString() : '—'}</td>
      <td style="color:${r.rain > 0 ? '#34d399' : 'inherit'}">${r.rain > 0 ? r.rain.toFixed(1) : '0'}</td>
      <td>${r.snow > 0 ? r.snow.toFixed(1) : '0'}</td>
      <td><span class="estado-badge" style="background:var(--pastel-blue);color:var(--text-blue)">${r.cond}</span></td>
      <td style="color:#a78bfa">${r.dew}</td>
      <td style="color:#a78bfa">${r.hi !== null ? r.hi : r.temp.toFixed(1)}</td>
      <td style="color:#a78bfa">${r.wc !== null ? r.wc : r.temp.toFixed(1)}</td>
      <td style="color:#a78bfa">${r.wr}</td>
    </tr>`).join('');
  }

  // ── Timer ─────────────────────────────────────────────────────────────────

  function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    nextFetchIn = INTERVAL;
    const fill = document.getElementById('wx-timer-fill');
    const cnt  = document.getElementById('wx-countdown');
    timerInterval = setInterval(() => {
      nextFetchIn = Math.max(0, nextFetchIn - 1000);
      fill.style.width = ((INTERVAL - nextFetchIn) / INTERVAL * 100).toFixed(2) + '%';
      const m = Math.floor(nextFetchIn / 60000);
      const s = Math.floor((nextFetchIn % 60000) / 1000);
      cnt.textContent = 'Próxima actualización en ' + m + 'm ' + String(s).padStart(2, '0') + 's';
      if (nextFetchIn === 0) { fetchWeather(); startTimer(); }
    }, 1000);
  }

  // ── API pública ───────────────────────────────────────────────────────────

  window.wxStart = function () { fetchWeather(); startTimer(); };

  window.wxManual = function () { fetchWeather(); if (timerInterval) startTimer(); };

  window.wxClear = function () {
    rows = [];
    renderTable();
    ['wx-temp','wx-range','wx-hum','wx-press','wx-wind','wx-gust','wx-wdir',
     'wx-clouds','wx-vis','wx-rain','wx-dew','wx-hi','wx-wc','wx-wr']
      .forEach(id => set(id, '--'));
  };

  window.wxExportCSV = function () {
    if (!rows.length) { alert('Sin datos para exportar'); return; }
    const h = ['Fecha','Hora','Temp_C','Max_C','Min_C','Humedad_pct','Presion_hPa',
               'Viento_kmh','Direccion','Rafaga_kmh','Nubes_pct','Visibilidad_m',
               'Lluvia_mm','Nieve_mm','Condicion','Rocio_C','SensTermica_C','WindChill_C','RecViento_km'];
    const lines = [h.join(','), ...rows.map(r => [
      fmtDate(r.ts), fmtTime(r.ts),
      r.temp.toFixed(1), r.tmax.toFixed(1), r.tmin.toFixed(1),
      r.hum, r.press, r.ws, r.wdir,
      r.gust !== null ? r.gust : '',
      r.clouds !== null ? r.clouds : '',
      r.vis !== null ? r.vis : '',
      r.rain > 0 ? r.rain.toFixed(1) : 0,
      r.snow > 0 ? r.snow.toFixed(1) : 0,
      '"' + r.cond + '"',
      r.dew,
      r.hi !== null ? r.hi : r.temp.toFixed(1),
      r.wc !== null ? r.wc : r.temp.toFixed(1),
      r.wr
    ].join(','))];
    const blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'meteorologia_' + new Date().toISOString().slice(0, 10) + '.csv';
    a.click();
  };

  // ── Auto-arrancar si la API key ya está cargada ───────────────────────────

  document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('wx-apikey').value.trim()) {
      window.wxStart();
    }
  });

})();
