// Subsystem 3 page: talks to the JSON API (/api/v1/s3/...). The login cookie identifies the user.
const $ = (id) => document.getElementById(id);
const building = window.S3_BUILDING;

function formObject(form) {
  const obj = {};
  new FormData(form).forEach((v, k) => { obj[k] = v; });
  form.querySelectorAll('input[type="number"]').forEach(i => { if (i.value !== '') obj[i.name] = Number(i.value); });
  return obj;
}
async function api(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json().catch(() => ({ error: 'Unexpected server response' }));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
function showMessage(text, error = false) {
  const el = $('analytics-message'); if (!el) return;
  el.textContent = text; el.classList.toggle('error', error);
}
function handleForm(id, url, success) {
  const form = $(id); if (!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    try {
      const data = formObject(form);
      await api(url(data), { method: 'PUT', body: JSON.stringify(data) });
      showMessage(success);
      loadAnalytics();
    } catch (err) { showMessage(err.message, true); }
  });
}
handleForm('settings-form', d => `/api/v1/s3/settings/${d.building_id}`, 'Settings saved.');
handleForm('goal-form', d => `/api/v1/s3/goals/${d.building_id}`, 'Monthly goal saved.');

async function loadAnalytics() {
  const form = $('analytics-form'); if (!form || !building) return;
  const month = form.querySelector('[name="month"]').value;
  $('kpi-score').textContent = '—'; $('goal-box').textContent = ''; $('goal-bar').hidden = true;
  try {
    const a = await api(`/api/v1/s3/analytics/${building}?period=month&date=${month}-01`);
    $('kpi-energy').textContent = `${a.energy_kwh} kWh`;
    $('kpi-cost').textContent = `€${a.cost.toFixed(2)}`;
    $('kpi-carbon').textContent = `${a.carbon_kg.toFixed(2)} kg`;
    showMessage(`Analytics for ${month}. Factor source: ${a.factor_source}`);
    try {
      const g = await api(`/api/v1/s3/goals/${building}/progress?month=${month}`);
      $('goal-box').textContent = `Goal: ${g.consumed_kwh} of ${g.target_kwh} kWh used (${g.progress_percent}%), ${g.remaining_kwh} kWh left.`;
      $('goal-bar').hidden = false;
      $('goal-bar').firstElementChild.style.width = Math.min(100, g.progress_percent) + '%';
      const s = await api(`/api/v1/s3/score/${building}?month=${month}`);
      $('kpi-score').textContent = `${s.score}/100`;
    } catch { $('kpi-score').textContent = 'Set a goal'; }
  } catch (err) {
    $('kpi-energy').textContent = $('kpi-cost').textContent = $('kpi-carbon').textContent = '—';
    showMessage(err.message, true);
  }
}
if ($('analytics-form')) {
  $('analytics-form').addEventListener('submit', e => { e.preventDefault(); loadAnalytics(); });
}

async function loadAlerts() {
  const host = $('alerts'); if (!host || !building) return;
  const result = await api(`/api/v1/s3/alerts?building_id=${building}`);
  host.replaceChildren();
  if (!result.alerts.length) { host.textContent = 'No alerts found.'; host.className = 'muted'; return; }
  host.className = '';
  result.alerts.forEach(a => {
    const item = document.createElement('div'); item.className = 'alert-item';
    const body = document.createElement('div');
    const p = document.createElement('div'); p.textContent = a.message;
    const small = document.createElement('small'); small.textContent = `${a.created_at} · ${a.is_read ? 'Read' : 'Unread'}`;
    body.append(p, small);
    const controls = document.createElement('div'); controls.className = 'row-actions';
    const read = document.createElement('button'); read.className = 'btn sec small'; read.textContent = 'Mark read'; read.disabled = Boolean(a.is_read);
    read.onclick = async () => { await api(`/api/v1/s3/alerts/${a.id}/read`, { method: 'PATCH' }); loadAlerts(); };
    const del = document.createElement('button'); del.className = 'btn danger small'; del.textContent = 'Delete';
    del.onclick = async () => { await api(`/api/v1/s3/alerts/${a.id}`, { method: 'DELETE' }); loadAlerts(); };
    controls.append(read, del); item.append(body, controls); host.append(item);
  });
}
if ($('evaluate-alert')) {
  $('evaluate-alert').addEventListener('click', async () => {
    try {
      const day = $('alert-date').value;
      const r = await api(`/api/v1/s3/evaluate-alert/${building}?date=${day}`, { method: 'POST' });
      showMessage(r.alert_created ? 'Daily limit exceeded: alert created.' : `No new alert. Use on that day: ${r.daily_kwh} kWh (limit ${r.daily_limit_kwh} kWh).`);
      loadAlerts();
    } catch (err) { showMessage(err.message, true); }
  });
}
loadAnalytics();
loadAlerts().catch(() => {});
