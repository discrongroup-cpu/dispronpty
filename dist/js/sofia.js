(function(){
var el=function(i){return document.getElementById(i);};
var dataEl=el('sofia-data');if(!dataEl)return;
var data=JSON.parse(dataEl.textContent),box=el('sofia'),open=el('sofia-open'),log=el('sofia-log'),quick=el('sofia-quick'),form=el('sofia-form'),inp=el('sofia-in');
var lead={},step='idle',started=false;
var norm=function(s){return String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');};
function say(t,who){var d=document.createElement('div');d.className='msg '+(who||'b');d.textContent=t;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
function opts(arr){quick.innerHTML='';arr.forEach(function(o){var b=document.createElement('button');b.type='button';b.textContent=o.label||o;b.onclick=function(){handle(o.value||o.label||o,o.label||o);};quick.appendChild(b);});}
function link(t,href){var d=say('');var a=document.createElement('a');a.href=href;a.textContent=t;if(/^https?:/.test(href)){a.target='_blank';a.rel='noopener';}d.appendChild(a);}
function openChat(){box.hidden=false;open.hidden=true;open.setAttribute('aria-expanded','true');inp.focus();if(!started){started=true;begin();}}
function closeChat(){box.hidden=true;open.hidden=false;open.setAttribute('aria-expanded','false');open.focus();}
open.onclick=openChat;el('sofia-close').onclick=closeChat;
document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('[data-sofia]');if(t){e.preventDefault();openChat();}});
box.addEventListener('keydown',function(e){if(e.key==='Escape')closeChat();});
function greet(){var h=new Date().getHours();return h<12?'Buenos días':h<19?'Buenas tardes':'Buenas noches';}
function begin(){say(greet()+', soy Sofía, asistente técnica de DISPRON GROUP. Le ayudo a registrar su requerimiento para que un especialista le contacte. ¿De qué sector es su operación?');step='sector';opts(data.sectores.map(function(s){return s.name;}));}
var KB=[
 [/precio|costo|cuanto|presupuesto/,'Cada proyecto se cotiza tras un diagnóstico técnico en sitio. Con los datos que me comparta, el equipo agenda la visita y prepara una propuesta por alcance.'],
 [/garantia/,'Las garantías se definen por alcance en la propuesta técnica. Un asesor le detallará los términos de su servicio.'],
 [/horario|nocturn|fin de semana|sin detener|sin cerrar/,'Sí, planificamos trabajos nocturnos y en fines de semana para no detener su operación, sobre todo en banca, hotelería y PH.'],
 [/provincia|cobertura|colon|chiriqui|david|cocle|veraguas|interior/,'Atendemos todas las provincias y comarcas de la República de Panamá.'],
 [/emergencia|urgente|24/,'Para emergencias, registre la urgencia como «Crítica» y escríbanos también por WhatsApp para priorizar la atención.']
];
var SVC=[[/electric|tablero|subestac|tension|transformador|generador|planta de emergencia/,'ingenieria-electrica'],[/aire|hvac|chiller|refriger|split|vrf|cuarto frio/,'hvac-aire-acondicionado'],
 [/incendio|rociador|plomer|agua|fuga|bomba|tuberia|hidro|sanitar|gas/,'fontaneria-hidraulica-contra-incendios'],[/epoxi|piso/,'pisos-pintura-epoxica'],[/stand|evento|convenc|feria/,'stands-corporativos'],
 [/render|plano|arquitect|3d|interior/,'arquitectura-planos-render-3d'],[/fachada|\bph\b|edificio|condomin|impermeab/,'mantenimiento-ph-edificios'],
 [/remodel|fit.?out|oficina|cielo|yeso|acabado|ebanist|mueble|pintura/,'remodelacion-fit-out'],[/soldadura|metal|estructura|tanque|piping/,'metalmecanica-soldadura'],
 [/maquinaria|montaje|automatiz|plc|linea/,'montaje-maquinaria-automatizacion'],[/predictiv|termograf|vibraci|mantenimiento/,'mantenimiento-industrial'],
 [/obra civil|construc|excavac|asfalto|paviment|galera/,'construccion-obra-civil'],[/epc|llave en mano|gerencia|inspecci/,'gerencia-proyectos-epc-llave-en-mano'],
 [/petrol|miner|industrial/,'ingenieria-proyectos-industriales-petroleros-mineria'],[/diseno industrial|producto|patente|simulac/,'diseno-industrial-ingenieria-de-producto'],
 [/suministro|importa|repuesto|material|equipo/,'suministro-equipos-materiales']];
function find(list,t){var n=norm(t);return list.filter(function(x){var m=norm(x.name);return m===n||m.indexOf(n)>-1||(n.length>4&&n.indexOf(m)>-1);})[0];}
function summary(){return ['Sector: '+lead.sector,'Servicio: '+lead.service,'Provincia: '+lead.province,'Urgencia: '+lead.urgency,'Contacto: '+lead.name+(lead.company?' ('+lead.company+')':'')+' · '+(lead.phone||lead.email)].join('\n');}
function ask(next){step=next;
 if(next==='service'){say('¿Qué servicio necesita? Puede elegirlo o describirlo con sus palabras.');opts(data.services.map(function(s){return s.name;}));}
 else if(next==='province'){say('¿En qué provincia está el sitio?');opts(['Panamá','Panamá Oeste','Colón','Chiriquí','Coclé','Otra provincia']);}
 else if(next==='urgency'){say('¿Qué urgencia tiene?');opts(['Planificada','Prioritaria (menos de 15 días)','Crítica (inmediata)']);}
 else if(next==='description'){say('Describa brevemente el requerimiento (área, equipo, problema o alcance).');opts(['Omitir']);}
 else if(next==='name'){say('Perfecto. ¿Cuál es su nombre y el de su empresa? (por ejemplo: Ana Pérez, Hotel Central)');quick.innerHTML='';}
 else if(next==='contact'){say('¿A qué teléfono o correo podemos contactarle?');quick.innerHTML='';}
 else if(next==='confirm'){say('Resumen de su solicitud:\n'+summary()+'\n¿Confirma que la registre?');opts(['Sí, registrar','Corregir']);}
}
function waHref(){return 'https://wa.me/'+data.wa+'?text='+encodeURIComponent('Hola DISPRON GROUP, solicito atención.\n'+summary()+(lead.description?'\nDetalle: '+lead.description:''));}
function submit(){say('Registrando…');
 fetch('/api/sofia/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lead)})
 .then(function(r){return r.json().catch(function(){return {};}).then(function(j){if(!r.ok||!j.ok){var e=new Error(j.error||'HTTP '+r.status);e.user=!!j.error&&r.status<500;throw e;}return j;});})
 .then(function(j){step='done';if(window.dspTrack)window.dspTrack('generate_lead',{fuente:'sofia',servicio:lead.service});
   say('Listo. Su solicitud quedó registrada con la referencia '+j.ref+'. Un especialista de DISPRON GROUP le contactará para coordinar la visita técnica. ¿Algo más?');opts(['Ver servicios','Nueva solicitud']);})
 .catch(function(e){step='done';say(e.user?'No pude registrar la solicitud: '+e.message:'No pude registrar la solicitud en línea. Puede enviarla por WhatsApp con un clic:');link('Enviar por WhatsApp',waHref());opts([{label:'Ir al cotizador',value:'__form'},'Nueva solicitud']);});}
function handle(v,label){
 v=String(v).trim();if(!v)return;say(label||v,'u');quick.innerHTML='';var n=norm(v);
 if(v==='__form'){location.href='/cotizar/';return;}
 if(n==='ver servicios'){location.href='/servicios/';return;}
 if(n==='nueva solicitud'||n==='corregir'){lead={};begin();return;}
 if(['name','contact','description'].indexOf(step)<0){var kb=KB.filter(function(k){return k[0].test(n);})[0];
  if(kb){say(kb[1]);if(step==='idle'||step==='done')opts(['Nueva solicitud',{label:'Ir al cotizador',value:'__form'}]);else ask(step);return;}}
 switch(step){
  case 'sector':{var s=find(data.sectores,v)||(/banc/.test(n)&&data.sectores[0])||(/hotel/.test(n)&&data.sectores[1])||(/\bph\b|horizontal|edificio|condomin/.test(n)&&data.sectores[2])||(/event|convenc|stand/.test(n)&&data.sectores[3])||(/industr|planta|fabrica|mina|puerto/.test(n)&&data.sectores[4]);
   lead.sector=s?s.name:v.slice(0,40);say('Entendido, sector '+lead.sector.toLowerCase()+'.');ask('service');break;}
  case 'service':{var sv=find(data.services,v);if(!sv){var m=SVC.filter(function(x){return x[0].test(n);})[0];if(m)sv=data.services.filter(function(x){return x.slug===m[1];})[0];}
   if(!sv){say('No identifiqué el servicio. Elija una de las líneas disponibles.');opts(data.services.map(function(x){return x.name;}));return;}
   lead.service=sv.name;say('Servicio: '+sv.name+'.');ask('province');break;}
  case 'province':{lead.province=v.slice(0,40);ask('urgency');break;}
  case 'urgency':{lead.urgency=/crit|inmedi|emerg/.test(n)?'Crítica':/prior|15|pronto/.test(n)?'Prioritaria':'Planificada';ask('description');break;}
  case 'description':{lead.description=n==='omitir'?'':v.slice(0,1500);ask('name');break;}
  case 'name':{var p=v.split(/\s*[,;\/|-]\s*|\s+de la empresa\s+|\s+de\s+(?=[A-ZÁÉÍÓÚ])/);lead.name=p[0].slice(0,80);lead.company=(p.slice(1).join(' ')||'').slice(0,100);ask('contact');break;}
  case 'contact':{var em=(v.match(/\S+@\S+\.\S+/)||[])[0],ph=v.replace(/\S+@\S+\.\S+/,'').replace(/[^\d+]/g,'');
   if(!em&&ph.replace(/\D/g,'').length<7){say('No reconocí un teléfono o correo válido. ¿Podría escribirlo nuevamente?');return;}
   lead.email=em||'';lead.phone=ph.replace(/\D/g,'').length>=7?ph:'';ask('confirm');break;}
  case 'confirm':{if(/^s|registr|confirm|ok/.test(n))submit();else{lead={};begin();}break;}
  default:{say('Puedo ayudarle a registrar una solicitud de visita técnica o responder dudas generales.');opts(['Nueva solicitud',{label:'Ir al cotizador',value:'__form'}]);}
 }
}
form.addEventListener('submit',function(e){e.preventDefault();var v=inp.value;inp.value='';handle(v);});
})();
