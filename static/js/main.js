(function(){
  document.documentElement.classList.add('js');
  var hdr=document.querySelector('.site-header'),top=document.querySelector('.to-top');
  function onScroll(){var y=window.scrollY>40;if(hdr)hdr.classList.toggle('scrolled',y);if(top)top.classList.toggle('show',window.scrollY>700);}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  var t=document.querySelector('.nav-toggle'),n=document.getElementById('nav');
  if(t&&n){t.addEventListener('click',function(){var o=n.classList.toggle('open');t.setAttribute('aria-expanded',o);t.setAttribute('aria-label',o?'Cerrar menú':'Abrir menú');document.body.style.overflow=o?'hidden':'';});}

  var rev=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.08});
    rev.forEach(function(el){io.observe(el);});
  }else{rev.forEach(function(el){el.classList.add('in');});}

  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-count]').forEach(function(el){
    if(reduce)return;var end=+el.dataset.count,s=null;
    var co=new IntersectionObserver(function(es){if(!es[0].isIntersecting)return;co.disconnect();
      function step(ts){if(!s)s=ts;var p=Math.min((ts-s)/1400,1);el.textContent=Math.round(end*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(step);}
      requestAnimationFrame(step);});co.observe(el);
  });

  var chips=document.querySelectorAll('.chip[data-filter]');
  chips.forEach(function(c){c.addEventListener('click',function(){
    var f=c.dataset.filter;chips.forEach(function(x){var a=x===c;x.classList.toggle('active',a);x.setAttribute('aria-pressed',a);});
    document.querySelectorAll('#project-grid .g-item,#post-grid .post-card').forEach(function(g){g.classList.toggle('hidden',f!=='all'&&g.dataset.cat!==f);});
  });});

  var links=document.querySelectorAll('[data-lightbox]');
  if(links.length){
    var lb=document.createElement('div');lb.className='lightbox';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');lb.setAttribute('aria-label','Imagen ampliada');
    lb.innerHTML='<button type="button" aria-label="Cerrar">×</button><figure><img alt=""><figcaption></figcaption></figure>';
    document.body.appendChild(lb);
    var img=lb.querySelector('img'),cap=lb.querySelector('figcaption'),btn=lb.querySelector('button'),last=null;
    function close(){lb.classList.remove('open');if(last)last.focus();}
    links.forEach(function(a){a.addEventListener('click',function(ev){ev.preventDefault();last=a;img.src=a.getAttribute('href');img.alt=a.dataset.caption||'';cap.textContent=a.dataset.caption||'';lb.classList.add('open');btn.focus();});});
    btn.addEventListener('click',close);lb.addEventListener('click',function(ev){if(ev.target===lb)close();});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&lb.classList.contains('open'))close();});
  }

  function track(n,p){if(typeof window.gtag==='function')window.gtag('event',n,p||{});}
  document.addEventListener('click',function(ev){
    var a=ev.target.closest&&ev.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href');
    if(h.indexOf('wa.me')>-1)track('click_whatsapp',{link_url:h});
    else if(h.indexOf('tel:')===0)track('click_tel');
    else if(h.indexOf('mailto:')===0)track('click_email');
  });

  window.dspTrack=track;
})();
