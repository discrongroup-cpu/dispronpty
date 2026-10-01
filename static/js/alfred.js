// ALFRED dentro del CRM: HUD + chat con 12 sub-agentes + habilidades + políticas + memoria. Cargado por crm.js al existir sesión activa.
window.AlfredHUD = (function () {
  const E = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let meta = null, guide = null, root, tab = 'chat', busy = false, hist = [], sel = null, rec = null;
  const api = async (u, o) => { const r = await fetch(u, o); const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.error || j.reply || 'Error'); return j; };
  const post = (u, b) => api(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) });
  const hour = () => { const h = new Date().getHours(); return h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches'; };
  const CHIPS = ['Reporte del pipeline', 'Califica mis leads', '¿Cuál es la próxima mejor acción?', 'Plan para buscar más clientes', 'Auditoría SEO y GEO del sitio', '¿Cómo llegamos al primer lugar?', 'Salud del sitio', 'Auditoría de seguridad', 'Checklist de lanzamiento', 'Show me the pipeline report', 'Introduce DISPRON in English'];

  function speak(t) { try { if (!speechSynthesis) return; const u = new SpeechSynthesisUtterance(t.replace(/```[\s\S]*?```/g, '').slice(0, 400)); u.lang = 'es-PA'; const v = speechSynthesis.getVoices().find(x => /^es/i.test(x.lang) && /male|hombre|jorge|diego|pablo|raul|alvaro/i.test(x.name)) || speechSynthesis.getVoices().find(x => /^es/i.test(x.lang)); if (v) u.voice = v; speechSynthesis.speak(u); } catch (e) { } }

  function mount() {
    if (root) return;
    const fab = document.createElement('button'); fab.className = 'alf-fab'; fab.id = 'alf-open'; fab.innerHTML = '<i class="alf-dot"></i>Alfred'; fab.setAttribute('aria-haspopup', 'dialog'); fab.onclick = open; document.body.appendChild(fab);
    root = document.createElement('div'); root.className = 'alf'; root.hidden = true; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', 'Alfred, mayordomo de DISPRON GROUP'); document.body.appendChild(root);
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !root.hidden) close(); });
  }
  async function open() { mount(); root.hidden = false; document.body.style.overflow = 'hidden'; if (!meta) { try { meta = await api('/api/alfred/meta'); } catch (e) { root.innerHTML = '<p style="padding:2rem">' + E(e.message) + '</p>'; return; } greet(); } else refresh(); render(); }
  function close() { root.hidden = true; document.body.style.overflow = ''; document.getElementById('alf-open').focus(); }
  function greet() { hist = [{ r: 'b', t: `${hour()}, Jefe Maestro. Alfred a su servicio en DISPRON GROUP.\nTengo 12 especialistas y ${meta.tools.length} habilidades conectadas a su CRM y a su sitio. Todo lo que ejecuto es real; si algo requiere datos que no existen, se lo digo.`, agent: null }]; }
  async function refresh() { try { meta = await api('/api/alfred/meta'); } catch (e) { } }

  function render() {
    const tabs = [['chat', 'Consola'], ['skills', 'Habilidades'], ['agents', 'Sub-agentes'], ['policies', 'Políticas'], ['memory', 'Memoria y registro'], ['guide', 'Guía de la plataforma']];
    root.innerHTML = `<div class="alf-hd"><img src="/img/logo-dispron-horizontal.png" alt="DISPRON GROUP"><div class="alf-t">ALFRED<small>CENTRO DE MANDO COMERCIAL · DISPRON</small></div><nav class="alf-tabs" role="tablist">${tabs.map(([k, l]) => `<button role="tab" aria-selected="${tab === k}" data-t="${k}">${l}</button>`).join('')}</nav><span class="alf-sp"></span><button id="alf-x" aria-label="Cerrar Alfred">Cerrar ✕</button></div><div class="alf-body" id="alf-b"></div>`;
    root.querySelectorAll('[data-t]').forEach(b => b.onclick = () => { tab = b.dataset.t; render(); });
    root.querySelector('#alf-x').onclick = close;
    const b = root.querySelector('#alf-b');
    if (tab === 'chat') chatView(b); else if (tab === 'skills') skillsView(b); else if (tab === 'agents') agentsView(b); else if (tab === 'policies') polView(b); else if (tab === 'guide') guideView(b); else memView(b);
  }

  function side() { return `<aside class="alf-card alf-side" data-sec="SEC-CORE"><div class="core ${busy ? 'busy' : ''}"><span class="ring r3"></span><span class="ring r1"></span><span class="ring r2"></span><b>A</b></div><h3>Sub-agentes</h3><div class="alf-scroll">${meta.agents.map(a => `<button class="ag ${sel === a.id ? 'on' : ''}" style="--c:${a.color}" data-ag="${a.id}"><i></i><span><b>${a.name}</b><small>${E(a.role)}</small></span></button>`).join('')}</div></aside>`; }
  function side2() { const used = {}; meta.log.forEach(l => used[l.agent] = (used[l.agent] || 0) + 1); return `<aside class="alf-card alf-side" data-sec="SEC-TELEMETRY"><h3>Telemetría</h3><div class="kv"><span>Habilidades</span><span>${meta.tools.length}</span><span>Sub-agentes</span><span>12</span><span>Ejecuciones</span><span>${meta.log.length}</span><span>Memoria</span><span>${meta.memory.length} hechos</span><span>Tickets</span><span>${meta.tickets.length}</span></div><h3 style="margin-top:1rem">Última actividad</h3><div class="alf-scroll">${meta.log.slice(0, 10).map(l => `<div style="font-size:.74rem;margin:.3rem 0;color:#8aa0b8"><b style="color:#e8d9b5">${E(l.agent)}</b> · ${E(l.tool)}<br>${new Date(l.at).toLocaleTimeString('es-PA')} · ${l.ms} ms · ${E(l.status || '')}</div>`).join('') || '<small style="color:#8aa0b8">Sin ejecuciones aún.</small>'}</div></aside>`; }

  function chatView(b) {
    b.innerHTML = side() + `<section class="alf-card" data-sec="SEC-CONSOLE"><h3>Consola de comando${sel ? ' · ' + E(meta.agents.find(a => a.id === sel).name) : ''}</h3><div class="alf-log" id="alf-log" role="log" aria-live="polite"></div><div class="alf-chips" id="alf-chips">${CHIPS.map(c => `<button>${E(c)}</button>`).join('')}</div><form class="alf-in" id="alf-f"><label class="sr" for="alf-i" style="position:absolute;left:-9999px">Mensaje para Alfred</label><input id="alf-i" autocomplete="off" maxlength="800" placeholder="Ordene a Alfred: «califica mis leads», «propuesta para Laura»…"><button type="button" class="mic" id="alf-mic" aria-label="Dictar con micrófono">MIC</button><button>Enviar</button></form></section>` + side2();
    const log = b.querySelector('#alf-log'); const draw = () => { log.innerHTML = hist.map((m, i) => msgHtml(m, i)).join(''); log.scrollTop = log.scrollHeight; log.querySelectorAll('[data-cf]').forEach(btn => btn.onclick = () => confirmRun(+btn.dataset.cf, btn.dataset.ok === '1')); }; draw();
    b.querySelectorAll('[data-ag]').forEach(x => x.onclick = () => { sel = sel === x.dataset.ag ? null : x.dataset.ag; const a = meta.agents.find(y => y.id === sel); if (a) hist.push({ r: 'b', t: `${a.name} — ${a.role}.\n${a.desc}\nHabilidades: ${meta.tools.filter(t => t.agentId === a.id).map(t => t.name).join('; ')}.`, agent: a.name }); render(); });
    b.querySelectorAll('#alf-chips button').forEach(x => x.onclick = () => send(x.textContent));
    b.querySelector('#alf-f').onsubmit = e => { e.preventDefault(); const i = b.querySelector('#alf-i'); const v = i.value; i.value = ''; send(v); };
    b.querySelector('#alf-mic').onclick = () => mic(b);
    b.querySelector('#alf-i').focus();
    window.__alfDraw = draw;
  }
  function msgHtml(m, i) {
    if (m.r === 'u') return `<div class="am u">${E(m.t)}</div>`;
    let t = E(m.t).replace(/```mermaid\n([\s\S]*?)```/g, '<pre>$1</pre>'); const tag = m.agent ? `<span class="tag">${E(m.agent.toUpperCase())}${m.toolName ? ' · ' + E(m.toolName) : ''}${m.ms != null ? ' · ' + m.ms + 'ms' : ''}</span><br>` : '<span class="tag g">ALFRED</span><br>';
    return `<div class="am">${tag}${t}${m.confirm && !m.done ? `<div class="cf"><button data-cf="${i}" data-ok="1">Confirmar, ejecutar</button><button class="n" data-cf="${i}" data-ok="0">Cancelar</button></div>` : ''}</div>`;
  }
  async function send(text, confirm) {
    text = String(text || '').trim(); if (!text && !confirm || busy) return; if (!confirm) hist.push({ r: 'u', t: text }); busy = true; render();
    try { const j = await post('/api/alfred/chat', { message: text, confirm }); hist.push({ r: 'b', t: j.reply, agent: j.agent, toolName: j.toolName, ms: j.ms, confirm: j.confirm }); speakMaybe(j.reply); await refresh(); }
    catch (e) { hist.push({ r: 'b', t: 'No pude completar la orden: ' + e.message }); }
    busy = false; render();
  }
  function confirmRun(i, ok) { const m = hist[i]; m.done = true; if (!ok) { hist.push({ r: 'b', t: 'Cancelado, Jefe Maestro. No se modificó nada.' }); render(); return; } send('', m.confirm); }
  function speakMaybe(t) { if (localStorage.getItem('alf-voice') === '1') speak(t); }
  function mic(b) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition; const btn = b.querySelector('#alf-mic'); const i = b.querySelector('#alf-i');
    if (!SR) { hist.push({ r: 'b', t: 'Este navegador no soporta dictado por voz. Use Chrome o Edge.' }); render(); return; }
    if (rec) { rec.stop(); rec = null; btn.classList.remove('on'); return; }
    rec = new SR(); rec.lang = 'es-PA'; rec.interimResults = true; btn.classList.add('on'); localStorage.setItem('alf-voice', '1');
    rec.onresult = e => { i.value = [...e.results].map(r => r[0].transcript).join(''); if (e.results[e.results.length - 1].isFinal) { const v = i.value; i.value = ''; rec.stop(); rec = null; send(v); } };
    rec.onerror = () => { rec = null; btn.classList.remove('on'); }; rec.onend = () => { rec = null; btn.classList && btn.classList.remove('on'); }; rec.start();
  }

  function skillsView(b) {
    b.innerHTML = `<section class="alf-card alf-full" data-sec="SEC-SKILLS"><h3>Habilidades de Alfred (${meta.tools.length}) — acciones reales sobre CRM y sitio</h3><div class="grid3">${meta.tools.map(t => `<div class="tool"><span class="risk ${t.risk}">${t.risk}</span> <small style="color:#8aa0b8">${E(t.agent)}</small><h4>${E(t.name)}</h4><p>${E(t.desc)}</p><button data-run="${t.id}">Ejecutar</button></div>`).join('')}</div></section>`;
    b.querySelectorAll('[data-run]').forEach(x => x.onclick = () => { const t = meta.tools.find(y => y.id === x.dataset.run); tab = 'chat'; const prompts = { lead_scoring: 'Califica mis leads', pipeline_report: 'Reporte del pipeline', seo_audit: 'Auditoría SEO y GEO del sitio', geo_ranking_plan: '¿Cómo llegamos al primer lugar?', site_health: 'Salud del sitio', security_audit: 'Auditoría de seguridad', next_best_action: '¿Cuál es la próxima mejor acción?', prospecting_plan: 'Plan para buscar más clientes', launch_checklist: 'Checklist de lanzamiento', backup_db: 'Respaldo de la base de datos', architecture_map: 'Mapa de arquitectura', openapi_spec: 'Genera la spec OpenAPI', deploy_checklist: 'Checklist de despliegue', env_status: 'Estado del entorno', suspicious_leads: 'Detecta leads sospechosos o duplicados', campaign_brief: 'Brief de campaña', bilingual_intro: 'Presentación en inglés', faq_search: 'Busca en las FAQ: ', jsonld_preview: 'Previsualiza el JSON-LD de /' }; render(); const q = prompts[t.id]; if (q && !q.endsWith(': ')) send(q); else { const i = document.getElementById('alf-i'); i.value = q || t.name + ' de '; i.focus(); hist.push({ r: 'b', t: `${t.name}: indique el lead o dato (nombre, empresa o DSP-XXXXXX) y envíe.`, agent: t.agent }); window.__alfDraw && window.__alfDraw(); } });
  }
  function agentsView(b) {
    b.innerHTML = `<section class="alf-card alf-full" data-sec="SEC-AGENTS"><h3>Los 12 sub-agentes de Alfred, adaptados a DISPRON</h3><div class="grid3">${meta.agents.map(a => `<div class="tool" style="border-left:3px solid ${a.color}"><h4 style="color:${a.color}">${a.name}</h4><small style="color:#e8d9b5">${E(a.role)} · ${E(a.category)}</small><p>${E(a.desc)}</p><small style="color:#8aa0b8">${meta.tools.filter(t => t.agentId === a.id).map(t => E(t.name)).join(' · ')}</small></div>`).join('')}</div></section>`;
  }
  function polView(b) { b.innerHTML = `<section class="alf-card alf-full" data-sec="SEC-POLICY"><h3>Políticas y salvaguardas</h3>${meta.policies.map(p => `<div class="pol"><div><b style="color:#fff">${E(p.title)}</b> <small>${E(p.code)}</small><small>${E(p.desc)}</small></div><span class="pa ${p.action}">${p.action.replace('_', ' ')}</span></div>`).join('')}<p style="color:#8aa0b8;font-size:.8rem">Alfred siempre le llama «Jefe Maestro», no usa emojis y nunca afirma haber hecho algo que no ejecutó.</p></section>`; }
  async function guideView(b) {
    if (!guide) { b.innerHTML = '<section class="alf-card alf-full"><p>Cargando guía…</p></section>'; try { guide = await api('/api/alfred/guide'); } catch (e) { b.innerHTML = '<section class="alf-card alf-full"><p>' + E(e.message) + '</p></section>'; return; } if (tab !== 'guide') return; }
    b.innerHTML = `<section class="alf-card alf-full" data-sec="SEC-GUIDE"><div class="guide-hd"><h3>Guía oficial · ALFRED DISPRON, plataforma completa</h3>${guide.file ? `<a class="guide-dl" href="${guide.file}" download>Descargar presentación (PPTX)</a>` : ''}</div><div class="grid3">${guide.sections.map(s => `<div class="tool guide"><h4>${E(s.title)}</h4><ul>${s.items.map(i => `<li>${E(i)}</li>`).join('')}</ul></div>`).join('')}</div></section>`;
  }
  function memView(b) {
    b.innerHTML = `<section class="alf-card" data-sec="SEC-MEMORY"><h3>Memoria de Minerva</h3><div class="alf-scroll">${meta.memory.map(m => `<div class="note" style="background:#0a1a2e;color:#d6e2ef;margin:.3rem 0;padding:.5rem;font-size:.85rem"><small>${m.at.slice(0, 10)}</small><br>${E(m.text)}</div>`).join('') || '<small style="color:#8aa0b8">Vacía. Diga: «recuerda que …».</small>'}</div></section><section class="alf-card" data-sec="SEC-LOG"><h3>Registro de ejecuciones</h3><div class="alf-scroll">${meta.log.map(l => `<div style="font-size:.8rem;margin:.3rem 0;border-bottom:1px solid #12263a;padding-bottom:.3rem"><b style="color:#e8d9b5">${E(l.agent)}</b> · ${E(l.tool)} · ${E(l.status || '')}<br><span style="color:#8aa0b8">${new Date(l.at).toLocaleString('es-PA')} · ${E(l.by)} · ${l.ms} ms</span></div>`).join('') || '<small style="color:#8aa0b8">Sin ejecuciones.</small>'}</div></section><section class="alf-card" data-sec="SEC-TICKETS"><h3>Tickets</h3><div class="alf-scroll">${meta.tickets.map(t => `<div style="font-size:.82rem;margin:.3rem 0"><b style="color:#C5A059">${t.id}</b> ${E(t.text)}</div>`).join('') || '<small style="color:#8aa0b8">Sin tickets.</small>'}</div></section>`;
  }
  return { mount };
})();
