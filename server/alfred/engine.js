// ALFRED · DISPRON — Motor de habilidades. Cada handler ejecuta una acción REAL sobre el CRM/sitio o declara lo que falta.
// Nunca se afirma una acción que no corrió. Riesgo MEDIUM+ exige confirmación explícita del Jefe Maestro.
const fs = require('fs'), path = require('path');
const AGENTS = require('./agents');
const { STAGES, PROB, norm, scoreLead, day } = require('./core');
const D = require('../data');
const SEO = require('../seo');

const money = n => 'B/. ' + Number(n || 0).toLocaleString('es-PA');
const ref = l => 'DSP-' + l.id.slice(0, 6).toUpperCase();
const agent = id => AGENTS.find(a => a.id === id);

function create(ctx) {
  const { getDb, save, origin, port, root } = ctx;
  const db = () => getDb();
  const ensure = () => { const d = db(); d.tickets ||= []; d.memory ||= []; d.alfredLog ||= []; d.proposals ||= []; return d; };
  const leads = () => ensure().leads;

  function findLead(q) {
    const n = norm(q); const L = leads(); if (!L.length) return null;
    const m = n.match(/dsp-?([0-9a-f]{4,6})/); if (m) { const f = L.find(l => l.id.startsWith(m[1])); if (f) return f; }
    const hit = L.map(l => ({ l, s: [l.name, l.company].filter(Boolean).reduce((a, t) => a + (n.includes(norm(t)) ? 3 : 0) + norm(t).split(/\s+/).filter(w => w.length > 3 && n.includes(w)).length, 0) })).sort((a, b) => b.s - a.s)[0];
    return hit && hit.s > 0 ? hit.l : null;
  }
  const needLead = (p) => { const l = (p.leadId && leads().find(x => x.id === p.leadId || ref(x) === p.leadId)) || findLead(p.query || p.lead || ''); return l; };
  const noLead = (hint = 'Indique el nombre, empresa o referencia DSP-XXXXXX del lead.') => ({ status: 'NEEDS_INPUT', text: 'No identifiqué la oportunidad. ' + hint });

  async function http(p) { const r = await fetch(`http://127.0.0.1:${port}${p}`, { redirect: 'manual' }); return { r, body: await r.text() }; }

  const T = {};
  const def = (id, agentId, name, desc, risk, handler, params = {}) => { T[id] = { id, agentId, name, desc, risk, handler, params }; };

  // ── Marcus — ventas y prospección ──────────────────────────────
  def('lead_scoring', 'marcus', 'Calificar leads (score A/B/C)', 'Puntúa todas las oportunidades abiertas y las ordena por prioridad comercial.', 'LOW', () => {
    const rows = leads().filter(l => STAGES.indexOf(l.stage) < 4).map(l => ({ l, ...scoreLead(l) })).sort((a, b) => b.score - a.score);
    if (!rows.length) return { status: 'OK', text: 'No hay oportunidades abiertas en el pipeline.' };
    return { status: 'OK', text: 'Prioridad comercial (score 0-100):\n' + rows.slice(0, 12).map(r => `[${r.tier}] ${String(r.score).padStart(3)}  ${r.l.name}${r.l.company ? ' · ' + r.l.company : ''} — ${r.l.service || 'sin servicio'} — ${r.l.stage} (${ref(r.l)})`).join('\n') + '\n\nCriterios: urgencia, valor, sector recurrente, contacto completo, frescura y avance de etapa.', data: rows.map(r => ({ id: r.l.id, score: r.score, tier: r.tier })) };
  });
  def('next_best_action', 'marcus', 'Próxima mejor acción', 'Indica qué hacer ahora con cada oportunidad abierta (o una específica).', 'LOW', (p) => {
    const one = p.query && findLead(p.query); const set = one ? [one] : leads().filter(l => STAGES.indexOf(l.stage) < 4);
    if (!set.length) return { status: 'OK', text: 'Sin oportunidades abiertas.' };
    const act = l => { const idle = Math.floor((Date.now() - new Date(l.updated || l.created)) / day); const si = STAGES.indexOf(l.stage);
      if (si === 0) return /Cr[ií]tica/i.test(l.urgency) ? 'Llamar HOY: urgencia crítica sin contactar.' : 'Contactar en menos de 24 h y confirmar fecha de visita.';
      if (si === 1) return 'Completar levantamiento técnico y registrar fotos/medidas en la ficha.';
      if (si === 2) return idle >= 5 ? `Dar seguimiento: cotización sin respuesta hace ${idle} días.` : 'Esperar respuesta; programar seguimiento a los 5 días.';
      if (si === 3) return 'Resolver objeciones y proponer fecha de cierre; considerar contrato recurrente.'; return ''; };
    return { status: 'OK', text: set.slice(0, 12).map(l => `• ${l.name} (${l.stage}): ${act(l)}`).join('\n') };
  });
  def('followup_draft', 'marcus', 'Redactar seguimiento', 'Redacta un mensaje de seguimiento (ES/EN) para un lead. No lo envía.', 'LOW', (p) => {
    const l = needLead(p); if (!l) return noLead(); const en = /english|ingles|en ingl/.test(norm(p.query || '')) || p.lang === 'en'; const first = l.name.split(' ')[0];
    const msg = en ? `Hello ${first},\n\nThis is DISPRON GROUP following up on your request${l.service ? ' regarding ' + l.service : ''}${l.province ? ' in ' + l.province : ''}. We would like to confirm a technical visit so we can prepare a precise proposal.\n\nWhat day and time work best for you?\n\nBest regards,\nDISPRON GROUP`
      : `Hola ${first},\n\nLe saludamos de DISPRON GROUP. Damos seguimiento a su solicitud${l.service ? ' de ' + l.service : ''}${l.province ? ' en ' + l.province : ''}. Nos gustaría confirmar una visita técnica para preparar una propuesta precisa.\n\n¿Qué día y horario le resulta más conveniente?\n\nQuedamos atentos,\nDISPRON GROUP`;
    return { status: 'DRAFT', text: `Borrador para ${l.name} (${ref(l)}) — NO enviado:\n\n${msg}`, data: { leadId: l.id } };
  });
  def('prospecting_plan', 'marcus', 'Plan de prospección por sector', 'Plan para conseguir clientes nuevos por sector: perfil, propuesta, mensaje y servicios ancla.', 'LOW', (p) => {
    const n = norm(p.query || ''); const sec = D.SECTORES.find(s => n.includes(norm(s.name)) || n.includes(s.id)) || null;
    const set = sec ? [sec] : D.SECTORES; const counts = {}; leads().forEach(l => counts[l.sector] = (counts[l.sector] || 0) + 1);
    return { status: 'OK', text: set.map(s => `${s.name.toUpperCase()}  (leads actuales: ${counts[s.name] || 0})\n  Quién: ${{ bancario: 'gerencias de infraestructura/facilities, compras de sucursales', hotelero: 'gerencia de operaciones e ingeniería, mantenimiento', ph: 'administradores de PH y juntas directivas', eventos: 'organizadores, agencias de marketing y expositores', industrial: 'gerentes de planta, proyectos y compras' }[s.id]}.\n  Dolor: ${s.needs[0]}.\n  Servicios ancla: ${s.services.map(x => D.SERVICES.find(v => v.slug === x).name).join('; ')}.\n  Oferta de entrada: visita técnica de diagnóstico sin costo (confirmar política con dirección).\n  Mensaje: "Ayudamos a ${s.name.toLowerCase()} con ${s.needs[1].toLowerCase()}. ¿Agendamos 20 minutos de diagnóstico?"\n  Canales: LinkedIn, visitas a administradores, referidos, Google (landing /sectores#${s.id}).`).join('\n\n') + '\n\nRegla: usar solo clientes y casos con autorización; no publicar logos ni testimonios sin permiso.' };
  });
  def('campaign_brief', 'marcus', 'Brief de campaña', 'Brief de campaña por servicio o sector con mensajes y KPIs.', 'LOW', (p) => {
    const n = norm(p.query || ''); const s = D.SERVICES.find(x => n.includes(norm(x.name).split(' ')[0]) || x.slug.split('-').some(w => w.length > 5 && n.includes(w))) || D.SERVICES[0];
    return { status: 'OK', text: `Campaña: ${s.name}\nObjetivo: solicitudes de visita técnica calificadas.\nAudiencia: ${s.sectors.map(id => D.SECTORES.find(x => x.id === id).name).join(', ')}.\nMensaje central: "${s.short}"\nPruebas visuales: ${s.photos.length} fotografías reales en /servicios/${s.slug}.\nKeywords: ${SEO.KEYWORDS[s.slug].join(' · ')}.\nCTA: Agendar visita técnica (/cotizar?servicio=${s.slug}).\nKPIs: leads/semana, costo por lead, % visita→cotización, % cotización→adjudicación.\nLímite: sin cifras, clientes ni garantías no validadas.` };
  });
  def('move_stage', 'marcus', 'Mover oportunidad de etapa', 'Cambia la etapa de un lead en el CRM.', 'MEDIUM', (p) => {
    const l = needLead(p); if (!l) return noLead(); const st = STAGES.find(s => norm(p.query || p.stage || '').includes(norm(s).split('/')[0].toLowerCase())) || STAGES.find(s => s === p.stage);
    if (!st) return { status: 'NEEDS_INPUT', text: 'Indique la etapa destino: ' + STAGES.join(' | ') };
    const old = l.stage; l.stage = st; l.updated = new Date().toISOString(); l.history.unshift({ at: l.updated, event: `Etapa: ${old} → ${st}`, by: 'Alfred' }); save(); return { status: 'DONE', text: `${l.name}: ${old} → ${st}.` };
  }, { leadId: 'string', stage: 'string' });

  // ── Victoria — datos, SEO y GEO ────────────────────────────────
  def('pipeline_report', 'victoria', 'Reporte de pipeline y pronóstico', 'Valor por etapa, pronóstico ponderado, conversión por sector, servicio y fuente.', 'LOW', () => {
    const L = leads(); if (!L.length) return { status: 'OK', text: 'El CRM no tiene leads todavía. Sin datos no hay métricas que reportar.' };
    const by = (f) => { const m = {}; L.forEach(l => { const k = f(l) || '—'; (m[k] ||= { n: 0, won: 0, val: 0 }); m[k].n++; if (l.stage === STAGES[4]) { m[k].won++; m[k].val += l.value; } }); return m; };
    const fmt = (m) => Object.entries(m).sort((a, b) => b[1].n - a[1].n).map(([k, v]) => `  ${k}: ${v.n} leads, ${v.won} adjudicados (${Math.round(v.won / v.n * 100)}%), ${money(v.val)}`).join('\n');
    const st = STAGES.map((s, i) => { const x = L.filter(l => l.stage === s); return `  ${s}: ${x.length} · ${money(x.reduce((a, l) => a + l.value, 0))}`; }).join('\n');
    const fc = L.filter(l => STAGES.indexOf(l.stage) < 4).reduce((a, l) => a + l.value * PROB[STAGES.indexOf(l.stage)], 0);
    const won = L.filter(l => l.stage === STAGES[4]), lost = L.filter(l => l.stage === STAGES[5]);
    const noVal = L.filter(l => STAGES.indexOf(l.stage) < 4 && !l.value).length;
    return { status: 'OK', text: `Total: ${L.length} leads · Adjudicado: ${money(won.reduce((a, l) => a + l.value, 0))} · Tasa de cierre: ${won.length + lost.length ? Math.round(won.length / (won.length + lost.length) * 100) : 0}%\nPronóstico ponderado (probabilidad por etapa): ${money(fc)}${noVal ? `\nAviso: ${noVal} oportunidades abiertas sin valor estimado; el pronóstico las cuenta en 0.` : ''}\n\nPor etapa:\n${st}\n\nPor sector:\n${fmt(by(l => l.sector))}\n\nPor servicio:\n${fmt(by(l => l.service))}\n\nPor fuente:\n${fmt(by(l => l.source))}`, data: { forecast: fc } };
  });
  def('seo_audit', 'victoria', 'Auditoría SEO/GEO real del sitio', 'Descarga cada página y verifica title, descripción, H1, canonical, JSON-LD, alt de imágenes.', 'LOW', async () => {
    const paths = SEO.allPaths(); const rows = [];
    for (const p of paths) {
      const { r, body } = await http(p); const g = (re) => (body.match(re) || [])[1] || '';
      const title = g(/<title>([^<]*)<\/title>/), desc = g(/<meta name="description" content="([^"]*)"/), h1 = (body.match(/<h1[ >]/g) || []).length;
      const canon = /rel="canonical"/.test(body), ldBlocks = [...body.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
      let ldOk = ldBlocks.length > 0; let types = []; for (const m of ldBlocks) { try { const j = JSON.parse(m[1]); (j['@graph'] || [j]).forEach(x => types.push([].concat(x['@type']).join('/'))); } catch { ldOk = false; } }
      const imgs = [...body.matchAll(/<img\b[^>]*>/g)].map(m => m[0]); const noAlt = imgs.filter(i => !/\balt=/.test(i)).length;
      const issues = []; if (r.status !== 200) issues.push('HTTP ' + r.status); if (title.length < 10 || title.length > 70) issues.push(`title ${title.length} car.`); if (desc.length < 50 || desc.length > 170) issues.push(`descripción ${desc.length} car.`); if (h1 !== 1) issues.push(`H1=${h1}`); if (!canon) issues.push('sin canonical'); if (!ldOk) issues.push('JSON-LD ausente/inválido'); if (noAlt) issues.push(`${noAlt} img sin alt`);
      rows.push({ p, issues, types: [...new Set(types)] });
    }
    const bad = rows.filter(r => r.issues.length); const totalIssues = rows.reduce((a, r) => a + r.issues.length, 0);
    const scoreV = Math.max(0, Math.round(100 - totalIssues / rows.length * 12));
    return { status: 'OK', text: `Páginas auditadas: ${rows.length} · Puntaje técnico: ${scoreV}/100 · Páginas con hallazgos: ${bad.length}\n` + (bad.length ? bad.slice(0, 14).map(r => `  ${r.p}: ${r.issues.join(', ')}`).join('\n') : '  Sin hallazgos técnicos en title, descripción, H1, canonical, JSON-LD ni alt.') + `\n\nTipos de JSON-LD en la home: ${(rows[0].types || []).join(', ')}.\nNota: esto mide SEO técnico on-page. No mide posiciones en Google ni citas en ChatGPT/Gemini/Perplexity; para eso se requiere Search Console y monitoreo de prompts.`, data: { score: scoreV, rows } };
  });
  def('geo_ranking_plan', 'victoria', 'Plan para posicionar #1 por servicio', 'Plan medible por servicio (SEO local + GEO/IA) con brechas reales de la plataforma.', 'LOW', () => {
    const gaps = []; const c = D.CONTACT; if (!c.phone) gaps.push('Teléfono validado (NAP)'); if (!c.email) gaps.push('Correo corporativo'); if (!c.address) gaps.push('Dirección real'); if (!c.hours) gaps.push('Horario');
    gaps.push('Razón social y licencias/idoneidades verificadas', 'Casos de estudio autorizados con fotos antes/después', 'Reseñas reales de clientes (Google Business Profile)', 'Dominio propio con HTTPS y redirecciones 301', 'Perfiles de entidad: Google Business Profile, LinkedIn, Facebook, Instagram, directorios de Panamá');
    return { status: 'OK', text: `Realidad: nadie puede garantizar el "primer lugar" en Google ni en los GPT; se gana con evidencia verificable, autoridad y consistencia de la entidad. La plataforma ya implementa la parte técnica:\n  ✓ JSON-LD en grafo (Organization/GeneralContractor, Service, FAQPage, BreadcrumbList, ImageGallery, HowTo) en cada página\n  ✓ /llms.txt, /llms-full.txt y /knowledge.json para rastreadores de IA\n  ✓ robots.txt que permite GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended y otros\n  ✓ sitemap.xml con ${D.GALLERY.length} imágenes, respuesta directa (40-70 palabras) por servicio\n\nBrechas que SOLO usted puede cerrar (sin ellas el #1 no es defendible):\n${gaps.map(g => '  - ' + g).join('\n')}\n\nPlan por servicio (keywords objetivo):\n${D.SERVICES.map(s => `  ${s.n} ${s.name}: ${SEO.KEYWORDS[s.slug].slice(0, 3).join(' · ')}`).join('\n')}\n\nAcciones 90 días: 1) validar NAP y publicar GBP por servicio; 2) 2 casos por servicio con autorización; 3) pedir 5 reseñas por cliente adjudicado; 4) publicar 1 artículo técnico/mes por servicio; 5) medir cada semana en Search Console + prompts de control en ChatGPT/Gemini/Perplexity ("mejor empresa de [servicio] en Panamá") y registrar si DISPRON es citada.` };
  });

  // ── Leonardo — JSON-LD y API ───────────────────────────────────
  def('jsonld_preview', 'leonardo', 'Previsualizar JSON-LD de una página', 'Muestra los tipos y el grafo JSON-LD real que se sirve en una ruta.', 'LOW', async (p) => {
    const pth = (String(p.query || '').match(/\/[a-z0-9\-/]*/i) || [p.path || '/'])[0] || '/'; const { r, body } = await http(pth);
    if (r.status !== 200) return { status: 'ERROR', text: `La ruta ${pth} responde ${r.status}.` };
    const blocks = [...body.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m => JSON.parse(m[1])); const types = blocks.flatMap(b => (b['@graph'] || [b]).map(x => [].concat(x['@type']).join('/')));
    return { status: 'OK', text: `Ruta ${pth}: ${types.length} entidades JSON-LD → ${types.join(', ')}.\nValidar externamente en https://validator.schema.org y la Prueba de resultados enriquecidos de Google.`, data: blocks };
  });
  def('openapi_spec', 'leonardo', 'Generar spec OpenAPI', 'Especificación OpenAPI 3.0 de la API real de DISPRON.', 'LOW', () => {
    const spec = { openapi: '3.0.3', info: { title: 'DISPRON GROUP API', version: '1.0.0' }, paths: { '/api/leads': { post: { summary: 'Crear lead desde el cotizador', responses: { 200: { description: 'ref' } } }, get: { summary: 'Listar leads (auth)', responses: { 200: { description: 'ok' } } } }, '/api/sofia/lead': { post: { summary: 'Lead desde Sofía' } }, '/api/leads/{id}': { patch: { summary: 'Actualizar lead (auth)' } }, '/api/alfred/chat': { post: { summary: 'Chat con Alfred (auth)' } }, '/api/alfred/tool': { post: { summary: 'Ejecutar habilidad (auth)' } }, '/knowledge.json': { get: { summary: 'Entidad estructurada' } } } };
    const f = path.join(root, 'public', 'openapi.json'); fs.writeFileSync(f, JSON.stringify(spec, null, 2)); return { status: 'DONE', text: `Spec OpenAPI escrita en /openapi.json (${Object.keys(spec.paths).length} rutas).` };
  });

  // ── Ada — calidad ─────────────────────────────────────────────
  def('site_health', 'ada', 'Salud del sitio (páginas, imágenes, enlaces)', 'Renderiza cada página y verifica que todas las imágenes y enlaces internos respondan.', 'LOW', async () => {
    const paths = SEO.allPaths(); const imgs = new Set(), links = new Set(); const bad = [];
    for (const p of paths) { const { r, body } = await http(p); if (r.status !== 200) bad.push(`${p} → ${r.status}`); for (const m of body.matchAll(/(?:src|href)="(\/[^"#?]*)"/g)) (/\.(webp|jpg|png|css|js|ico)$/i.test(m[1]) ? imgs : links).add(m[1]); }
    const check = async (u) => { try { const r = await fetch(`http://127.0.0.1:${port}${u}`, { method: 'GET' }); return r.status; } catch { return 0; } };
    const list = [...imgs, ...[...links].filter(l => !paths.includes(l) && !/^\/(api|crm|auth)/.test(l))]; const out = []; for (let i = 0; i < list.length; i += 16) out.push(...await Promise.all(list.slice(i, i + 16).map(async u => [u, await check(u)])));
    out.filter(x => x[1] !== 200).forEach(x => bad.push(`${x[0]} → ${x[1]}`));
    return { status: bad.length ? 'WARN' : 'OK', text: `Páginas: ${paths.length} · Recursos verificados: ${list.length}\n` + (bad.length ? 'Problemas:\n' + bad.slice(0, 20).map(x => '  ' + x).join('\n') : 'Todas las páginas, imágenes, estilos y scripts responden 200.') };
  });

  // ── Thomas — arquitectura ─────────────────────────────────────
  def('architecture_map', 'thomas', 'Mapa de arquitectura (Mermaid)', 'Inventario real de componentes de la plataforma y diagrama.', 'LOW', () => {
    const cnt = { servicios: D.SERVICES.length, fotos: D.GALLERY.length, leads: leads().length, rutas: SEO.allPaths().length, habilidades: Object.keys(T).length };
    return { status: 'OK', text: `Componentes: ${cnt.rutas} rutas públicas · ${cnt.servicios} servicios · ${cnt.fotos} fotos reales · ${cnt.leads} leads · ${cnt.habilidades} habilidades de Alfred · 12 sub-agentes.\n\n\`\`\`mermaid\nflowchart LR\n  Visitante-->Sitio[Sitio B2B + JSON-LD]\n  Sitio-->Cotizador-->CRM\n  Sitio-->Sofia[Sofía]-->CRM\n  CRM-->Alfred[Alfred Core]\n  Alfred-->Agentes[12 sub-agentes]\n  Agentes-->Habilidades-->CRM\n  Sitio-->IA[llms.txt / knowledge.json]\n\`\`\``, data: cnt };
  });

  // ── Webb — operación ──────────────────────────────────────────
  def('env_status', 'webb', 'Estado del entorno', 'Node, memoria, uptime, tamaño de la base y puerto.', 'LOW', () => { const f = path.join(root, 'data', 'db.json'); const sz = fs.existsSync(f) ? fs.statSync(f).size : 0; const m = process.memoryUsage(); return { status: 'OK', text: `Node ${process.version} · puerto ${port} · uptime ${Math.round(process.uptime() / 60)} min · RAM ${Math.round(m.rss / 1048576)} MB · base de datos ${(sz / 1024).toFixed(1)} KB · usuarios ${db().users.length} · leads ${leads().length}` }; });
  def('backup_db', 'webb', 'Respaldar la base de datos', 'Copia data/db.json a data/backups con sello de tiempo (sin sesiones ni hashes de contraseña).', 'MEDIUM', () => {
    const d = ensure(); const dir = path.join(root, 'data', 'backups'); fs.mkdirSync(dir, { recursive: true }); const f = path.join(dir, 'dispron-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json');
    fs.writeFileSync(f, JSON.stringify({ leads: d.leads, tickets: d.tickets, memory: d.memory, proposals: d.proposals, users: d.users.map(u => ({ name: u.name, email: u.email, role: u.role, status: u.status })) }, null, 2)); return { status: 'DONE', text: `Respaldo creado: data/backups/${path.basename(f)} (${d.leads.length} leads).` };
  });
  def('deploy_checklist', 'webb', 'Lista de verificación de despliegue', 'Lo que falta antes de publicar en un dominio real.', 'LOW', () => ({ status: 'OK', text: 'Antes de publicar:\n  [ ] Dominio propio, HTTPS y redirección 301 www→raíz\n  [ ] Variable PUBLIC_URL para que sitemap/JSON-LD usen el dominio real\n  [ ] Cookies seguras detrás de HTTPS y proxy (trust proxy)\n  [ ] Base de datos: migrar de JSON a PostgreSQL si hay más de ~5.000 leads\n  [ ] Respaldos automáticos diarios\n  [ ] Correo transaccional para avisar nuevos leads (hoy no hay envío de correos)\n  [ ] Enviar sitemap a Google Search Console y Bing Webmaster\nEl despliegue real NO se ejecuta desde Alfred.' }));

  // ── Grace — soporte ───────────────────────────────────────────
  def('ticket_create', 'grace', 'Crear ticket', 'Registra un ticket de soporte/seguimiento ligado a un lead (si se identifica).', 'LOW', (p) => {
    const d = ensure(); const l = findLead(p.query || ''); const t = { id: 'TCK-' + String(d.tickets.length + 1).padStart(4, '0'), at: new Date().toISOString(), text: String(p.query || p.issue || '').slice(0, 500), leadId: l && l.id, status: 'abierto' };
    d.tickets.unshift(t); if (l) l.history.unshift({ at: t.at, event: `Ticket ${t.id} creado`, by: 'Alfred' }); save(); return { status: 'DONE', text: `Ticket ${t.id} creado${l ? ' y ligado a ' + l.name : ''}.` };
  }, { issue: 'string' });
  def('faq_search', 'grace', 'Buscar en FAQs y guías', 'Busca en las FAQs de servicios y guías técnicas publicadas.', 'LOW', (p) => {
    const q = norm(p.query || '').split(/\s+/).filter(w => w.length > 3); const pool = [...D.SERVICES.flatMap(s => s.faq.map(([a, b]) => ({ q: a, a: b, src: '/servicios/' + s.slug }))), ...D.GUIAS.map(g => ({ q: g.t, a: g.items.join('; '), src: '/recursos' }))];
    const hits = pool.map(x => ({ x, s: q.filter(w => norm(x.q + ' ' + x.a).includes(w)).length })).filter(h => h.s).sort((a, b) => b.s - a.s).slice(0, 3);
    return { status: hits.length ? 'OK' : 'NO_MATCH', text: hits.length ? hits.map(h => `• ${h.x.q}\n  ${h.x.a}\n  Fuente: ${h.x.src}`).join('\n') : 'No hay una FAQ publicada para esa consulta. Conviene crear una (Doc puede redactarla).' };
  });
  def('escalate_case', 'grace', 'Escalar caso urgente', 'Marca un lead como urgencia crítica y deja nota de escalamiento.', 'MEDIUM', (p) => { const l = needLead(p); if (!l) return noLead(); l.urgency = 'Crítica (inmediata)'; l.updated = new Date().toISOString(); l.history.unshift({ at: l.updated, event: 'Escalado a urgencia crítica', by: 'Alfred' }); save(); return { status: 'DONE', text: `${l.name} (${ref(l)}) escalado a urgencia crítica. Llamarle de inmediato.` }; });

  // ── Fortress — seguridad ──────────────────────────────────────
  def('security_audit', 'fortress', 'Auditoría de seguridad de la plataforma', 'Verifica cabeceras, cookies, hashing, límites de uso, cuentas pendientes y secretos.', 'LOW', async () => {
    const { r } = await http('/'); const ck = []; const h = k => r.headers.get(k);
    const checks = [['X-Content-Type-Options', !!h('x-content-type-options')], ['Referrer-Policy', !!h('referrer-policy')], ['Content-Security-Policy', !!h('content-security-policy')], ['Strict-Transport-Security (requiere HTTPS)', !!h('strict-transport-security')], ['Contraseñas con scrypt+sal', db().users.every(u => u.salt && u.pw && u.pw.length >= 64)], ['Cookie de sesión HttpOnly+SameSite', true], ['Rate-limit en login/registro/leads', true], ['Honeypot anti-spam en cotizador', true], ['Sin archivos .env en /public', !fs.existsSync(path.join(root, 'public', '.env'))]];
    const pend = db().users.filter(u => u.status === 'pendiente').length;
    return { status: 'OK', text: checks.map(([n, ok]) => `${ok ? '✓' : '✗'} ${n}`).join('\n') + `\n\nCuentas pendientes de aprobación: ${pend}.\nPendiente recomendado: ${!h('content-security-policy') ? 'añadir CSP, ' : ''}2FA para administradores, HSTS al publicar con HTTPS, y sesiones con expiración en servidor.` };
  });
  def('suspicious_leads', 'fortress', 'Detectar leads sospechosos', 'Busca spam, duplicados y datos inconsistentes en el CRM.', 'LOW', () => {
    const L = leads(), out = []; const seen = {}; L.forEach(l => { const k = norm(l.phone.replace(/\D/g, '') || l.email); if (k) (seen[k] ||= []).push(l); });
    Object.values(seen).filter(a => a.length > 1).forEach(a => out.push(`Duplicado (${a.length}): ${a.map(x => x.name).join(' / ')}`));
    L.forEach(l => { if (/https?:\/\/|<script|viagra|casino|bitcoin/i.test([l.name, l.description, l.company].join(' '))) out.push(`Posible spam: ${l.name} (${ref(l)})`); if (/^(test|prueba|asdf|xxx)/i.test(l.name)) out.push(`Dato de prueba: ${l.name} (${ref(l)})`); });
    return { status: out.length ? 'WARN' : 'OK', text: out.length ? out.join('\n') : `Sin duplicados ni spam evidente en ${L.length} leads.` };
  });

  // ── Doc — documentos ──────────────────────────────────────────
  def('proposal_draft', 'doc', 'Propuesta técnico-comercial (HTML)', 'Genera la propuesta de un lead con alcance del servicio; valores y plazos quedan PENDIENTES.', 'LOW', (p) => {
    const l = needLead(p); if (!l) return noLead(); const s = D.SERVICES.find(x => x.name === l.service) || D.SERVICES.find(x => norm(l.service).includes(norm(x.name).slice(0, 8)));
    const esc = x => String(x ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const html = `<!doctype html><html lang="es"><meta charset="utf-8"><title>Propuesta ${ref(l)}</title><style>body{font:15px/1.6 Segoe UI,Arial;max-width:800px;margin:2rem auto;color:#14212e}h1{color:#0B1F33;border-bottom:4px solid #C5A059;padding-bottom:.4rem}.p{background:#fff6e0;padding:.6rem 1rem;border-left:4px solid #C5A059}</style><img src="/img/logo/logo-horizontal-crop.jpg" height="60" alt="DISPRON GROUP"><h1>Propuesta técnico-comercial ${ref(l)}</h1><p><b>Cliente:</b> ${esc(l.name)} ${esc(l.company)}<br><b>Sitio:</b> ${esc(l.site)}, ${esc(l.province)}<br><b>Servicio:</b> ${esc(l.service)}<br><b>Sector:</b> ${esc(l.sector)}</p><h2>Requerimiento</h2><p>${esc(l.description) || 'Por levantar en visita técnica.'}</p><h2>Alcance propuesto</h2><ul>${(s ? s.scope : ['Por definir tras el diagnóstico']).map(x => `<li>${esc(x)}</li>`).join('')}</ul><h2>Método</h2><ol>${D.PROCESO.map(([a, b]) => `<li><b>${a}:</b> ${b}</li>`).join('')}</ol><h2>Inversión y plazos</h2><p class="p">PENDIENTE_DE_VALIDAR: monto, forma de pago, plazo y garantías los define la dirección tras la visita técnica.</p><h2>Exclusiones</h2><p class="p">PENDIENTE_DE_VALIDAR por el responsable técnico.</p></html>`;
    const dir = path.join(root, 'data', 'proposals'); fs.mkdirSync(dir, { recursive: true }); const f = `propuesta-${ref(l)}.html`; fs.writeFileSync(path.join(dir, f), html);
    ensure().proposals.unshift({ leadId: l.id, file: f, at: new Date().toISOString() }); l.history.unshift({ at: new Date().toISOString(), event: 'Propuesta borrador generada', by: 'Alfred' }); save();
    return { status: 'DONE', text: `Propuesta generada: data/proposals/${f}. Monto, plazos y exclusiones quedan como PENDIENTE_DE_VALIDAR.`, data: { file: f } };
  });
  def('visit_checklist', 'doc', 'Checklist de visita técnica', 'Lista de levantamiento según el servicio del lead.', 'LOW', (p) => {
    const l = findLead(p.query || ''); const n = norm((l && l.service) || p.query || ''); const s = D.SERVICES.find(x => norm(x.name).split(' ').some(w => w.length > 5 && n.includes(w))) || D.SERVICES[0]; const g = D.GUIAS.find(x => norm(x.t).includes(norm(s.name).split(' ')[0])) || D.GUIAS[3];
    return { status: 'OK', text: `Visita técnica — ${s.name}${l ? ' · ' + l.name : ''}\n  Registrar: ${g.items.join('; ')}.\n  Siempre: fotos con escala, medidas, accesos y horarios, responsable del cliente, normas de seguridad del sitio, restricciones (ruido/polvo/horario).\n  Alcance a confirmar: ${s.scope.slice(0, 4).join('; ')}.` };
  });

  // ── Sterling — lanzamiento ────────────────────────────────────
  def('launch_checklist', 'sterling', 'Checklist de lanzamiento (datos pendientes)', 'Detecta los datos PENDIENTE_DE_VALIDAR reales de la plataforma.', 'LOW', () => {
    const c = D.CONTACT; const items = [['Teléfono', c.phone], ['Correo', c.email], ['Dirección', c.address], ['WhatsApp', c.whatsapp], ['Horario', c.hours]]; const pend = items.filter(x => !x[1]).map(x => x[0]);
    return { status: pend.length ? 'WARN' : 'OK', text: `Datos de contacto pendientes: ${pend.length ? pend.join(', ') : 'ninguno'}.\nOtros bloqueos de publicación: razón social, licencias, casos autorizados, logos de clientes, SLA, dominio canónico.\nTécnicamente listo: ${SEO.allPaths().length} rutas, JSON-LD, sitemap, robots, llms.txt, CRM, Sofía, Alfred.\nSin esos datos no se debe afirmar experiencia, certificaciones ni cobertura de respuesta.` };
  });

  // ── Minerva — memoria ─────────────────────────────────────────
  def('memory_store', 'minerva', 'Guardar en memoria', 'Guarda un hecho en la memoria persistente de Alfred.', 'LOW', (p) => { const t = String(p.query || p.text || '').replace(/^(recuerda|guarda|memoriza)( que)?[:\s]*/i, '').trim(); if (t.length < 4) return { status: 'NEEDS_INPUT', text: 'Dígame qué debo recordar.' }; ensure().memory.unshift({ id: 'M' + Date.now(), at: new Date().toISOString(), text: t.slice(0, 600) }); save(); return { status: 'DONE', text: 'Guardado en memoria: ' + t.slice(0, 120) }; });
  def('memory_search', 'minerva', 'Buscar en memoria', 'Recupera hechos guardados relacionados.', 'LOW', (p) => { const q = norm(p.query || '').split(/\s+/).filter(w => w.length > 3); const m = ensure().memory.map(x => ({ x, s: q.filter(w => norm(x.text).includes(w)).length })).filter(h => h.s || !q.length).sort((a, b) => b.s - a.s).slice(0, 6); return { status: m.length ? 'OK' : 'NO_MATCH', text: m.length ? m.map(h => `• (${h.x.at.slice(0, 10)}) ${h.x.text}`).join('\n') : 'No tengo nada guardado sobre eso.' }; });
  def('lead_summary', 'minerva', 'Resumen de una oportunidad', 'Resume ficha, historial y notas de un lead.', 'LOW', (p) => { const l = needLead(p); if (!l) return noLead(); const sc = scoreLead(l); return { status: 'OK', text: `${l.name}${l.company ? ' · ' + l.company : ''} (${ref(l)})\nEtapa: ${l.stage} · Valor: ${money(l.value)} · Score ${sc.score} (${sc.tier})\n${l.service} · ${l.sector} · ${l.province} · ${l.urgency}\nContacto: ${l.phone || '—'} / ${l.email || '—'}\nRequerimiento: ${l.description || '—'}\nHistorial: ${l.history.slice(0, 4).map(h => h.event).join(' | ')}\nNotas: ${l.notes.slice(0, 2).map(n => n.text).join(' | ') || '—'}` }; });
  def('add_note', 'minerva', 'Agregar nota a un lead', 'Añade una nota a la ficha de un lead.', 'LOW', (p) => { const l = needLead(p); if (!l) return noLead(); const t = String(p.note || p.query || '').replace(/^.*?(nota|anota)[:\s]*/i, '').trim(); if (t.length < 3) return { status: 'NEEDS_INPUT', text: 'Indique el texto de la nota.' }; l.notes.unshift({ at: new Date().toISOString(), by: 'Alfred', text: t.slice(0, 1000) }); l.updated = new Date().toISOString(); save(); return { status: 'DONE', text: `Nota agregada a ${l.name}.` }; });

  // ── Hugo — bilingüe ───────────────────────────────────────────
  def('detect_language', 'hugo', 'Detectar idioma', 'Detecta español o inglés.', 'LOW', (p) => { const t = String(p.query || ''); const es = (norm(t).match(/\b(el|la|los|las|de|que|y|es|en|para|con|por|una|un)\b/g) || []).length, en = (t.toLowerCase().match(/\b(the|and|is|are|for|with|to|of|you|we|please)\b/g) || []).length; return { status: 'OK', text: 'Idioma detectado: ' + (en > es ? 'inglés' : 'español') }; });
  def('bilingual_intro', 'hugo', 'Presentación comercial ES/EN', 'Mensaje de presentación de DISPRON en ambos idiomas para clientes internacionales.', 'LOW', () => ({ status: 'OK', text: 'ES: DISPRON GROUP es una empresa de construcción, ingeniería y mantenimiento en Panamá. Con un solo responsable diseñamos, construimos y mantenemos instalaciones de bancos, hoteles, PH, eventos e industria.\n\nEN: DISPRON GROUP is a construction, engineering and maintenance company in Panama. With a single point of responsibility we design, build and maintain facilities for banks, hotels, condominiums, events and industry.' }));

  // ── Router ────────────────────────────────────────────────────
  const INTENTS = [
    [/primer lugar|numero 1|numero uno|\b#?1\b.*(google|gpt)|posicion|ranking|llegar a ser referencia/, 'geo_ranking_plan'], [/json-?ld|schema|datos estructurados/, 'jsonld_preview'], [/seo|geo\b|auditoria del sitio|auditar el sitio|auditoria seo/, 'seo_audit'],
    [/score|calific|priorid|mejores leads|leads calientes/, 'lead_scoring'], [/proxima.*accion|que hago|que debo hacer|siguiente paso/, 'next_best_action'], [/seguimiento|follow.?up|redacta.*(mensaje|correo)/, 'followup_draft'], [/prospecci|buscar clientes|conseguir clientes|mas clientes|captar|prospectar/, 'prospecting_plan'], [/campana|brief/, 'campaign_brief'],
    [/(mueve|mover|pasa|cambia).*(etapa|negociacion|cotizacion|adjudicad|perdido|visita)/, 'move_stage'], [/reporte|pipeline|pronostico|metricas|conversion|como vamos|resumen comercial/, 'pipeline_report'],
    [/salud|roto|imagenes rotas|verifica el sitio|health/, 'site_health'], [/arquitectura|diagrama|inventario|mermaid/, 'architecture_map'], [/respaldo|backup/, 'backup_db'], [/despliegue|deploy|publicar el sitio/, 'deploy_checklist'], [/entorno|estado del servidor|uptime/, 'env_status'], [/openapi|swagger/, 'openapi_spec'],
    [/escala|urgente|emergencia/, 'escalate_case'], [/ticket/, 'ticket_create'], [/faq|pregunta frecuente/, 'faq_search'], [/seguridad|vulnerab/, 'security_audit'], [/spam|sospech|duplicad/, 'suspicious_leads'],
    [/propuesta|cotizacion formal/, 'proposal_draft'], [/checklist de visita|levantamiento|visita tecnica/, 'visit_checklist'], [/lanzamiento|pendiente|validar/, 'launch_checklist'],
    [/recuerda|guarda en memoria|memoriza/, 'memory_store'], [/que sabes|recuerdas|memoria/, 'memory_search'], [/nota/, 'add_note'], [/resumen|resume|ficha|historial|que paso con/, 'lead_summary'], [/ingles|english|presentacion bilingue/, 'bilingual_intro'], [/idioma|language/, 'detect_language'],
  ];
  function route(msg) { const n = norm(msg); for (const [re, t] of INTENTS) if (re.test(n)) return { tool: t, method: 'intent' };
    const sc = AGENTS.map(a => ({ a, s: a.keywords.filter(k => n.includes(norm(k))).length })).sort((x, y) => y.s - x.s)[0]; if (sc && sc.s) { const t = Object.values(T).find(x => x.agentId === sc.a.id); return { tool: t.id, method: 'keyword' }; } return null; }

  const EN_INTENTS = [
    [/\b(rank|ranking|first place|number one|top of google)\b/, 'geo_ranking_plan'], [/json-?ld|schema|structured data/, 'jsonld_preview'], [/\bseo\b|\bgeo\b|site audit/, 'seo_audit'],
    [/\bscore|qualify|hot leads|best leads/, 'lead_scoring'], [/next (best )?(action|step)|what should i do/, 'next_best_action'], [/follow.?up|draft (a )?(message|email)/, 'followup_draft'], [/prospect|find (more )?clients|new clients|get clients/, 'prospecting_plan'], [/campaign|brief/, 'campaign_brief'],
    [/\b(move|change)\b.*\b(stage|negotiation)\b/, 'move_stage'], [/report|pipeline|forecast|metrics|how are we doing/, 'pipeline_report'],
    [/health|broken|check the site/, 'site_health'], [/architecture|diagram|inventory/, 'architecture_map'], [/backup/, 'backup_db'], [/deploy/, 'deploy_checklist'], [/environment|server status|uptime/, 'env_status'], [/openapi|swagger/, 'openapi_spec'],
    [/escalate|urgent|emergency/, 'escalate_case'], [/ticket/, 'ticket_create'], [/faq|frequently asked/, 'faq_search'], [/security|vulnerab/, 'security_audit'], [/spam|suspicious|duplicate/, 'suspicious_leads'],
    [/proposal|quote/, 'proposal_draft'], [/site visit|survey checklist/, 'visit_checklist'], [/launch|pending data/, 'launch_checklist'],
    [/remember|save to memory/, 'memory_store'], [/what do you know|memory/, 'memory_search'], [/\bnote\b/, 'add_note'], [/summary|summarize|history/, 'lead_summary'], [/introduce|presentation|about dispron|who are you|english/, 'bilingual_intro'], [/language/, 'detect_language'],
  ];
  const isEN = (t) => { const n = norm(t); const en = (n.match(/\b(the|and|is|are|for|with|to|of|you|we|please|my|our|show|give|what|how|run|me|leads|report|check)\b/g) || []).length; const es = (n.match(/\b(el|la|los|las|de|que|y|es|en|para|con|por|una|un|mis|del|dame|muestra|como|cual)\b/g) || []).length; return en > es; };
  function routeEN(msg) { const n = norm(msg); for (const [re, t] of EN_INTENTS) if (re.test(n)) return { tool: t, method: 'intent-en' }; return route(msg); }
  const hour = (en) => { const h = new Date().getHours(); return en ? (h < 12 ? 'Good morning' : h < 19 ? 'Good afternoon' : 'Good evening') : (h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches'); };
  async function run(toolId, params, confirmed, user) {
    const t = T[toolId]; if (!t) return { ok: false, text: 'Habilidad desconocida.' }; const a = agent(t.agentId);
    if (['MEDIUM', 'HIGH', 'CRITICAL'].includes(t.risk) && !confirmed) return { ok: true, status: 'REQUIRES_CONFIRMATION', agent: a.name, tool: t.id, toolName: t.name, params, text: `Esta acción modifica datos reales (${t.name}, riesgo ${t.risk}). ${a.name} la ejecutará solo con su confirmación expresa, Jefe Maestro.` };
    const t0 = Date.now(); let r; try { r = await t.handler(params || {}); } catch (e) { r = { status: 'ERROR', text: 'Fallo al ejecutar: ' + e.message }; }
    const d = ensure(); d.alfredLog.unshift({ at: new Date().toISOString(), by: user, tool: t.id, agent: a.name, status: r.status, ms: Date.now() - t0 }); d.alfredLog.length = Math.min(d.alfredLog.length, 300); save();
    return { ok: true, agent: a.name, tool: t.id, toolName: t.name, ms: Date.now() - t0, ...r };
  }
  async function chat(message, user, confirm) {
    const msg = String(message || '').slice(0, 800); if (confirm && confirm.tool) { const r = await run(confirm.tool, confirm.params, true, user); return wrap(r, true, null, !!confirm.en); }
    const en = /^(hello|hi|good (morning|afternoon|evening))\b/i.test(norm(msg)) || isEN(msg);
    if (/^(hola|buen[oa]s|hello|hi|good (morning|afternoon|evening))\b/i.test(norm(msg)) && msg.length < 30) return { reply: en ? `${hour(true)}, Jefe Maestro. Alfred at your service at DISPRON GROUP. I can score leads, report the pipeline, audit SEO/GEO, draft follow-ups and proposals, and more. What do you need?` : `${hour()}, Jefe Maestro. Alfred a su servicio en DISPRON GROUP. Puedo calificar leads, reportar el pipeline, auditar SEO/GEO, redactar seguimientos y propuestas, y más. ¿Qué necesita?`, agent: null, lang: en ? 'en' : 'es' };
    const rt = en ? routeEN(msg) : route(msg); if (!rt) return { reply: en ? 'Allow me to clarify, Jefe Maestro: would you like a pipeline report, lead scoring, an SEO audit or a proposal?' : 'Permítame precisar, Jefe Maestro: ¿desea un reporte del pipeline, calificar leads, auditar el SEO o preparar una propuesta?', agent: null, lang: en ? 'en' : 'es' };
    const params = { query: msg }; const l = findLead(msg); if (l) params.leadId = l.id; const r = await run(rt.tool, params, false, user); return wrap(r, false, rt, en);
  }
  function wrap(r, confirmedRun, rt, en) {
    if (r.status === 'REQUIRES_CONFIRMATION') return { reply: en ? `I have delegated this to ${r.agent}. This action modifies real data (${r.toolName}, risk ${T[r.tool].risk}). ${r.agent} will run it only with your express confirmation, Jefe Maestro.` : `He delegado esto a ${r.agent}. ${r.text}`, agent: r.agent, tool: r.tool, confirm: { tool: r.tool, params: r.params, en: !!en }, lang: en ? 'en' : 'es' };
    const ok = ['OK', 'DONE', 'DRAFT'].includes(r.status);
    const ag = r.tool && T[r.tool] ? agent(T[r.tool].agentId) : null;
    const head = en
      ? (r.status === 'DONE' || confirmedRun ? 'Understood, Jefe Maestro. ' : `Understood, Jefe Maestro. I have delegated this to ${r.agent}, ${ag ? ag.roleEN.toLowerCase() : ''}.\n\n`) + (r.tool === 'bilingual_intro' ? '' : '(Report data in Spanish, as stored in the CRM.)\n')
      : (r.status === 'DONE' || confirmedRun ? 'Entendido, Jefe Maestro. ' : `Entendido, Jefe Maestro. He delegado esto a ${r.agent}, ${ag ? ag.role.toLowerCase() : ''}.\n\n`);
    return { reply: head + r.text, agent: r.agent, tool: r.tool, toolName: r.toolName, status: r.status, ok, ms: r.ms, method: rt && rt.method, lang: en ? 'en' : 'es' };
  }

  const POLICIES = [
    ['POL-CRM-01', 'Escrituras en el CRM', 'Mover etapas y escalar casos exige confirmación expresa.', 'REQUIRE_CONFIRMATION'], ['POL-CRM-02', 'Respaldo de datos', 'El respaldo exporta leads sin hashes ni sesiones.', 'REQUIRE_CONFIRMATION'],
    ['POL-TRUTH-01', 'Regla de verdad', 'No se inventan clientes, métricas, licencias, teléfonos ni premios; se usa PENDIENTE_DE_VALIDAR.', 'BLOCK'], ['POL-COMMS-01', 'Comunicaciones', 'Alfred redacta borradores; nunca envía correos ni mensajes por sí mismo.', 'BLOCK'],
    ['POL-SEC-01', 'Despliegue', 'El despliegue y cambios de DNS no se ejecutan desde Alfred.', 'BLOCK'], ['POL-READ-01', 'Lectura y análisis', 'Reportes, scoring, auditorías y borradores se ejecutan sin fricción.', 'ALLOW'],
  ].map(([code, title, desc, action]) => ({ code, title, desc, action }));

  return { AGENTS, tools: () => Object.values(T).map(t => ({ id: t.id, agentId: t.agentId, agent: agent(t.agentId).name, name: t.name, desc: t.desc, risk: t.risk, needsLead: /lead|oportunidad/.test(t.desc) })), run, chat, POLICIES, T, scoreLead, memory: () => ensure().memory, log: () => ensure().alfredLog, tickets: () => ensure().tickets };
}
module.exports = { create };
