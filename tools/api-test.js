const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert/strict');

const PORT = 8790 + Math.floor(Math.random() * 100);
const DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'dispron-test-'));
const B = `http://127.0.0.1:${PORT}`;
const srv = spawn(process.execPath, [path.join(__dirname, '..', 'server', 'index.js')], { env: { ...process.env, PORT: String(PORT), DATA_DIR }, stdio: ['ignore', 'pipe', 'inherit'] });

const jar = {};
async function req(who, p, opt = {}) {
  const headers = { ...(opt.body ? { 'Content-Type': 'application/json' } : {}), ...(jar[who] ? { Cookie: jar[who] } : {}) };
  const r = await fetch(B + p, { method: opt.method || (opt.body ? 'POST' : 'GET'), headers, body: opt.body && JSON.stringify(opt.body), redirect: 'manual' });
  const sc = r.headers.get('set-cookie'); if (sc) jar[who] = sc.split(';')[0];
  const t = await r.text(); let j = null; try { j = JSON.parse(t); } catch { /* not json */ }
  return { s: r.status, h: r.headers, t, j };
}
let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; console.log('  ✓ ' + m); };

async function main() {
  for (let i = 0; i < 50; i++) { try { await fetch(B + '/robots.txt'); break; } catch { await new Promise(r => setTimeout(r, 100)); } }
  const pages = ['/', '/servicios/', '/servicios/ingenieria-electrica/', '/proyectos/', '/sectores/', '/sectores/bancario/', '/blog/', '/recursos/', '/cotizar/', '/acceso/', '/contacto/', '/sitemap.xml', '/robots.txt', '/llms.txt', '/llms-full.txt', '/knowledge.json', '/.well-known/ai-plugin-info.json'];
  for (const p of pages) { const r = await req('anon', p); ok(r.s === 200, `GET ${p} → 200`); }
  const home = await req('anon', '/');
  ok(/script-src 'self'/.test(home.h.get('content-security-policy')) && home.h.get('x-content-type-options') === 'nosniff', 'Cabeceras de seguridad (CSP, nosniff)');
  ok(!home.h.get('x-powered-by'), 'Sin X-Powered-By');
  ok((await req('anon', '/blog')).s === 301, '/blog redirige a /blog/');
  ok((await req('anon', '/auth')).h.get('location') === '/acceso/', '/auth → /acceso/');
  ok((await req('anon', '/no-existe/')).s === 404, '404 personalizado');
  ok((await req('anon', '/_headers')).s === 404 && (await req('anon', '/.htaccess')).s === 404, 'Archivos de hosting no expuestos');
  ok((await req('anon', '/crm/')).h.get('location') === '/acceso/', 'CRM sin sesión → /acceso/');
  ok((await req('anon', '/api/leads')).s === 401, 'GET /api/leads exige sesión');
  ok((await req('anon', '/api/alfred/meta')).s === 401, 'Alfred exige sesión');
  ok((await req('anon', '/api/leads', { body: { name: 'X' } })).s === 400, 'Lead sin contacto → 400');
  const hp = await req('anon', '/api/leads', { body: { name: 'Bot', phone: '60000000', website: 'spam' } });
  ok(hp.s === 200, 'Honeypot aceptado sin registrar');
  const l1 = await req('anon', '/api/leads', { body: { name: 'Ana Pérez', company: 'Hotel Central', phone: '+507 6123-4567', sector: 'Hotelero', service: 'HVAC y Aire Acondicionado', province: 'Panamá', urgency: 'Prioritaria', description: 'Mantenimiento de chillers' } });
  ok(l1.j && /^DSP-[0-9A-F]{6}$/.test(l1.j.ref), 'Cotizador crea lead con referencia ' + (l1.j && l1.j.ref));
  const l2 = await req('anon', '/api/sofia/lead', { body: { name: 'Luis', email: 'luis@example.com', sector: 'Bancario', service: 'Ingeniería Eléctrica', urgency: 'Crítica' } });
  ok(l2.j && l2.j.ok, 'Sofía crea lead');
  const a = await req('admin', '/api/auth/register', { body: { name: 'Admin', email: 'admin@example.com', password: 'clave-segura-123' } });
  ok(a.j.role === 'admin' && a.j.status === 'activo' && /HttpOnly/i.test(a.h.get('set-cookie')), 'Primer usuario = admin activo con cookie HttpOnly');
  ok((await req('ventas', '/api/auth/register', { body: { name: 'Vendedor', email: 'v@example.com', password: 'clave-segura-456' } })).j.status === 'pendiente', 'Segundo usuario queda pendiente');
  ok((await req('ventas', '/api/auth/login', { body: { email: 'v@example.com', password: 'clave-segura-456' } })).s === 403, 'Usuario pendiente no puede entrar');
  ok((await req('x', '/api/auth/login', { body: { email: 'admin@example.com', password: 'mala' } })).s === 401, 'Contraseña incorrecta → 401');
  ok((await req('admin', '/crm/')).s === 200, 'CRM con sesión → 200');
  const L = await req('admin', '/api/leads');
  ok(L.j.leads.length === 2 && L.j.stages.length === 6, 'Pipeline con 2 leads y 6 etapas');
  const lid = L.j.leads.find(l => l.name === 'Ana Pérez').id;
  const up = await req('admin', '/api/leads/' + lid, { method: 'PATCH', body: { stage: 'Cotización enviada', value: 12500, note: 'Visita realizada' } });
  ok(up.j.stage === 'Cotización enviada' && up.j.value === 12500 && up.j.notes.length === 1, 'Mover etapa, valor y nota');
  const csv = await req('admin', '/api/leads.csv');
  ok(csv.s === 200 && csv.t.includes('Ana Pérez') && /text\/csv/.test(csv.h.get('content-type')), 'Exportación CSV');
  const users = await req('admin', '/api/users');
  const vid = users.j.find(u => u.email === 'v@example.com').id;
  ok((await req('admin', '/api/users/' + vid, { method: 'PATCH', body: { status: 'activo' } })).j.ok, 'Admin aprueba usuario');
  ok((await req('ventas', '/api/auth/login', { body: { email: 'v@example.com', password: 'clave-segura-456' } })).s === 200, 'Usuario aprobado inicia sesión');
  ok((await req('ventas', '/api/leads/' + lid, { method: 'DELETE' })).s === 403, 'Ventas no puede borrar leads');
  ok((await req('ventas', '/api/users')).s === 403, 'Ventas no gestiona usuarios');
  const meta = await req('admin', '/api/alfred/meta');
  ok(meta.j.agents.length === 12 && meta.j.tools.length > 20, `Alfred: ${meta.j.agents.length} agentes, ${meta.j.tools.length} herramientas`);
  const sc = await req('admin', '/api/alfred/scores');
  ok(Object.keys(sc.j).length === 2, 'Alfred puntúa leads');
  for (const t of ['lead_scoring', 'pipeline_report', 'seo_audit', 'site_health', 'geo_ranking_plan', 'jsonld_preview', 'security_audit', 'faq_search', 'campaign_brief', 'prospecting_plan', 'architecture_map', 'visit_checklist']) {
    const r = await req('admin', '/api/alfred/tool', { body: { tool: t, params: { query: t === 'jsonld_preview' ? '/servicios/ingenieria-electrica/' : 'hotel aire acondicionado' } } });
    ok(r.s === 200 && r.j && r.j.status !== 'ERROR', `Alfred ${t}: ${r.j && r.j.status} ${(r.j && r.j.text || '').split('\n')[0].slice(0, 90)}`);
  }
  const allTools = (await req('admin', '/api/alfred/meta')).j.tools;
  const anyLead = (await req('admin', '/api/leads')).j;
  const leadId = (Array.isArray(anyLead) ? anyLead : anyLead.leads || [])[0]?.id;
  const failed = [];
  for (const t of allTools) {
    const r = await req('admin', '/api/alfred/tool', { body: { tool: t.id, confirmed: true, params: { query: 'hotel aire acondicionado', leadId, stage: 'En negociación', text: 'Nota de prueba', subject: 'Prueba', note: 'Nota de prueba' } } });
    if (r.s !== 200 || !r.j || r.j.status === 'ERROR') failed.push(t.id + ':' + (r.j && r.j.text));
  }
  ok(allTools.length === 30 && failed.length === 0, `Alfred: las 30 habilidades se ejecutan sin error ${failed.join(' | ')}`);
  const gd = await req('admin', '/api/alfred/guide');
  ok(gd.s === 200 && gd.j.sections.length >= 8 && gd.j.file, 'Alfred: guía de la plataforma disponible');
  const px = await fetch(B + gd.j.file, { headers: { Cookie: jar.admin } });
  ok(px.status === 200 && (await px.arrayBuffer()).byteLength > 100000, 'Alfred: presentación PPTX descargable');
  ok((await req('anon', '/api/alfred/guide')).s === 401, 'Guía de Alfred exige sesión');
  const enr = await req('admin', '/api/alfred/chat', { body: { message: 'Please show me the pipeline report' } });
  ok(enr.j.lang === 'en' && enr.j.tool === 'pipeline_report' && /^Understood/.test(enr.j.reply), 'Alfred responde en inglés');
  const enc = await req('admin', '/api/alfred/chat', { body: { message: 'Please move the lead to negotiation stage' } });
  ok(enc.j.confirm && enc.j.confirm.en && /express confirmation/.test(enc.j.reply), 'Alfred en inglés exige confirmación MEDIUM');
  const ch = await req('admin', '/api/alfred/chat', { body: { message: 'reporte del pipeline' } });
  ok(ch.s === 200 && ch.j.reply, 'Alfred chat responde');
  const del = await req('admin', '/api/alfred/tool', { body: { tool: 'backup_db', params: {} } });
  ok(del.j.status === 'CONFIRM' || /confirm/i.test(JSON.stringify(del.j)), 'Operación MEDIUM exige confirmación');
  ok((await req('admin', '/api/leads/' + lid, { method: 'DELETE' })).j.ok, 'Admin borra lead');
  ok((await req('admin', '/api/auth/logout', { body: {} })).j.ok && (await req('admin', '/api/leads')).s === 401, 'Logout invalida sesión');
  console.log(`\n${n} pruebas OK`);
}
main().catch(e => { console.error('FALLO:', e.message); process.exitCode = 1; }).finally(() => { srv.kill(); fs.rmSync(DATA_DIR, { recursive: true, force: true }); });
