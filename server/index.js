const express = require('express');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const Alfred = require('./alfred/engine');

const app = express();
const PORT = Number(process.env.PORT) || 8000;
const DIST = path.join(__dirname, '..', 'dist');
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const DB_FILE = path.join(DATA_DIR, 'db.json');
const HTTPS = process.env.FORCE_HTTPS === '1';
fs.mkdirSync(DATA_DIR, { recursive: true });

const STAGES = ['Nuevo Lead', 'Visita/Diagnóstico', 'Cotización enviada', 'En negociación', 'Adjudicado/Contrato recurrente', 'Perdido'];
const db = fs.existsSync(DB_FILE) ? JSON.parse(fs.readFileSync(DB_FILE, 'utf8')) : { users: [], sessions: {}, leads: [] };
const save = () => { const tmp = DB_FILE + '.tmp'; fs.writeFileSync(tmp, JSON.stringify(db, null, 2)); fs.renameSync(tmp, DB_FILE); };
const id = () => crypto.randomBytes(6).toString('hex');
const clean = (s, n = 500) => String(s ?? '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const ref = (l) => 'DSP-' + l.id.slice(0, 6).toUpperCase();

app.disable('x-powered-by');
if (process.env.TRUST_PROXY) app.set('trust proxy', process.env.TRUST_PROXY);
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  res.setHeader('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self' https://wa.me; object-src 'none'");
  if (HTTPS) res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});
app.use(express.json({ limit: '100kb' }));
app.use(cookieParser());

const hits = new Map();
const limit = (max, ms) => (req, res, next) => {
  const k = req.ip + req.path, now = Date.now();
  const arr = (hits.get(k) || []).filter(t => now - t < ms); arr.push(now); hits.set(k, arr);
  if (arr.length > max) return res.status(429).json({ error: 'Demasiadas solicitudes. Intente en unos minutos.' });
  next();
};
setInterval(() => { const now = Date.now(); for (const [k, a] of hits) if (!a.some(t => now - t < 600000)) hits.delete(k); }, 600000).unref();

const hash = (pw, salt) => crypto.scryptSync(pw, salt, 64).toString('hex');
const cookieOpts = { httpOnly: true, sameSite: 'lax', secure: HTTPS, maxAge: 7 * 864e5, path: '/' };
const me = (req) => { const s = db.sessions[req.cookies.sid]; return s ? db.users.find(u => u.id === s.uid) : null; };
const needUser = (req, res, next) => { const u = me(req); if (!u) return res.status(401).json({ error: 'No autenticado' }); if (u.status !== 'activo') return res.status(403).json({ error: 'Cuenta pendiente de acceso' }); req.user = u; next(); };
const needAdmin = (req, res, next) => needUser(req, res, () => req.user.role === 'admin' ? next() : res.status(403).json({ error: 'Solo administradores' }));
const startSession = (res, u) => { const sid = crypto.randomBytes(24).toString('hex'); db.sessions[sid] = { uid: u.id, at: Date.now() }; save(); res.cookie('sid', sid, cookieOpts); };

