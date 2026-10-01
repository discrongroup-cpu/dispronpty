(function(){
var al=document.getElementById('aalert'),L=document.getElementById('login'),R=document.getElementById('reg');
if(!L)return;
var $=function(i){return document.getElementById(i);};
document.querySelectorAll('.tabs button').forEach(function(b){b.onclick=function(){document.querySelectorAll('.tabs button').forEach(function(x){x.setAttribute('aria-selected',x===b);});L.hidden=b.dataset.t!=='login';R.hidden=b.dataset.t!=='reg';al.hidden=true;};});
function msg(t,ok){al.textContent=t;al.hidden=false;al.className='alert'+(ok?' okk':'');}
async function post(u,b){var r;try{r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});}catch(e){throw new Error('No hay conexión con el servidor de la plataforma.');}
 var j=await r.json().catch(function(){return {};});if(r.status===404||r.status===405)throw new Error('El servidor de la plataforma no está activo en este hosting.');if(!r.ok)throw new Error(j.error||'Error');return j;}
fetch('/api/me').then(function(r){return r.ok?r.json():null;}).then(function(u){if(u&&u.status==='activo')location.href='/crm/';}).catch(function(){});
L.onsubmit=async function(e){e.preventDefault();try{await post('/api/auth/login',{email:$('le').value,password:$('lp').value});location.href='/crm/';}catch(x){msg(x.message);}};
R.onsubmit=async function(e){e.preventDefault();try{var j=await post('/api/auth/register',{name:$('rn').value,email:$('re').value,password:$('rp').value});if(j.status==='activo')location.href='/crm/';else msg('Cuenta creada. Queda pendiente de aprobación por un administrador.',true);}catch(x){msg(x.message);}};
})();
