(function(){
var MAP={nombre:'name',empresa:'company',telefono:'phone',mensaje:'description',servicio:'service',provincia:'province'};
var track=function(n,p){if(window.dspTrack)window.dspTrack(n,p);};
function payload(f){var o={};new FormData(f).forEach(function(v,k){o[MAP[k]||k]=String(v).trim();});
  var s=f.querySelector('select[name=servicio],select[name=service]');if(s&&s.selectedIndex>0)o.service=s.options[s.selectedIndex].text;
  delete o.consent;return o;}
function waText(o){return 'Hola DISPRON GROUP, solicito una cotización.\n'+[['Nombre',o.name],['Empresa',o.company],['Teléfono',o.phone],['Correo',o.email],['Sector',o.sector],['Servicio',o.service],['Urgencia',o.urgency],['Provincia',o.province],['Sitio',o.site],['Fecha',[o.date,o.slot].filter(Boolean).join(' ')],['Detalle',o.description]]
  .filter(function(x){return x[1];}).map(function(x){return x[0]+': '+x[1];}).join('\n');}
function send(f,o){return fetch(f.getAttribute('action')||'/api/leads',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(o)})
  .then(function(r){return r.json().catch(function(){return {};}).then(function(j){if(!r.ok||!j.ok){var e=new Error(j.error||'HTTP '+r.status);e.status=r.status;e.user=!!j.error&&r.status<500;throw e;}return j;});});}
function fallback(f,o,st){st.textContent='No pudimos registrar la solicitud en línea. ';var a=document.createElement('a');a.className='btn btn-wa';a.target='_blank';a.rel='noopener';
  a.href='https://wa.me/'+f.dataset.wa+'?text='+encodeURIComponent(waText(o));a.textContent='Enviar por WhatsApp';st.appendChild(a);}
function contactOk(o){return o.name&&((o.phone||'').replace(/\D/g,'').length>=7||/^\S+@\S+\.\S+$/.test(o.email||''));}
var qs=new URLSearchParams(location.search);
function prefill(f){var sv=qs.get('servicio'),sc=qs.get('sector');
  var s=f.querySelector('select[name=servicio],select[name=service]');
  if(s&&sv)[].forEach.call(s.options,function(op){if(op.dataset.slug===sv||op.value===sv)s.value=op.value;});
  var c=f.querySelector('select[name=sector]');if(c&&sc)[].forEach.call(c.options,function(op){if(op.dataset.id===sc)c.value=op.value;});}
function submitLead(f,done){var st=f.querySelector('.form-status'),o=payload(f);
  if(o.website)return;
  if(!contactOk(o)){st.textContent='Indique su nombre y un teléfono o correo válido.';return;}
  var btn=f.querySelector('[type=submit]');btn.disabled=true;st.textContent='Enviando…';
  send(f,o).then(function(j){track('generate_lead',{servicio:o.service||'',provincia:o.province||''});done(j);})
  .catch(function(e){if(e.user)st.textContent=e.message;else fallback(f,o,st);})
  .then(function(){btn.disabled=false;});}

var c=document.getElementById('quote-form');
if(c){prefill(c);c.addEventListener('submit',function(ev){ev.preventDefault();submitLead(c,function(j){c.reset();c.querySelector('.form-status').textContent='¡Gracias! Su solicitud quedó registrada con la referencia '+j.ref+'.';});});}

var f=document.getElementById('qform');
if(!f)return;
prefill(f);
var steps=f.querySelectorAll('.wz-step'),bar=f.querySelectorAll('.wz-progress li'),prev=f.querySelector('[data-prev]'),next=f.querySelector('[data-next]'),sub=f.querySelector('[type=submit]'),st=f.querySelector('.form-status'),cur=0;
function show(i){cur=i;steps.forEach(function(s,k){s.hidden=k!==i;});bar.forEach(function(b,k){b.classList.toggle('on',k<=i);});
  prev.hidden=i===0;next.hidden=i===steps.length-1;sub.hidden=i!==steps.length-1;st.textContent='';
  var first=steps[i].querySelector('select,input:not(.hp),textarea');if(first&&i>0)first.focus();}
function valid(i){var bad=[].filter.call(steps[i].querySelectorAll('[required]'),function(el){return !el.checkValidity();});
  if(bad.length){bad[0].reportValidity?bad[0].reportValidity():0;bad[0].focus();st.textContent='Complete los campos obligatorios.';return false;}return true;}
next.addEventListener('click',function(){if(valid(cur))show(cur+1);});
prev.addEventListener('click',function(){show(cur-1);});
f.addEventListener('submit',function(ev){ev.preventDefault();if(!valid(cur))return;
  submitLead(f,function(j){steps.forEach(function(s){s.hidden=true;});f.querySelector('.wz-nav').hidden=true;f.querySelector('.wz-progress').hidden=true;st.textContent='';
    var d=f.querySelector('.wz-done');d.hidden=false;d.querySelector('.wz-ref').textContent=j.ref;d.setAttribute('tabindex','-1');d.focus();});});
show(0);
})();