app.post('/api/auth/register', limit(10, 600000), (req, res) => {
  const name = clean(req.body.name, 80), email = clean(req.body.email, 120).toLowerCase(), pw = String(req.body.password || '');
  if (!name || !/^\S+@\S+\.\S+$/.test(email)) return res.status(400).json({ error: 'Nombre y correo válidos son requeridos.' });
  if (pw.length < 10) return res.status(400).json({ error: 'La contraseña debe tener al menos 10 caracteres.' });
  if (db.users.some(u => u.email === email)) return res.status(409).json({ error: 'Ese correo ya está registrado.' });
  const first = db.users.length === 0, salt = crypto.randomBytes(16).toString('hex');
  const u = { id: id(), name, email, salt, pw: hash(pw, salt), role: first ? 'admin' : 'ventas', status: first ? 'activo' : 'pendiente', created: new Date().toISOString() };
  db.users.push(u); save();
  if (first) startSession(res, u);
  res.json({ ok: true, role: u.role, status: u.status });
});
app.post('/api/auth/login', limit(15, 600000), (req, res) => {
  const email = clean(req.body.email, 120).toLowerCase(), u = db.users.find(x => x.email === email);
  if (!u || !crypto.timingSafeEqual(Buffer.from(hash(String(req.body.password || ''), u.salt)), Buffer.from(u.pw))) return res.status(401).json({ error: 'Credenciales incorrectas.' });
  if (u.status !== 'activo') return res.status(403).json({ error: 'Su cuenta está pendiente de aprobación por un administrador.' });
  startSession(res, u); res.json({ ok: true });
});
app.post('/api/auth/logout', (req, res) => { delete db.sessions[req.cookies.sid]; save(); res.clearCookie('sid', { path: '/' }); res.json({ ok: true }); });
app.get('/api/me', (req, res) => { const u = me(req); res.json(u ? { name: u.name, email: u.email, role: u.role, status: u.status } : null); });
app.get('/api/users', needAdmin, (req, res) => res.json(db.users.map(({ id, name, email, role, status, created }) => ({ id, name, email, role, status, created }))));
app.patch('/api/users/:id', needAdmin, (req, res) => {
  const u = db.users.find(x => x.id === req.params.id); if (!u) return res.sendStatus(404);
  if (u.id === req.user.id) return res.status(400).json({ error: 'No puede modificar su propia cuenta.' });
  if (['activo', 'pendiente', 'suspendido'].includes(req.body.status)) u.status = req.body.status;
  if (['admin', 'ventas'].includes(req.body.role)) u.role = req.body.role;
  if (u.status !== 'activo') for (const [k, s] of Object.entries(db.sessions)) if (s.uid === u.id) delete db.sessions[k];
  save(); res.json({ ok: true });
});

function createLead(src, b) {
  const now = new Date().toISOString();
  const lead = {
    id: id(), created: now, updated: now, stage: STAGES[0], source: src,
    name: clean(b.name, 80), company: clean(b.company, 100), phone: clean(b.phone, 30), email: clean(b.email, 120),
    sector: clean(b.sector, 40), service: clean(b.service, 100), province: clean(b.province, 40), site: clean(b.site, 200),
    urgency: clean(b.urgency, 20), date: clean(b.date, 20), slot: clean(b.slot, 20), description: clean(b.description, 1500),
    value: 0, notes: [], history: [{ at: now, event: `Lead creado vía ${src}` }],
  };
  db.leads.unshift(lead); save(); return lead;
}
const validContact = (b) => clean(b.name) && (clean(b.phone).replace(/\D/g, '').length >= 7 || /^\S+@\S+\.\S+$/.test(clean(b.email)));

