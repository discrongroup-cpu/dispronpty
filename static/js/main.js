(function(){
  var t=document.querySelector('.nav-toggle'),n=document.getElementById('nav');
  if(t&&n){t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o);});}
  var f=document.getElementById('quote-form');
  if(!f)return;
  var p=new URLSearchParams(location.search).get('servicio'),sel=document.getElementById('servicio');
  if(p&&sel){sel.value=p;}
  f.addEventListener('submit',function(ev){
    var d=new FormData(f),st=f.querySelector('.form-status');
    if(d.get('_gotcha')){ev.preventDefault();return;}
    var action=f.getAttribute('action');
    if(action&&action!=='#'){
      ev.preventDefault();
      fetch(action,{method:'POST',body:d,headers:{Accept:'application/json'}}).then(function(r){
        st.textContent=r.ok?'¡Gracias! Hemos recibido su solicitud y le contactaremos pronto.':'No se pudo enviar. Escríbanos por WhatsApp.';
        if(r.ok)f.reset();
      }).catch(function(){st.textContent='No se pudo enviar. Escríbanos por WhatsApp.';});
      return;
    }
    ev.preventDefault();
    var svc=sel&&sel.selectedIndex>0?sel.options[sel.selectedIndex].text:'';
    var msg='Hola DICPROM, solicito cotización.%0A'+
      ['Nombre: '+d.get('nombre'),'Empresa: '+(d.get('empresa')||'-'),'Teléfono: '+d.get('telefono'),'Correo: '+d.get('email'),
       'Servicio: '+(svc||'-'),'Provincia: '+(d.get('provincia')||'-'),'Proyecto: '+d.get('mensaje')].map(encodeURIComponent).join('%0A');
    st.textContent='Abriendo WhatsApp para enviar su solicitud…';
    window.open('https://wa.me/'+f.dataset.wa+'?text='+msg,'_blank','noopener');
  });
})();
