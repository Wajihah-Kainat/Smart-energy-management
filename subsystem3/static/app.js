const $ = (id) => document.getElementById(id);
const today = new Date();
const isoToday = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
const monthToday = isoToday.slice(0,7);
document.querySelector('[name="reading_date"]').value = isoToday;
document.querySelector('[name="date"]').value = isoToday;
document.querySelector('[name="month"]').value = monthToday;

function formObject(form) {
  const obj = {};
  new FormData(form).forEach((v,k) => { obj[k] = v; });
  form.querySelectorAll('input[type="number"]').forEach(i => { if(i.value !== '') obj[i.name] = Number(i.value); });
  const simulated = form.querySelector('[name="is_simulated"]');
  if (simulated) obj.is_simulated = simulated.checked;
  return obj;
}
async function api(url, options={}) {
  const response = await fetch(url, {headers:{'Content-Type':'application/json','X-User-ID':'1',...(options.headers||{})},...options});
  const data = await response.json().catch(()=>({error:'Unexpected server response'}));
  if(!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
function showMessage(text, error=false) {
  const el = $('analytics-message'); el.textContent = text; el.classList.toggle('error', error);
}
async function handleForm(id, urlBuilder, success) {
  $(id).addEventListener('submit', async e => {
    e.preventDefault();
    try { const data=formObject(e.currentTarget); const result=await api(urlBuilder(data),{method:'PUT',body:JSON.stringify(data)}); showMessage(success); console.log(result); }
    catch(err){showMessage(err.message,true);}
  });
}
handleForm('settings-form', d=>`/api/v1/s3/settings/${d.building_id}`, 'Settings saved.');
handleForm('goal-form', d=>`/api/v1/s3/goals/${d.building_id}`, 'Monthly goal saved.');
$('reading-form').addEventListener('submit', async e=>{
  e.preventDefault(); const d=formObject(e.currentTarget);
  try { await api('/api/v1/s3/readings',{method:'POST',body:JSON.stringify(d)}); showMessage('Reading saved.'); }
  catch(err){showMessage(err.message,true);}
});
$('analytics-form').addEventListener('submit', async e=>{
  e.preventDefault(); const d=formObject(e.currentTarget);
  try {
    const a=await api(`/api/v1/s3/analytics/${d.building_id}?period=month&date=${d.date}`);
    $('kpi-energy').textContent=`${a.energy_kwh} kWh`;
    $('kpi-cost').textContent=`€${a.cost.toFixed(2)}`;
    $('kpi-carbon').textContent=`${a.carbon_kg.toFixed(2)} kg`;
    const month=d.date.slice(0,7);
    try { const s=await api(`/api/v1/s3/score/${d.building_id}?month=${month}`); $('kpi-score').textContent=`${s.score}/100`; }
    catch { $('kpi-score').textContent='Set a goal'; }
    showMessage(`Analytics loaded for ${a.start_date}. Factor source: ${a.factor_source}`);
  } catch(err){showMessage(err.message,true);}
});
$('load-alerts').addEventListener('click', async()=>{
  const building=document.querySelector('#analytics-form [name="building_id"]').value;
  try {
    const result=await api(`/api/v1/s3/alerts?building_id=${building}`);
    const host=$('alerts'); host.replaceChildren();
    if(!result.alerts.length){host.textContent='No alerts found.';return;}
    result.alerts.forEach(a=>{
      const item=document.createElement('div');item.className='alert';
      const body=document.createElement('div');const p=document.createElement('p');p.textContent=a.message;
      const small=document.createElement('small');small.textContent=`${a.created_at} · ${a.is_read?'Read':'Unread'}`;body.append(p,small);
      const controls=document.createElement('div');
      const read=document.createElement('button');read.className='secondary';read.textContent='Mark read';read.disabled=Boolean(a.is_read);
      read.onclick=async()=>{await api(`/api/v1/s3/alerts/${a.id}/read`,{method:'PATCH'});$('load-alerts').click();};
      const del=document.createElement('button');del.className='secondary';del.textContent='Delete';del.onclick=async()=>{await api(`/api/v1/s3/alerts/${a.id}`,{method:'DELETE'});$('load-alerts').click();};
      controls.append(read,del);item.append(body,controls);host.append(item);
    });
  } catch(err){showMessage(err.message,true);}
});
$('evaluate-alert').addEventListener('click',async()=>{
  const building=document.querySelector('#analytics-form [name="building_id"]').value;
  const selected=document.querySelector('#analytics-form [name="date"]').value;
  try{const r=await api(`/api/v1/s3/evaluate-alert/${building}?date=${selected}`,{method:'POST'});showMessage(r.alert_created?'Daily limit exceeded: alert created.':`No new alert. Daily use: ${r.daily_kwh} kWh.`);$('load-alerts').click();}
  catch(err){showMessage(err.message,true);}
});