app.post('/api/leads', limit(8, 600000), (req, res) => {
  if (req.body.website) return res.json({ ok: true, ref: 'DSP-RECIBIDO' });
  if (!validContact(req.body)) return res.status(400).json({ error: 'Indique su nombre y un teléfono o correo válido.' });
  res.json({ ok: true, ref: ref(createLead(clean(req.body.origin, 30) === 'contacto' ? 'Formulario de contacto' : 'Cotizador web', req.body)) });
});
app.post('/api/sofia/lead', limit(8, 600000), (req, res) => {
  if (!validContact(req.body)) return res.status(400).json({ error: 'Falta nombre y contacto.' });
  res.json({ ok: true, ref: ref(createLead('Sofía (chatbot)', req.body)) });
});
app.get('/api/leads', needUser, (req, res) => res.json({ stages: STAGES, leads: db.leads }));
app.patch('/api/leads/:id', needUser, (req, res) => {
  const l = db.leads.find(x => x.id === req.params.id); if (!l) return res.sendStatus(404);
  const b = req.body, ev = [];
  if (b.stage && STAGES.includes(b.stage) && b.stage !== l.stage) { ev.push(`Etapa: ${l.stage} → ${b.stage}`); l.stage = b.stage; }
  if (b.value !== undefined) { const v = Math.max(0, Number(b.value) || 0); if (v !== l.value) ev.push(`Valor estimado: B/. ${v.toLocaleString('es-PA')}`); l.value = v; }
  for (const k of ['name', 'company', 'phone', 'email', 'sector', 'service', 'province', 'site', 'urgency', 'date', 'description']) if (b[k] !== undefined) l[k] = clean(b[k], k === 'description' ? 1500 : 200);
  if (b.note) { l.notes.unshift({ at: new Date().toISOString(), by: req.user.name, text: clean(b.note, 1000) }); ev.push('Nota agregada'); }
  ev.forEach(e => l.history.unshift({ at: new Date().toISOString(), event: e, by: req.user.name }));
  l.updated = new Date().toISOString(); save(); res.json(l);
});
app.delete('/api/leads/:id', needAdmin, (req, res) => { db.leads = db.leads.filter(x => x.id !== req.params.id); save(); res.json({ ok: true }); });
app.get('/api/leads.csv', needUser, (req, res) => {
  const cols = ['id', 'created', 'stage', 'name', 'company', 'phone', 'email', 'sector', 'service', 'province', 'urgency', 'value', 'source'];
  const q = v => { const s = String(v ?? ''); return '"' + (/^[=+\-@]/.test(s) ? "'" + s : s).replace(/"/g, '""') + '"'; };
  res.attachment('leads-dispron.csv').type('text/csv').send('\ufeff' + cols.join(',') + '\n' + db.leads.map(l => cols.map(c => q(l[c])).join(',')).join('\n'));
});

const alfred = Alfred.create({ getDb: () => (db.tickets || (db.tickets = []), db.memory || (db.memory = []), db.alfredLog || (db.alfredLog = []), db.proposals || (db.proposals = []), db), save, port: PORT, root: __dirname });
app.get('/api/alfred/meta', needUser, (req, res) => res.json({ agents: alfred.AGENTS, tools: alfred.tools(), policies: alfred.POLICIES, memory: alfred.memory().slice(0, 20), log: alfred.log().slice(0, 30), tickets: alfred.tickets().slice(0, 20) }));
app.post('/api/alfred/chat', needUser, limit(60, 60000), async (req, res) => { try { res.json(await alfred.chat(clean(req.body.message, 2000), req.user.name, req.body.confirm)); } catch (e) { console.error(e); res.status(500).json({ reply: 'Error interno al procesar la solicitud.' }); } });
app.post('/api/alfred/tool', needUser, limit(60, 60000), async (req, res) => { try { res.json(await alfred.run(clean(req.body.tool, 60), req.body.params || {}, !!req.body.confirmed, req.user.name)); } catch (e) { console.error(e); res.status(500).json({ status: 'ERROR', text: 'Error interno al ejecutar la herramienta.' }); } });
app.get('/api/alfred/scores', needUser, (req, res) => res.json(Object.fromEntries(db.leads.map(l => [l.id, alfred.scoreLead(l)]))));
app.get('/proposals/:f', needUser, (req, res) => { const p = path.join(__dirname, 'data', 'proposals', path.basename(req.params.f)); fs.existsSync(p) ? res.sendFile(p) : res.sendStatus(404); });
app.use('/api', (req, res) => res.status(404).json({ error: 'Ruta no encontrada' }));

const LEGACY = { '/auth': '/acceso/', '/galeria': '/proyectos/', '/login': '/acceso/' };
app.get(Object.keys(LEGACY), (req, res) => res.redirect(301, LEGACY[req.path]));
app.get(['/crm', '/crm/'], (req, res, next) => {
  const u = me(req);
  if (!u || u.status !== 'activo') return res.redirect(302, '/acceso/');
  res.setHeader('Cache-Control', 'no-store');
  next();
});

const longCache = /\.(css|js|webp|png|jpg|jpeg|svg|ico|woff2)$/i;
const staticOpts = { extensions: ['html'], dotfiles: 'allow', setHeaders: (res, f) => res.setHeader('Cache-Control', longCache.test(f) ? 'public, max-age=31536000, immutable' : 'public, max-age=600') };
app.use((req, res, next) => /^\/(_headers|_redirects|\.htaccess)$/.test(req.path) ? res.sendStatus(404) : next());
app.use(express.static(DIST, staticOpts));
app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1h' }));
app.use((req, res) => res.status(404).sendFile(path.join(DIST, '404.html')));

app.listen(PORT, () => console.log('DISPRON GROUP en http://localhost:' + PORT));
