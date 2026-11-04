/* เช็กก่อนออกบ้าน: พยากรณ์อากาศ + เฝ้าระวังน้ำท่วม แบบเรียลไทม์
 *
 * แหล่งข้อมูล (ไม่ต้องใช้ API key):
 *  - Open-Meteo Forecast API     : อากาศปัจจุบัน รายชั่วโมง รายวัน (อัปเดตทุก 15 นาที)
 *  - Open-Meteo Air Quality API  : PM2.5 / PM10 / AQI (CAMS ของ Copernicus)
 *  - Open-Meteo Flood API        : ปริมาณน้ำในลำน้ำ (GloFAS ของ Copernicus)
 *  - Open-Meteo Geocoding API    : ค้นหาชื่อพื้นที่
 *  - ThaiWater (สสน.)             : ระดับน้ำจากสถานีโทรมาตรทั่วประเทศ
 */
(() => {
  "use strict";

  const REFRESH_MS = 10 * 60 * 1000;
  const FETCH_TIMEOUT_MS = 20000;
  const STATION_RADIUS_KM = 60;
  const STATION_MAX_AGE_H = 24;

  const URLS = {
    forecast: (lat, lon) =>
      "https://api.open-meteo.com/v1/forecast" +
      `?latitude=${lat}&longitude=${lon}` +
      "&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,wind_direction_10m" +
      "&hourly=temperature_2m,precipitation_probability,precipitation,weather_code,uv_index,visibility" +
      "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,uv_index_max,sunrise,sunset,wind_gusts_10m_max" +
      "&past_days=3&forecast_days=7&timezone=auto",
    air: (lat, lon) =>
      "https://air-quality-api.open-meteo.com/v1/air-quality" +
      `?latitude=${lat}&longitude=${lon}` +
      "&current=pm2_5,pm10,us_aqi&hourly=pm2_5&past_days=1&forecast_days=1&timezone=auto",
    flood: (lat, lon) =>
      "https://flood-api.open-meteo.com/v1/flood" +
      `?latitude=${lat}&longitude=${lon}` +
      "&daily=river_discharge,river_discharge_max&past_days=7&forecast_days=14",
    geocode: (q) =>
      "https://geocoding-api.open-meteo.com/v1/search" +
      `?name=${encodeURIComponent(q)}&count=8&language=th&format=json`,
    thaiwater: "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load",
  };

  const QUICK_PLACES = [
    { name: "กรุงเทพมหานคร", lat: 13.7563, lon: 100.5018 },
    { name: "เชียงใหม่", lat: 18.7883, lon: 98.9853 },
    { name: "ขอนแก่น", lat: 16.4419, lon: 102.836 },
    { name: "นครราชสีมา", lat: 14.9799, lon: 102.0978 },
    { name: "อยุธยา", lat: 14.3532, lon: 100.5689 },
    { name: "ชลบุรี", lat: 13.3611, lon: 100.9847 },
    { name: "หาดใหญ่", lat: 7.0084, lon: 100.4747 },
    { name: "ภูเก็ต", lat: 7.8804, lon: 98.3923 },
    { name: "อุบลราชธานี", lat: 15.2287, lon: 104.8564 },
    { name: "นครศรีธรรมราช", lat: 8.4304, lon: 99.9631 },
  ];

  // WMO weather code → ภาษาไทย
  const WEATHER = {
    0: ["ท้องฟ้าแจ่มใส", "☀️", "🌙"],
    1: ["ท้องฟ้าโปร่ง", "🌤️", "🌙"],
    2: ["มีเมฆบางส่วน", "⛅", "☁️"],
    3: ["เมฆมาก", "☁️", "☁️"],
    45: ["มีหมอก", "🌫️", "🌫️"],
    48: ["หมอกน้ำค้างแข็ง", "🌫️", "🌫️"],
    51: ["ฝนละอองเล็กน้อย", "🌦️", "🌧️"],
    53: ["ฝนละออง", "🌦️", "🌧️"],
    55: ["ฝนละอองหนาแน่น", "🌧️", "🌧️"],
    56: ["ฝนละอองเยือกแข็ง", "🌧️", "🌧️"],
    57: ["ฝนละอองเยือกแข็ง", "🌧️", "🌧️"],
    61: ["ฝนเล็กน้อย", "🌦️", "🌧️"],
    63: ["ฝนปานกลาง", "🌧️", "🌧️"],
    65: ["ฝนหนัก", "🌧️", "🌧️"],
    66: ["ฝนเยือกแข็ง", "🌧️", "🌧️"],
    67: ["ฝนเยือกแข็งหนัก", "🌧️", "🌧️"],
    71: ["หิมะเล็กน้อย", "🌨️", "🌨️"],
    73: ["หิมะ", "🌨️", "🌨️"],
    75: ["หิมะหนัก", "🌨️", "🌨️"],
    77: ["เกล็ดหิมะ", "🌨️", "🌨️"],
    80: ["ฝนซู่เล็กน้อย", "🌦️", "🌧️"],
    81: ["ฝนซู่", "🌧️", "🌧️"],
    82: ["ฝนซู่หนักมาก", "⛈️", "⛈️"],
    85: ["หิมะตกเป็นช่วง", "🌨️", "🌨️"],
    86: ["หิมะตกหนักเป็นช่วง", "🌨️", "🌨️"],
    95: ["พายุฝนฟ้าคะนอง", "⛈️", "⛈️"],
    96: ["พายุฝนฟ้าคะนอง ลูกเห็บ", "⛈️", "⛈️"],
    99: ["พายุฝนฟ้าคะนอง ลูกเห็บหนัก", "⛈️", "⛈️"],
  };
  const THUNDER_CODES = new Set([95, 96, 99]);
  const HEAVY_RAIN_CODES = new Set([65, 67, 82, 95, 96, 99]);

  const TH_DAYS = ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."];

  // ---------- state ----------
  const state = {
    place: null,
    refreshTimer: null,
    loading: false,
    lastLoaded: 0,
    thaiwaterCache: null, // { at, stations }
    map: null,
    mapLayer: null,
  };

  // ---------- helpers ----------
  const $ = (id) => document.getElementById(id);

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => (
      { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
    ));
  }

  function num(v) {
    if (v === null || v === undefined || v === "") return NaN;
    const n = typeof v === "number" ? v : parseFloat(v);
    return Number.isFinite(n) ? n : NaN;
  }

  function fmt(v, digits = 0, unit = "") {
    return Number.isFinite(v) ? `${v.toFixed(digits)}${unit}` : "–";
  }

  async function fetchJSON(url) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), FETCH_TIMEOUT_MS);
    try {
      const res = await fetch(url, { signal: ctrl.signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } finally {
      clearTimeout(t);
    }
  }

  function storageGet(key) {
    try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
  }
  function storageSet(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* ignore */ }
  }

  function haversineKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  function weatherInfo(code, isDay = 1) {
    const w = WEATHER[code] || ["ไม่ทราบสภาพอากาศ", "❔", "❔"];
    return { text: w[0], icon: isDay ? w[1] : w[2] };
  }

  function hhmm(isoLocal) {
    return typeof isoLocal === "string" && isoLocal.length >= 16 ? isoLocal.slice(11, 16) : "–";
  }

  function windDir(deg) {
    if (!Number.isFinite(deg)) return "";
    const dirs = ["เหนือ", "ตะวันออกเฉียงเหนือ", "ตะวันออก", "ตะวันออกเฉียงใต้",
      "ใต้", "ตะวันตกเฉียงใต้", "ตะวันตก", "ตะวันตกเฉียงเหนือ"];
    return dirs[Math.round(deg / 45) % 8];
  }

  function relTime(date) {
    const mins = Math.round((Date.now() - date.getTime()) / 60000);
    if (mins < 1) return "เมื่อสักครู่";
    if (mins < 60) return `${mins} นาทีที่แล้ว`;
    const h = Math.round(mins / 60);
    if (h < 48) return `${h} ชั่วโมงที่แล้ว`;
    return `${Math.round(h / 24)} วันที่แล้ว`;
  }

  // ---------- classification ----------
  // เกณฑ์ PM2.5 เฉลี่ย 24 ชม. ของกรมควบคุมมลพิษ (ปรับปรุง 2566)
  function pm25Level(v) {
    if (!Number.isFinite(v)) return null;
    if (v <= 15) return { label: "ดีมาก", cls: "lv-good", rank: 0 };
    if (v <= 25) return { label: "ดี", cls: "lv-good", rank: 0 };
    if (v <= 37.5) return { label: "ปานกลาง", cls: "lv-ok", rank: 1 };
    if (v <= 75) return { label: "เริ่มมีผลกระทบต่อสุขภาพ", cls: "lv-warn", rank: 2 };
    return { label: "มีผลกระทบต่อสุขภาพ", cls: "lv-bad", rank: 3 };
  }

  function uvLevel(v) {
    if (!Number.isFinite(v)) return null;
    if (v < 3) return { label: "ต่ำ", cls: "lv-good", rank: 0 };
    if (v < 6) return { label: "ปานกลาง", cls: "lv-ok", rank: 1 };
    if (v < 8) return { label: "สูง", cls: "lv-warn", rank: 2 };
    if (v < 11) return { label: "สูงมาก", cls: "lv-bad", rank: 3 };
    return { label: "อันตราย", cls: "lv-bad", rank: 3 };
  }

  // เกณฑ์ดัชนีความร้อนของกรมอุตุนิยมวิทยา (ใช้อุณหภูมิที่รู้สึกเป็นตัวแทน)
  function heatLevel(v) {
    if (!Number.isFinite(v) || v < 27) return null;
    if (v < 33) return { label: "เฝ้าระวัง", cls: "lv-ok", rank: 1, tip: "อาจอ่อนเพลียหากอยู่กลางแดดนาน" };
    if (v < 42) return { label: "เตือนภัย", cls: "lv-warn", rank: 2, tip: "เสี่ยงตะคริวและเพลียแดด ดื่มน้ำบ่อยๆ" };
    if (v < 52) return { label: "อันตราย", cls: "lv-bad", rank: 3, tip: "เสี่ยงโรคลมแดด หลีกเลี่ยงกิจกรรมกลางแจ้ง" };
    return { label: "อันตรายมาก", cls: "lv-bad", rank: 3, tip: "เสี่ยงโรคลมแดดสูงมาก งดกิจกรรมกลางแจ้ง" };
  }

  // เกณฑ์ปริมาณฝนรายวันของกรมอุตุนิยมวิทยา
  function rainDayLabel(mm) {
    if (!Number.isFinite(mm) || mm < 0.1) return "ไม่มีฝน";
    if (mm <= 10) return "ฝนเล็กน้อย";
    if (mm <= 35) return "ฝนปานกลาง";
    if (mm <= 90) return "ฝนหนัก";
    return "ฝนหนักมาก";
  }

  // สถานะระดับน้ำตามเกณฑ์ ThaiWater (% ความจุลำน้ำ)
  function stationStatus(pct) {
    if (!Number.isFinite(pct)) return { label: "ไม่มีข้อมูล %", cls: "s-unknown", color: "#8592a3", rank: -1 };
    if (pct > 100) return { label: "ล้นตลิ่ง", cls: "s-over", color: "#d0262d", rank: 3 };
    if (pct > 70) return { label: "น้ำมาก", cls: "s-high", color: "#e08a00", rank: 2 };
    if (pct > 30) return { label: "ปกติ", cls: "s-normal", color: "#1a8f4c", rank: 0 };
    return { label: "น้ำน้อย", cls: "s-low", color: "#c08a2c", rank: 0 };
  }

  const RISK_LEVELS = [
    { label: "ความเสี่ยงต่ำ", cls: "lv-good" },
    { label: "เฝ้าระวัง", cls: "lv-ok" },
    { label: "เสี่ยงสูง", cls: "lv-warn" },
    { label: "วิกฤต", cls: "lv-bad" },
  ];

  // ---------- ThaiWater parsing ----------
  // โครงสร้าง JSON ของ ThaiWater อาจเปลี่ยนได้ จึงอ่านแบบยืดหยุ่นจากหลายชื่อฟิลด์
  function getPath(obj, path) {
    let cur = obj;
    for (const k of path.split(".")) {
      if (cur == null || typeof cur !== "object") return undefined;
      cur = cur[k];
    }
    return cur;
  }
  function pick(obj, paths) {
    for (const p of paths) {
      const v = getPath(obj, p);
      if (v !== undefined && v !== null && v !== "") return v;
    }
    return undefined;
  }
  function text(v) {
    if (v && typeof v === "object") return v.th || v.en || Object.values(v).find((x) => typeof x === "string") || "";
    return v == null ? "" : String(v);
  }

  function findRecordArray(json) {
    const arrays = [];
    (function walk(o, depth) {
      if (!o || depth > 5) return;
      if (Array.isArray(o)) {
        if (o.length && typeof o[0] === "object") arrays.push(o);
        return;
      }
      if (typeof o === "object") for (const k of Object.keys(o)) walk(o[k], depth + 1);
    })(json, 0);
    arrays.sort((a, b) => b.length - a.length);
    return arrays[0] || [];
  }

  function normalizeStation(r) {
    const lat = num(pick(r, ["station.tele_station_lat", "tele_station_lat", "station.lat", "lat", "latitude"]));
    const lon = num(pick(r, ["station.tele_station_long", "tele_station_long", "station.lon", "station.long", "lon", "long", "longitude"]));
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    const leftBank = num(pick(r, ["station.left_bank", "left_bank"]));
    const rightBank = num(pick(r, ["station.right_bank", "right_bank"]));
    let bank = num(pick(r, ["station.min_bank", "min_bank"]));
    if (!Number.isFinite(bank)) {
      const banks = [leftBank, rightBank].filter(Number.isFinite);
      if (banks.length) bank = Math.min(...banks);
    }
    const timeRaw = pick(r, ["waterlevel_datetime", "datetime", "date_time", "date"]);
    const time = timeRaw ? new Date(String(timeRaw).replace(" ", "T") + (/[zZ]|[+-]\d\d:?\d\d$/.test(timeRaw) ? "" : "+07:00")) : null;
    return {
      lat, lon,
      name: text(pick(r, ["station.tele_station_name", "tele_station_name", "station.station_name", "station_name", "name"])) || "สถานีวัดระดับน้ำ",
      level: num(pick(r, ["waterlevel_msl", "water_level_msl", "waterlevel", "water_level"])),
      pct: num(pick(r, ["storage_percent", "waterlevel_percent", "percent"])),
      bank,
      ground: num(pick(r, ["station.ground_level", "ground_level"])),
      time: time && !isNaN(time) ? time : null,
      province: text(pick(r, ["geocode.province_name", "province_name", "station.province_name"])),
      amphoe: text(pick(r, ["geocode.amphoe_name", "amphoe_name"])),
      tumbon: text(pick(r, ["geocode.tumbon_name", "tumbon_name"])),
      river: text(pick(r, ["river_name", "station.river_name", "basin.basin_name"])),
      agency: text(pick(r, ["agency.agency_shortname", "agency.agency_name", "agency_name"])),
    };
  }

  async function loadThaiWaterStations() {
    const c = state.thaiwaterCache;
    if (c && Date.now() - c.at < REFRESH_MS - 30000) return c.stations;
    const json = await fetchJSON(URLS.thaiwater);
    const stations = findRecordArray(json).map(normalizeStation).filter(Boolean);
    if (!stations.length) throw new Error("ไม่พบข้อมูลสถานีในผลลัพธ์");
    state.thaiwaterCache = { at: Date.now(), stations };
    return stations;
  }

  function nearestStations(all, lat, lon) {
    const cutoff = Date.now() - STATION_MAX_AGE_H * 3600 * 1000;
    return all
      .map((s) => ({ ...s, dist: haversineKm(lat, lon, s.lat, s.lon) }))
      .filter((s) => s.dist <= STATION_RADIUS_KM && (!s.time || s.time.getTime() >= cutoff))
      .sort((a, b) => a.dist - b.dist)
      .slice(0, 6);
  }

  // ---------- charts (inline SVG) ----------
  function rainChartSVG(hours) {
    const W = 360, H = 150, padL = 26, padB = 22, padT = 14;
    const n = hours.length;
    if (!n) return "<p class='muted'>ไม่มีข้อมูล</p>";
    const bw = (W - padL) / n;
    const maxMm = Math.max(5, ...hours.map((h) => h.mm || 0));
    let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
    [0, 50, 100].forEach((p) => {
      const y = padT + (H - padT - padB) * (1 - p / 100);
      s += `<line class="grid-line" x1="${padL}" x2="${W}" y1="${y}" y2="${y}"/>`;
      s += `<text x="0" y="${y + 4}">${p}%</text>`;
    });
    hours.forEach((h, i) => {
      const x = padL + i * bw + 2;
      const plotH = H - padT - padB;
      const ph = Number.isFinite(h.prob) ? (h.prob / 100) * plotH : 0;
      const mh = Number.isFinite(h.mm) ? Math.min(1, h.mm / maxMm) * plotH : 0;
      s += `<rect class="bar-soft" x="${x}" y="${padT + plotH - ph}" width="${bw - 4}" height="${ph}" rx="2"><title>${h.time} โอกาสฝน ${fmt(h.prob, 0, "%")}</title></rect>`;
      if (mh > 0) s += `<rect class="bar" x="${x + (bw - 4) * 0.25}" y="${padT + plotH - mh}" width="${(bw - 4) * 0.5}" height="${mh}" rx="2"><title>${h.time} ฝน ${fmt(h.mm, 1, " มม.")}</title></rect>`;
      if (i % 2 === 0) s += `<text x="${x}" y="${H - 6}">${h.time}</text>`;
    });
    s += "</svg>";
    return s + `<p class="note"><span class="dot" style="background:var(--bar-soft)"></span>โอกาสฝน (%)
      <span class="dot" style="background:var(--bar)"></span>ปริมาณฝน (สูงสุดของกราฟ ${maxMm.toFixed(1)} มม./ชม.)</p>`;
  }

  function riverChartSVG(days, todayIdx) {
    const W = 360, H = 140, padL = 6, padB = 22, padT = 10;
    const vals = days.map((d) => d.q).filter(Number.isFinite);
    if (vals.length < 2) return "<p class='muted'>ไม่มีข้อมูลลำน้ำสำหรับจุดนี้</p>";
    const max = Math.max(...vals) * 1.1 || 1;
    const min = 0;
    const plotH = H - padT - padB;
    const x = (i) => padL + (i / (days.length - 1)) * (W - padL * 2);
    const y = (v) => padT + plotH * (1 - (v - min) / (max - min));
    const pts = (arr) => arr.map((d) => `${x(d.i).toFixed(1)},${y(d.q).toFixed(1)}`).join(" ");
    const indexed = days.map((d, i) => ({ ...d, i })).filter((d) => Number.isFinite(d.q));
    const past = indexed.filter((d) => d.i <= todayIdx);
    const future = indexed.filter((d) => d.i >= todayIdx);
    let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
    s += `<line class="grid-line" x1="0" x2="${W}" y1="${padT + plotH}" y2="${padT + plotH}"/>`;
    if (todayIdx >= 0) {
      const tx = x(todayIdx);
      s += `<line class="now-line" x1="${tx}" x2="${tx}" y1="${padT}" y2="${padT + plotH}"/>`;
      s += `<text x="${Math.min(tx + 4, W - 40)}" y="${padT + 10}">วันนี้</text>`;
    }
    if (past.length > 1) s += `<polyline class="line-past" points="${pts(past)}"/>`;
    if (future.length > 1) s += `<polyline class="line" points="${pts(future)}"/>`;
    days.forEach((d, i) => {
      if (i % 3 === 0) s += `<text x="${Math.min(x(i), W - 30)}" y="${H - 6}">${d.date.slice(8, 10)}/${d.date.slice(5, 7)}</text>`;
    });
    s += `<text x="${W - 120}" y="${H - 28}">สูงสุดในกราฟ ${Math.max(...vals).toFixed(0)} ม³/วิ</text>`;
    s += "</svg>";
    return s;
  }

  // ---------- rendering ----------
  function renderPlaceHeader() {
    const p = state.place;
    $("place-name").textContent = p.name;
    const meta = [p.admin, `${p.lat.toFixed(3)}, ${p.lon.toFixed(3)}`].filter(Boolean).join(" · ");
    $("place-meta").textContent = meta;
    document.title = `${p.name} | เช็กก่อนออกบ้าน`;
  }

  function renderWeather(fc) {
    const cur = fc.current || {};
    const H = fc.hourly || {};
    const D = fc.daily || {};
    const times = H.time || [];
    // index ของชั่วโมงปัจจุบัน (เวลาท้องถิ่นของพื้นที่นั้น)
    let idx = -1;
    for (let i = 0; i < times.length; i++) if (times[i] <= cur.time) idx = i;
    if (idx < 0) idx = 0;

    const w = weatherInfo(cur.weather_code, cur.is_day);
    $("now-icon").textContent = w.icon;
    $("now-temp").textContent = fmt(cur.temperature_2m, 0, "°C");
    $("now-desc").textContent = w.text;
    $("now-feels").textContent = fmt(cur.apparent_temperature, 0, "°C");
    $("now-hum").textContent = fmt(cur.relative_humidity_2m, 0, "%");
    $("now-wind").textContent = Number.isFinite(cur.wind_speed_10m)
      ? `${fmt(cur.wind_speed_10m, 0)} / ${fmt(cur.wind_gusts_10m, 0)} กม./ชม. ${windDir(cur.wind_direction_10m)}`
      : "–";
    const vis = num(H.visibility?.[idx]);
    $("now-vis").textContent = Number.isFinite(vis) ? (vis >= 10000 ? "มากกว่า 10 กม." : `${(vis / 1000).toFixed(1)} กม.`) : "–";

    const heat = heatLevel(cur.apparent_temperature);
    $("heat-note").innerHTML = heat
      ? `ดัชนีความร้อน: <strong class="${heat.cls}" style="padding:0 .4rem;border-radius:6px">${heat.label}</strong> ${esc(heat.tip)}`
      : "";

    // ฝน 12 ชม.
    const next = [];
    for (let i = idx + 1; i <= idx + 12 && i < times.length; i++) {
      next.push({ time: hhmm(times[i]), prob: num(H.precipitation_probability?.[i]), mm: num(H.precipitation?.[i]), code: H.weather_code?.[i] });
    }
    $("rain-chart").innerHTML = rainChartSVG(next);
    const maxProb6 = Math.max(0, ...next.slice(0, 6).map((h) => h.prob).filter(Number.isFinite));
    const sum12 = next.reduce((a, h) => a + (Number.isFinite(h.mm) ? h.mm : 0), 0);
    const firstRain = next.find((h) => (h.prob >= 50) || h.mm >= 0.5);
    $("rain-summary").textContent = firstRain
      ? `คาดว่าจะเริ่มมีฝนราว ${firstRain.time} น. ฝนรวม 12 ชม. ประมาณ ${sum12.toFixed(1)} มม.`
      : `โอกาสฝนต่ำใน 12 ชั่วโมงข้างหน้า (ฝนรวม ${sum12.toFixed(1)} มม.)`;

    // UV / แดด
    const uvNow = num(H.uv_index?.[idx]);
    const todayIdx = (D.time || []).indexOf((cur.time || "").slice(0, 10));
    const ti = todayIdx >= 0 ? todayIdx : 3; // past_days=3 → index 3 คือวันนี้
    const uvMaxToday = num(D.uv_index_max?.[ti]);
    const uvl = uvLevel(Number.isFinite(uvNow) ? uvNow : uvMaxToday);
    $("uv-badge").className = `level-badge ${uvl ? uvl.cls : ""}`;
    $("uv-badge").textContent = uvl ? `UV ${uvl.label}` : "–";
    $("uv-now").textContent = fmt(uvNow, 1);
    $("uv-max").textContent = Number.isFinite(uvMaxToday) ? `${uvMaxToday.toFixed(1)} (${uvLevel(uvMaxToday).label})` : "–";
    $("sunrise").textContent = hhmm(D.sunrise?.[ti]) + " น.";
    $("sunset").textContent = hhmm(D.sunset?.[ti]) + " น.";
    $("uv-note").textContent = Number.isFinite(uvMaxToday) && uvMaxToday >= 6
      ? "ช่วง 10:00–15:00 น. แดดแรงที่สุด ควรทาครีมกันแดด SPF30+ และสวมหมวก"
      : "ระดับ UV วันนี้ไม่สูงมาก";

    // 7 วัน
    const days = [];
    for (let i = ti; i < (D.time || []).length && days.length < 7; i++) {
      const d = new Date(D.time[i] + "T00:00:00");
      const wi = weatherInfo(D.weather_code?.[i], 1);
      days.push(`<div class="day">
        <div class="day-name">${i === ti ? "วันนี้" : `${TH_DAYS[d.getDay()]} ${d.getDate()}`}</div>
        <div class="day-icon" aria-hidden="true">${wi.icon}</div>
        <div>${esc(wi.text)}</div>
        <div class="day-temp">${fmt(num(D.temperature_2m_max?.[i]), 0, "°")} / ${fmt(num(D.temperature_2m_min?.[i]), 0, "°")}</div>
        <div class="day-rain">☔ ${fmt(num(D.precipitation_probability_max?.[i]), 0, "%")} · ${fmt(num(D.precipitation_sum?.[i]), 1, " มม.")}</div>
        <div class="day-uv">${esc(rainDayLabel(num(D.precipitation_sum?.[i])))} · UV ${fmt(num(D.uv_index_max?.[i]), 0)}</div>
      </div>`);
    }
    $("daily").innerHTML = days.join("");

    // ปริมาณฝนสะสม
    let past72 = 0, next24 = 0;
    for (let i = Math.max(0, idx - 71); i <= idx; i++) past72 += num(H.precipitation?.[i]) || 0;
    for (let i = idx + 1; i <= idx + 24 && i < times.length; i++) next24 += num(H.precipitation?.[i]) || 0;
    let next7d = 0;
    for (let i = ti; i < ti + 7 && i < (D.time || []).length; i++) next7d += num(D.precipitation_sum?.[i]) || 0;
    $("rain-past72").textContent = `${past72.toFixed(1)} มม.`;
    $("rain-next24").textContent = `${next24.toFixed(1)} มม.`;
    $("rain-next7d").textContent = `${next7d.toFixed(1)} มม.`;

    const next6 = next.slice(0, 6);
    return {
      temp: num(cur.temperature_2m),
      feels: num(cur.apparent_temperature),
      gust: num(cur.wind_gusts_10m),
      code: cur.weather_code,
      vis,
      uvMaxToday,
      maxProb6,
      thunder6: next6.some((h) => THUNDER_CODES.has(h.code)) || THUNDER_CODES.has(cur.weather_code),
      heavy6: next6.some((h) => HEAVY_RAIN_CODES.has(h.code) || h.mm >= 10),
      firstRain,
      past72, next24, next7d,
      maxGustToday: num(D.wind_gusts_10m_max?.[ti]),
      heat,
    };
  }

  function renderAir(aq) {
    const cur = aq?.current || {};
    const H = aq?.hourly || {};
    const pm25 = num(cur.pm2_5);
    // ค่าเฉลี่ย 24 ชม. ล่าสุด (ใช้เทียบเกณฑ์ไทย)
    let avg24 = NaN;
    if (Array.isArray(H.time) && cur.time) {
      const vals = [];
      H.time.forEach((t, i) => { if (t <= cur.time) vals.push(num(H.pm2_5?.[i])); });
      const last = vals.slice(-24).filter(Number.isFinite);
      if (last.length >= 12) avg24 = last.reduce((a, b) => a + b, 0) / last.length;
    }
    const basis = Number.isFinite(avg24) ? avg24 : pm25;
    const lv = pm25Level(basis);
    $("air-badge").className = `level-badge ${lv ? lv.cls : ""}`;
    $("air-badge").textContent = lv ? lv.label : "ไม่มีข้อมูล";
    $("air-pm25").textContent = Number.isFinite(pm25) ? `${pm25.toFixed(1)} µg/m³` : "–";
    $("air-pm10").textContent = fmt(num(cur.pm10), 1, " µg/m³");
    $("air-aqi").textContent = fmt(num(cur.us_aqi), 0);
    $("air-note").textContent = Number.isFinite(avg24)
      ? `เฉลี่ย 24 ชม. ${avg24.toFixed(1)} µg/m³ (เกณฑ์กรมควบคุมมลพิษ: ไม่เกิน 37.5)`
      : "";
    return { pm25: basis, level: lv };
  }

  function renderRiver(fl) {
    const D = fl?.daily || {};
    const times = D.time || [];
    const todayStr = new Date().toISOString().slice(0, 10);
    let todayIdx = times.indexOf(todayStr);
    if (todayIdx < 0) todayIdx = Math.min(7, times.length - 1);
    const days = times.map((t, i) => ({ date: t, q: num(D.river_discharge?.[i]) }));
    $("river-chart").innerHTML = riverChartSVG(days, todayIdx);

    const past = days.slice(Math.max(0, todayIdx - 7), todayIdx + 1).map((d) => d.q).filter(Number.isFinite);
    const fut = days.slice(todayIdx, todayIdx + 8).map((d) => d.q).filter(Number.isFinite);
    const qNow = days[todayIdx]?.q;
    const pastMean = past.length ? past.reduce((a, b) => a + b, 0) / past.length : NaN;
    const futMax = fut.length ? Math.max(...fut) : NaN;
    const ratio = futMax / pastMean;

    let note = "";
    let rank = 0;
    if (!Number.isFinite(qNow) || !Number.isFinite(pastMean)) {
      note = "ไม่มีลำน้ำขนาดใหญ่ในแบบจำลองสำหรับตำแหน่งนี้";
    } else if (pastMean < 5) {
      note = `ลำน้ำในจุดนี้มีขนาดเล็ก (${qNow.toFixed(1)} ม³/วินาที) ผลจากแบบจำลองระดับลุ่มน้ำอาจไม่สะท้อนน้ำท่วมขังในเมือง`;
    } else {
      const trend = ratio >= 1.15 ? "มีแนวโน้มเพิ่มขึ้น" : ratio <= 0.85 ? "มีแนวโน้มลดลง" : "ค่อนข้างคงที่";
      note = `ตอนนี้ ${qNow.toFixed(0)} ม³/วินาที ${trend} สูงสุดใน 7 วันข้างหน้าประมาณ ${futMax.toFixed(0)} ม³/วินาที (${(ratio * 100).toFixed(0)}% ของค่าเฉลี่ย 7 วันที่ผ่านมา)`;
      if (ratio >= 2) rank = 2;
      else if (ratio >= 1.5) rank = 1;
    }
    $("river-note").textContent = note;
    return { rank, ratio, qNow, futMax, valid: Number.isFinite(pastMean) && pastMean >= 5 };
  }

  function renderStations(list, err) {
    const box = $("stations");
    if (err) {
      box.innerHTML = `<div class="error-box">ดึงข้อมูลสถานีวัดระดับน้ำจาก ThaiWater ไม่สำเร็จ (${esc(err.message || err)})
        <br>ตรวจสอบระดับน้ำล่าสุดได้ที่ <a href="https://www.thaiwater.net/water/wl" target="_blank" rel="noopener">thaiwater.net</a></div>`;
      return;
    }
    if (!list.length) {
      box.innerHTML = `<p class="muted">ไม่พบสถานีวัดระดับน้ำที่รายงานข้อมูลใน ${STATION_MAX_AGE_H} ชม. ล่าสุด ภายในรัศมี ${STATION_RADIUS_KM} กม.</p>`;
      return;
    }
    box.innerHTML = list.map((s) => {
      const st = stationStatus(s.pct);
      const where = [s.tumbon && `ต.${s.tumbon}`, s.amphoe && `อ.${s.amphoe}`, s.province && `จ.${s.province}`].filter(Boolean).join(" ");
      let levelText = Number.isFinite(s.level) ? `ระดับน้ำ ${s.level.toFixed(2)} ม.รทก.` : "ไม่มีค่าระดับน้ำ";
      if (Number.isFinite(s.level) && Number.isFinite(s.bank)) {
        const diff = s.level - s.bank;
        levelText += diff > 0
          ? ` · <strong style="color:var(--bad)">สูงกว่าตลิ่ง ${diff.toFixed(2)} ม.</strong>`
          : ` · ต่ำกว่าตลิ่ง ${Math.abs(diff).toFixed(2)} ม.`;
      }
      const width = Number.isFinite(s.pct) ? Math.max(2, Math.min(100, s.pct)) : 0;
      return `<div class="station">
        <div class="station-head">
          <span class="station-name">${esc(s.name)}</span>
          <span class="station-dist">${s.dist.toFixed(1)} กม.</span>
        </div>
        <div class="station-meta">${esc([where, s.river && `ลำน้ำ ${s.river}`].filter(Boolean).join(" · "))}</div>
        <div class="station-level">${levelText}</div>
        <div class="gauge" title="${fmt(s.pct, 0, "% ของความจุลำน้ำ")}"><span style="width:${width}%;background:${st.color}"></span></div>
        <div class="station-meta"><span class="dot ${st.cls}" style="margin-left:0"></span>${st.label} ${Number.isFinite(s.pct) ? `(${s.pct.toFixed(0)}% ของความจุลำน้ำ)` : ""}
          · ${s.time ? `อัปเดต ${relTime(s.time)}` : "ไม่ทราบเวลา"}${s.agency ? ` · ${esc(s.agency)}` : ""}</div>
      </div>`;
    }).join("");
  }

  function renderMap(stations) {
    if (!window.L) return;
    const p = state.place;
    if (!state.map) {
      state.map = L.map("map", { scrollWheelZoom: false });
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }).addTo(state.map);
    }
    if (state.mapLayer) state.mapLayer.remove();
    const layer = L.layerGroup();
    L.marker([p.lat, p.lon]).bindPopup(`<strong>${esc(p.name)}</strong>`).addTo(layer);
    const bounds = [[p.lat, p.lon]];
    stations.forEach((s) => {
      const st = stationStatus(s.pct);
      L.circleMarker([s.lat, s.lon], { radius: 9, color: "#fff", weight: 2, fillColor: st.color, fillOpacity: 0.95 })
        .bindPopup(`<strong>${esc(s.name)}</strong><br>${st.label}${Number.isFinite(s.pct) ? ` (${s.pct.toFixed(0)}%)` : ""}<br>
          ${Number.isFinite(s.level) ? `ระดับน้ำ ${s.level.toFixed(2)} ม.รทก.` : ""}`)
        .addTo(layer);
      bounds.push([s.lat, s.lon]);
    });
    layer.addTo(state.map);
    state.mapLayer = layer;
    if (bounds.length > 1) state.map.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 });
    else state.map.setView([p.lat, p.lon], 11);
    setTimeout(() => state.map.invalidateSize(), 50);
  }

  function assessFlood(wx, river, stations) {
    const found = []; // [ระดับ, เหตุผล]
    if (wx) {
      if (wx.past72 >= 150 || wx.next24 >= 90) found.push([3, `ฝนสะสมมาก: 72 ชม. ที่ผ่านมา ${wx.past72.toFixed(0)} มม. และคาดว่าจะตกอีก ${wx.next24.toFixed(0)} มม. ใน 24 ชม.`]);
      else if (wx.past72 >= 90 || wx.next24 >= 35) found.push([2, `ฝนหนัก: 72 ชม. ที่ผ่านมา ${wx.past72.toFixed(0)} มม. / 24 ชม. ข้างหน้า ${wx.next24.toFixed(0)} มม. เสี่ยงน้ำท่วมขังในที่ลุ่มและถนน`]);
      else if (wx.past72 >= 35 || wx.next24 >= 20) found.push([1, `มีฝนสะสมปานกลาง (72 ชม. ${wx.past72.toFixed(0)} มม. / 24 ชม. ข้างหน้า ${wx.next24.toFixed(0)} มม.) อาจมีน้ำขังชั่วคราว`]);
    }
    const near = (stations || []).filter((s) => s.dist <= 25 && Number.isFinite(s.pct));
    if (near.length) {
      const worst = near.reduce((a, b) => (b.pct > a.pct ? b : a));
      const where = `สถานี ${worst.name} (ห่าง ${worst.dist.toFixed(0)} กม.)`;
      if (worst.pct > 100) found.push([3, `${where} น้ำล้นตลิ่ง ระดับน้ำ ${worst.pct.toFixed(0)}% ของความจุลำน้ำ`]);
      else if (worst.pct >= 90) found.push([2, `${where} ระดับน้ำใกล้ตลิ่ง ${worst.pct.toFixed(0)}% ของความจุลำน้ำ`]);
      else if (worst.pct > 70) found.push([1, `${where} น้ำมาก ${worst.pct.toFixed(0)}% ของความจุลำน้ำ`]);
    }
    if (river?.valid && river.rank) {
      found.push([river.rank, `แบบจำลองคาดว่าปริมาณน้ำในลำน้ำจะเพิ่มเป็น ${(river.ratio * 100).toFixed(0)}% ของค่าเฉลี่ยสัปดาห์ที่ผ่านมา`]);
    }
    found.sort((a, b) => b[0] - a[0]);
    const level = found.length ? found[0][0] : 0;
    const reasons = found.length
      ? found.map((f) => f[1])
      : ["ไม่พบสัญญาณน้ำท่วมจากปริมาณฝน ระดับน้ำในสถานีใกล้เคียง และแบบจำลองลำน้ำ"];
    const lv = RISK_LEVELS[level];
    $("flood-badge").className = `level-badge ${lv.cls}`;
    $("flood-badge").textContent = `น้ำท่วม: ${lv.label}`;
    $("flood-reasons").innerHTML = reasons.map((r) => `<li>${esc(r)}</li>`).join("");
    return { level, label: lv.label, reasons };
  }

  function renderVerdict(wx, air, flood) {
    const items = [];
    const alerts = [];
    let worst = 0;

    if (flood) {
      if (flood.level >= 3) { worst = 3; alerts.push(["bad", "🌊", `ความเสี่ยงน้ำท่วมระดับวิกฤต: ${flood.reasons[0]} เลี่ยงการเดินทางที่ไม่จำเป็นและติดตามประกาศของ ปภ.`]); }
      else if (flood.level === 2) { worst = Math.max(worst, 2); alerts.push(["warn", "🌊", `เสี่ยงน้ำท่วมสูง: ${flood.reasons[0]}`]); }
      if (flood.level >= 2) items.push(["🚗", "เลี่ยงถนนที่ลุ่มและทางลอด", "อย่าขับรถหรือเดินลุยน้ำที่ไหลเชี่ยว น้ำลึกเพียง 30 ซม. ก็พัดรถเก๋งได้"]);
      else if (flood.level === 1) items.push(["🌊", "อาจมีน้ำขังบางจุด", "เผื่อเวลาเดินทาง และตรวจเส้นทางก่อนออก"]);
    }
    if (wx) {
      if (wx.thunder6) { worst = Math.max(worst, 2); alerts.push(["warn", "⛈️", "อาจมีพายุฝนฟ้าคะนองใน 6 ชั่วโมงข้างหน้า หลีกเลี่ยงที่โล่งแจ้งและต้นไม้ใหญ่"]); }
      if (wx.maxProb6 >= 60 || wx.heavy6) items.push(["☂️", "พกร่มหรือเสื้อกันฝน", wx.firstRain ? `ฝนอาจเริ่มราว ${wx.firstRain.time} น. (โอกาส ${wx.maxProb6.toFixed(0)}%)` : `โอกาสฝนสูงสุด ${wx.maxProb6.toFixed(0)}%`]);
      else if (wx.maxProb6 >= 30) items.push(["🌂", "พกร่มพับไว้ก็ดี", `โอกาสฝนใน 6 ชม. ${wx.maxProb6.toFixed(0)}%`]);
      if (wx.heat && wx.heat.rank >= 2) { worst = Math.max(worst, wx.heat.rank); items.push(["🥵", `อากาศร้อน (${wx.heat.label})`, `รู้สึกเหมือน ${wx.feels.toFixed(0)}°C ${wx.heat.tip}`]); }
      if (wx.heat && wx.heat.rank >= 3) alerts.push(["bad", "🥵", `ดัชนีความร้อนระดับ${wx.heat.label} (รู้สึกเหมือน ${wx.feels.toFixed(0)}°C)`]);
      if (Number.isFinite(wx.uvMaxToday) && wx.uvMaxToday >= 6) worst = Math.max(worst, 1);
      if (Number.isFinite(wx.uvMaxToday) && wx.uvMaxToday >= 6) items.push(["🧴", "ทาครีมกันแดด สวมหมวก/แว่นกันแดด", `UV สูงสุดวันนี้ ${wx.uvMaxToday.toFixed(0)} (${uvLevel(wx.uvMaxToday).label})`]);
      const gust = Math.max(wx.gust || 0, wx.maxGustToday || 0);
      if (gust >= 60) { worst = Math.max(worst, 2); alerts.push(["warn", "💨", `ลมกระโชกแรงถึง ${gust.toFixed(0)} กม./ชม. ระวังป้ายและกิ่งไม้หักโค่น`]); }
      else if (gust >= 40) items.push(["💨", "ลมค่อนข้างแรง", `ลมกระโชกสูงสุด ${gust.toFixed(0)} กม./ชม.`]);
      if (Number.isFinite(wx.vis) && wx.vis < 1000) items.push(["🌫️", "ทัศนวิสัยต่ำ", `มองเห็นได้ราว ${(wx.vis / 1000).toFixed(1)} กม. เปิดไฟหน้ารถและขับช้าลง`]);
    }
    if (air?.level) {
      if (air.level.rank >= 2) {
        worst = Math.max(worst, air.level.rank);
        items.push(["😷", "สวมหน้ากาก N95", `PM2.5 ${air.pm25.toFixed(0)} µg/m³ (${air.level.label}) ลดกิจกรรมกลางแจ้ง`]);
        if (air.level.rank >= 3) alerts.push(["bad", "😷", `PM2.5 ${air.pm25.toFixed(0)} µg/m³ มีผลกระทบต่อสุขภาพ กลุ่มเสี่ยงควรงดออกนอกอาคาร`]);
      } else if (air.level.rank === 1) {
        items.push(["😷", "กลุ่มเสี่ยงควรพกหน้ากาก", `PM2.5 ${air.pm25.toFixed(0)} µg/m³ (ปานกลาง)`]);
      }
    }
    if (!items.length) items.push(["✅", "ออกจากบ้านได้ตามปกติ", "ไม่พบสภาพอากาศที่ต้องระวังเป็นพิเศษ"]);
    items.push(["📱", "ชาร์จโทรศัพท์ให้เต็ม", "บันทึกเบอร์ฉุกเฉิน 1784 และ 1669 ไว้"]);

    const verdicts = [
      "ออกจากบ้านได้ตามปกติ สภาพอากาศเอื้ออำนวย",
      "ออกได้ แต่ควรเตรียมของตามรายการด้านล่าง",
      "ควรระวังเป็นพิเศษ ตรวจเส้นทางและเตรียมตัวก่อนออก",
      "ไม่แนะนำให้ออกจากบ้านหากไม่จำเป็น",
    ];
    $("verdict-text").textContent = verdicts[worst];
    $("checklist").innerHTML = items.map(([ic, title, sub]) =>
      `<li><span class="ic" aria-hidden="true">${ic}</span><div><strong>${esc(title)}</strong><br><span class="muted">${esc(sub)}</span></div></li>`
    ).join("");
    $("alerts").innerHTML = alerts.map(([kind, ic, msg]) =>
      `<div class="alert alert-${kind}"><span aria-hidden="true">${ic}</span><span>${esc(msg)}</span></div>`
    ).join("");
  }

  function sectionError(id, msg) {
    const el = $(id);
    if (el) el.insertAdjacentHTML("beforeend", `<div class="error-box">${esc(msg)}</div>`);
  }

  // ---------- main load ----------
  async function loadAll() {
    if (!state.place || state.loading) return;
    state.loading = true;
    const { lat, lon } = state.place;
    $("refresh-btn").disabled = true;
    $("updated-at").textContent = "กำลังอัปเดตข้อมูล…";
    document.querySelectorAll(".error-box").forEach((e) => e.remove());

    const [fc, aq, fl, tw] = await Promise.allSettled([
      fetchJSON(URLS.forecast(lat, lon)),
      fetchJSON(URLS.air(lat, lon)),
      fetchJSON(URLS.flood(lat, lon)),
      loadThaiWaterStations(),
    ]);

    let wx = null, air = null, river = null, stations = [];
    if (fc.status === "fulfilled") {
      try { wx = renderWeather(fc.value); } catch (e) { console.error(e); sectionError("card-now", "แสดงผลพยากรณ์อากาศไม่สำเร็จ"); }
    } else {
      sectionError("card-now", `ดึงข้อมูลพยากรณ์อากาศไม่สำเร็จ (${fc.reason?.message || "เครือข่าย"})`);
    }
    if (aq.status === "fulfilled") {
      try { air = renderAir(aq.value); } catch (e) { console.error(e); }
    } else {
      sectionError("card-air", "ดึงข้อมูลคุณภาพอากาศไม่สำเร็จ ดูได้ที่ air4thai.pcd.go.th");
    }
    if (fl.status === "fulfilled") {
      try { river = renderRiver(fl.value); } catch (e) { console.error(e); }
    } else {
      $("river-chart").innerHTML = "";
      $("river-note").textContent = "ดึงข้อมูลแบบจำลองลำน้ำไม่สำเร็จ";
    }
    if (tw.status === "fulfilled") {
      stations = nearestStations(tw.value, lat, lon);
      renderStations(stations);
      if (state.place.fromGPS && stations[0] && !state.place.admin) {
        const s = stations[0];
        state.place.admin = [s.amphoe && `อ.${s.amphoe}`, s.province && `จ.${s.province}`].filter(Boolean).join(" ");
        renderPlaceHeader();
      }
    } else {
      renderStations([], tw.reason || new Error("เครือข่าย"));
    }
    try { renderMap(stations); } catch (e) { console.error(e); }

    const flood = assessFlood(wx, river, stations);
    renderVerdict(wx, air, flood);

    const anyOk = [fc, aq, fl, tw].some((r) => r.status === "fulfilled");
    state.lastLoaded = Date.now();
    const now = new Date();
    $("updated-at").textContent = anyOk
      ? `อัปเดตล่าสุด ${now.toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit" })} น. · อัปเดตอัตโนมัติทุก 10 นาที`
      : "เชื่อมต่อแหล่งข้อมูลไม่ได้ ลองรีเฟรชอีกครั้ง";
    document.querySelector(".live-dot").classList.toggle("stale", !anyOk);
    $("refresh-btn").disabled = false;
    state.loading = false;
  }

  function scheduleRefresh() {
    clearInterval(state.refreshTimer);
    state.refreshTimer = setInterval(loadAll, REFRESH_MS);
  }

  function setPlace(place) {
    state.place = place;
    storageSet("lastPlace", { ...place, fromGPS: false });
    renderPlaceHeader();
    loadAll();
    scheduleRefresh();
  }

  // ---------- search ----------
  async function doSearch(q) {
    const list = $("search-results");
    list.hidden = false;
    list.innerHTML = `<li class="muted" style="padding:.5rem .7rem">กำลังค้นหา…</li>`;
    try {
      const json = await fetchJSON(URLS.geocode(q));
      const results = (json.results || []).sort((a, b) => (b.country_code === "TH") - (a.country_code === "TH"));
      if (!results.length) {
        list.innerHTML = `<li class="muted" style="padding:.5rem .7rem">ไม่พบ “${esc(q)}” ลองพิมพ์ชื่อภาษาอังกฤษ เช่น Hat Yai</li>`;
        return;
      }
      list.innerHTML = results.map((r, i) => {
        const admin = [r.admin2, r.admin1, r.country].filter(Boolean).join(", ");
        return `<li><button type="button" data-i="${i}">${esc(r.name)} <small>${esc(admin)}</small></button></li>`;
      }).join("");
      list.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
        const r = results[+b.dataset.i];
        list.hidden = true;
        $("search-input").value = "";
        setPlace({ name: r.name, admin: [r.admin2, r.admin1].filter(Boolean).join(", "), lat: r.latitude, lon: r.longitude });
      }));
    } catch (e) {
      list.innerHTML = `<li class="muted" style="padding:.5rem .7rem">ค้นหาไม่สำเร็จ (${esc(e.message)})</li>`;
    }
  }

  function useGeolocation() {
    if (!navigator.geolocation) {
      alert("เบราว์เซอร์นี้ไม่รองรับการระบุตำแหน่ง");
      return;
    }
    const btn = $("geo-btn");
    btn.disabled = true;
    btn.textContent = "กำลังหาตำแหน่ง…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        btn.disabled = false;
        btn.textContent = "📍 ตำแหน่งของฉัน";
        state.place = { name: "ตำแหน่งปัจจุบันของคุณ", admin: "", lat: pos.coords.latitude, lon: pos.coords.longitude, fromGPS: true };
        renderPlaceHeader();
        loadAll();
        scheduleRefresh();
      },
      (err) => {
        btn.disabled = false;
        btn.textContent = "📍 ตำแหน่งของฉัน";
        alert(err.code === 1
          ? "คุณไม่ได้อนุญาตให้เข้าถึงตำแหน่ง กรุณาค้นหาชื่อพื้นที่แทน"
          : "หาตำแหน่งไม่สำเร็จ กรุณาค้นหาชื่อพื้นที่แทน");
      },
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 5 * 60 * 1000 }
    );
  }

  // ---------- init ----------
  function init() {
    $("quick-places").innerHTML = QUICK_PLACES.map((p, i) =>
      `<button type="button" class="chip" data-i="${i}">${esc(p.name)}</button>`).join("");
    $("quick-places").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-i]");
      if (b) setPlace({ ...QUICK_PLACES[+b.dataset.i], admin: "ประเทศไทย" });
    });

    $("search-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const q = $("search-input").value.trim();
      if (q.length >= 2) doSearch(q);
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest("#search-form")) $("search-results").hidden = true;
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") $("search-results").hidden = true;
    });
    $("geo-btn").addEventListener("click", useGeolocation);
    $("refresh-btn").addEventListener("click", () => { state.thaiwaterCache = null; loadAll(); });

    // กลับมาที่แท็บหลังหายไปนาน → อัปเดตทันที
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && Date.now() - state.lastLoaded > REFRESH_MS) loadAll();
    });

    const saved = storageGet("lastPlace");
    const valid = saved && Number.isFinite(saved.lat) && Number.isFinite(saved.lon) && saved.name;
    setPlace(valid ? saved : { ...QUICK_PLACES[0], admin: "ประเทศไทย" });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
