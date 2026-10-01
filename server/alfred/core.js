// Núcleo compartido: puntuación de leads, probabilidades por etapa y normalización de texto.
const STAGES = ['Nuevo Lead', 'Visita/Diagnóstico', 'Cotización enviada', 'En negociación', 'Adjudicado/Contrato recurrente', 'Perdido'];
const PROB = [0.10, 0.25, 0.45, 0.65, 1, 0];
const norm = s => String(s ?? '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const day = 864e5;

function scoreLead(l, now = Date.now()) {
  let s = 10; const why = [];
  const add = (n, t) => { s += n; why.push((n > 0 ? '+' : '') + n + ' ' + t); };
  if (/Cr[ií]tica/i.test(l.urgency)) add(25, 'urgencia crítica'); else if (/Prioritaria/i.test(l.urgency)) add(12, 'urgencia prioritaria');
  if (l.value >= 50000) add(25, 'valor ≥ B/. 50.000'); else if (l.value >= 10000) add(15, 'valor ≥ B/. 10.000'); else if (l.value > 0) add(5, 'valor estimado');
  if (/banc|hotel/i.test(l.sector)) add(8, 'sector con contratos recurrentes');
  if (/mantenimiento/i.test(l.service)) add(12, 'servicio recurrente');
  if (l.phone && l.email) add(8, 'contacto completo'); else if (l.phone || l.email) add(3, 'contacto parcial');
  if (l.description && l.description.length > 20) add(5, 'requerimiento descrito');
  if (l.site) add(4, 'sitio identificado');
  const si = STAGES.indexOf(l.stage); add([0, 5, 10, 15, 0, 0][si] || 0, 'avance de etapa');
  const age = (now - new Date(l.created)) / day, idle = (now - new Date(l.updated || l.created)) / day;
  const open = si < 4;
  if (open && age <= 2) add(10, 'lead reciente');
  if (open && idle > 14) add(-10, 'sin actividad > 14 días');
  if (si === 5) s = Math.min(s, 5);
  s = Math.max(0, Math.min(100, Math.round(s)));
  return { score: s, tier: s >= 70 ? 'A' : s >= 45 ? 'B' : 'C', why };
}

module.exports = { STAGES, PROB, norm, scoreLead, day };
