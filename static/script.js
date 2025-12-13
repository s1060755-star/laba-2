document.addEventListener("DOMContentLoaded", () => {
  console.log("Velvet Bite loaded 🍰");
  // Initialize burger/menu toggles per-nav in a defensive way so menu works even if other code throws
  try {
    const toggles = document.querySelectorAll('.menu-toggle');
    toggles.forEach(t => {
      // avoid duplicate attachments
      if (t.dataset.menuAttached === '1') return;
      t.dataset.menuAttached = '1';
      t.setAttribute('role', 'button');
      // find the closest nav parent, then its .nav-links inside that nav; fallback to global #nav-links
      let nav = t.closest('nav');
      let links = null;
      if (nav) links = nav.querySelector('.nav-links') || nav.querySelector('#nav-links');
      if (!links) links = document.getElementById('nav-links') || document.querySelector('.nav-links');
      // set initial aria state
      t.setAttribute('aria-expanded', String(links && links.classList.contains('show')));
      if (!links) return;
      t.addEventListener('click', () => {
        try {
          links.classList.toggle('show');
          t.classList.toggle('active');
          const expanded = t.getAttribute('aria-expanded') === 'true';
          t.setAttribute('aria-expanded', String(!expanded));
          document.body.style.overflow = links.classList.contains('show') ? 'hidden' : '';
        } catch (e) { console.error('menu toggle click handler error', e); }
      });
    });
  } catch (e) { console.error('menu init error', e); }

  // --- Перевірка форми реєстрації ---
  const signUpForm = document.getElementById('signUpForm');
  const submitBtn = document.getElementById('submitBtn');
  
  if (signUpForm) {
    const inputs = signUpForm.querySelectorAll('input[required]');
    
    // Функція перевірки заповнення полів
    function checkForm() {
      let allFilled = true;
      
      inputs.forEach(input => {
        if (input.value.trim() === '') {
          allFilled = false;
        }
      });
      
      submitBtn.disabled = !allFilled;
    }
    
    // Додаємо обробники подій для кожного поля
    inputs.forEach(input => {
      input.addEventListener('input', checkForm);
      input.addEventListener('change', checkForm);
    });
    
    // Перевірка при завантаженні сторінки
    checkForm();
    
    // We use normal form POST for sign-up/login to keep behavior simple.
  }

  // --- Інший ваш код ---
  const showMoreBtn = document.getElementById('showMoreBtn');
  if (showMoreBtn) {
    showMoreBtn.addEventListener('click', () => {
      document.querySelectorAll('.hidden-item').forEach(item => {
        item.style.display = 'block';
      });
      showMoreBtn.parentElement.style.display = 'none';
    });
  }

  // --- Flash messages -> toasts ---
  const flashContainers = document.querySelectorAll('.flash-messages');
  if (flashContainers.length) {
    // Move each message to a single top-level container so it floats above everything
    let toastRoot = document.getElementById('toast-root');
    if (!toastRoot) {
      toastRoot = document.createElement('div');
      toastRoot.id = 'toast-root';
      toastRoot.className = 'flash-messages';
      document.body.appendChild(toastRoot);
    }

    flashContainers.forEach(container => {
      Array.from(container.children).forEach(node => {
        // Attach a close button and auto-dismiss
        const closeBtn = document.createElement('button');
        closeBtn.className = 'flash-close';
        closeBtn.innerHTML = '✕';
        closeBtn.addEventListener('click', () => node.remove());
        node.appendChild(closeBtn);
        toastRoot.appendChild(node);
        // Auto remove after 4s
        setTimeout(() => {
          try { node.remove(); } catch(e) {}
        }, 4000);
      });
      // remove original container (empty)
      container.remove();
    });
  }

  // Ensure menu toggle is attached robustly (attach on load and resize)
  function ensureMenuToggle(){
    try{
      const navLinksEl = document.getElementById('nav-links') || document.querySelector('.nav-links');
      const toggles = document.querySelectorAll('.menu-toggle');
      if(!navLinksEl || !toggles.length) return;
      toggles.forEach(t => {
        if(t.dataset.menuAttached === '1') return; // already attached
        t.dataset.menuAttached = '1';
        t.setAttribute('role','button');
        t.setAttribute('aria-expanded', String(navLinksEl.classList.contains('show')));
        t.addEventListener('click', function(e){
          try{
            navLinksEl.classList.toggle('show');
            t.classList.toggle('active');
            const expanded = t.getAttribute('aria-expanded') === 'true';
            t.setAttribute('aria-expanded', String(!expanded));
            // lock body scroll on small screens
            if (navLinksEl.classList.contains('show')) document.body.style.overflow = 'hidden'; else document.body.style.overflow = '';
          }catch(err){
            console.error('menu-toggle handler error', err);
          }
        });
      });
    }catch(e){ console.error('ensureMenuToggle error', e); }
  }

  // Run on load and on resize to ensure handler exists
  ensureMenuToggle();
  window.addEventListener('resize', ensureMenuToggle);

  // --- Theme toggle: create button dynamically if template doesn't include it ---
  let themeToggle = document.getElementById('theme-toggle');
  function createThemeToggle(){
    if(themeToggle) return;
    themeToggle = document.createElement('button');
    themeToggle.id = 'theme-toggle';
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-pressed','false');
    themeToggle.setAttribute('aria-label','Перемкнути новорічну тему');
    themeToggle.innerHTML = '<span class="theme-label">Новорічна</span>';
    document.body.appendChild(themeToggle);
  }

  function updateToggleState(theme){
    if(!themeToggle) return;
    const isNew = theme === 'newyear';
    themeToggle.setAttribute('aria-pressed', String(isNew));
    const icon = themeToggle.querySelector('.theme-icon');
    const label = themeToggle.querySelector('.theme-label');
    if(icon) icon.textContent = isNew ? '✨' : '🎄';
    if(label) label.textContent = isNew ? 'Святкова' : 'Новорічна';
  }

  function applyTheme(theme){
    // Only control festive overlays (snow + garlands).
    // Do NOT change the global theme or other styles — leave the simple theme untouched.
    if(theme === 'newyear'){
      ensureSnow();
      ensureGarlands();
    } else {
      removeSnow();
      removeGarlands();
    }
    updateToggleState(theme);
  }

  createThemeToggle();
  const saved = (function(){ try { return localStorage.getItem('theme'); } catch(e){ return null; } })() || 'light';
  applyTheme(saved);
  if(themeToggle){
    // ensure theme toggle is a safe button that cannot navigate away
    themeToggle.setAttribute('type', 'button');
    themeToggle.addEventListener('click', function(e){
      try{ e.preventDefault(); e.stopPropagation(); }catch(err){}
      // Determine current state from persisted value first to avoid relying
      // on a class that we intentionally do not toggle anymore.
      const current = (function(){ try{ return localStorage.getItem('theme') || 'light'; }catch(e){ return document.documentElement.classList.contains('newyear') ? 'newyear' : 'light'; } })();
      const next = current === 'newyear' ? 'light' : 'newyear';
      applyTheme(next);
      try { localStorage.setItem('theme', next); } catch(e){}
    });
  }

  /* Snow: create randomized flakes that fall rarely and with varied paths */
  function ensureSnow(){
    if(document.querySelector('.snow-container')) return;
    const container = document.createElement('div'); container.className = 'snow-container';
    document.body.appendChild(container);

    const flakes = 14; // relatively few
    for(let i=0;i<flakes;i++){
      const f = document.createElement('div');
      f.className = 'flake';
      f.textContent = '❄';
      const left = Math.random()*100;
      const size = 8 + Math.random()*22; // font-size
      const duration = 10 + Math.random()*20; // seconds
      // use a negative delay so flakes start at a random point in their fall
      const delay = -Math.random()*duration;
      const dx = (Math.random()*160 - 80) + 'px';
      f.style.left = left + '%';
      f.style.fontSize = size + 'px';
      f.style.opacity = (0.6 + Math.random()*0.4).toFixed(2);
      f.style.setProperty('--dx', dx);
      f.style.animation = `fall-random ${duration}s linear ${delay}s infinite`;
      container.appendChild(f);
    }
  }

  function removeSnow(){
    const c = document.querySelector('.snow-container'); if(c) c.remove();
  }

  /* Garland lights: create per-card light elements so each bulb can twinkle independently */
  function ensureGarlands(){
    try{
      document.querySelectorAll('.menu-item').forEach(item => {
        if(item.querySelector('.garland-lights')) return; // already created
        const g = document.createElement('div'); g.className = 'garland-lights';
        const positions = [4,18,32,48,62,76,90];
        const colors = ['#ff6b6b','#ffd166','#81f79f','#9fd1ff','#d6a3ff','#ffd166','#ff6b6b'];
        positions.forEach((pos, i) => {
          const s = document.createElement('span');
          s.className = 'light';
          s.style.left = pos + '%';
          s.style.background = colors[i % colors.length];
          s.style.animationDelay = (Math.random() * 1.8) + 's';
          s.style.opacity = (0.8 + Math.random() * 0.2).toFixed(2);
          g.appendChild(s);
        });
        item.appendChild(g);
      });
    }catch(e){ console.error('ensureGarlands error', e); }
  }

  function removeGarlands(){
    document.querySelectorAll('.garland-lights').forEach(el => el.remove());
  }

  /* Promo wheel: shows once per session (localStorage flag), draws a canvas wheel and spins to pick a discount */
  function createPromoModal(forceShow){
    try{
      // only auto-show if user hasn't spun before (persist across sessions)
      if(!forceShow && window.localStorage && localStorage.getItem('promoSpun')) return; // already spun
    }catch(e){ }

    const discounts = [5,10,15,20,25,50];
    const colors = ['#f9c2c2','#ffd9a8','#d8f7d6','#d0e9ff','#e6d1ff','#ffd7e6'];

    const overlay = document.createElement('div'); overlay.className = 'promo-overlay'; overlay.id = 'promoOverlay';
    const modal = document.createElement('div'); modal.className = 'promo-modal';
    modal.innerHTML = `
      <h3>Вітаємо! Спробуй колесо фортуни</h3>
      <div class="promo-wheel-wrap">
        <div class="wheel-frame">
          <canvas id="promoWheel" class="promo-wheel" width="320" height="320" aria-hidden="true"></canvas>
          <div id="spinCenter" class="spin-center" role="button" aria-label="SPIN"><span class="spin-text">SPIN</span></div>
        </div>
        <button id="promoSpin" class="promo-spin-btn">Крутити</button>
        <div id="promoResult" class="promo-result" aria-live="polite"></div>
        <button id="promoClose" class="promo-close">Закрити</button>
      </div>
    `;
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // draw wheel onto canvas
    const canvas = document.getElementById('promoWheel');
    const ctx = canvas.getContext('2d');
    const cx = canvas.width/2, cy = canvas.height/2, r = Math.min(cx,cy)-8;
    const seg = 360 / discounts.length;
    function drawWheel(){
      for(let i=0;i<discounts.length;i++){
        const start = (i*seg) * Math.PI/180;
        const end = ((i+1)*seg) * Math.PI/180;
        ctx.beginPath();
        ctx.moveTo(cx,cy);
        ctx.arc(cx,cy,r,start,end);
        ctx.closePath();
        ctx.fillStyle = colors[i%colors.length];
        ctx.fill();
        // text
        ctx.save();
        ctx.translate(cx,cy);
        const angle = (i*seg + seg/2) * Math.PI/180;
        ctx.rotate(angle);
        ctx.fillStyle = '#4B2E2B';
        ctx.font = 'bold 14px Montserrat, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(discounts[i] + '%', r-10, 6);
        ctx.restore();
      }
      // center label is provided by overlay element (spinCenter) so we don't draw it on canvas
    }
    drawWheel();

    const wheelEl = canvas; // rotate the canvas element
    const spinBtn = document.getElementById('promoSpin');
    const spinCenter = document.getElementById('spinCenter');
    const resEl = document.getElementById('promoResult');
    const closeBtn = document.getElementById('promoClose');

    let spinning = false;
    spinBtn.addEventListener('click', () => {
      if(spinning) return; spinning = true; spinBtn.disabled = true; resEl.textContent='';
      const rounds = 5 + Math.floor(Math.random()*4); // 5-8 rounds
      const idx = Math.floor(Math.random() * discounts.length);
      // rotate so the chosen segment centers under the pointer (we still pick idx randomly,
      // but we'll compute which segment actually lands under the triangle by reading
      // the computed transform after animation to avoid offset mismatches)
      // add a bounded jitter so the wheel doesn't consistently land on segment edges
      // jitter range is +/- 30% of a segment to avoid edges while keeping randomness
      const jitter = (Math.random() * (seg * 0.6)) - (seg * 0.3);
      const rotateTo = rounds*360 + (idx * seg) + seg/2 + 180 + jitter;
      wheelEl.style.transition = 'transform 5s cubic-bezier(.2,.9,.2,1)';
      // force reflow so transition applies reliably
      void wheelEl.offsetWidth;
      wheelEl.style.transform = `rotate(${rotateTo}deg)`;
      wheelEl.addEventListener('transitionend', function handler(){
        wheelEl.removeEventListener('transitionend', handler);
        // read actual applied rotation from computed transform to determine which
        // segment is under the pointer (robust against coordinate/origin differences)
        try{
          const st = window.getComputedStyle(wheelEl);
          const tr = st.transform || st.webkitTransform || '';
          let appliedDeg = 0;
          if(tr && tr !== 'none'){
            const m = tr.match(/matrix\(([^)]+)\)/);
            if(m){
              const vals = m[1].split(',').map(v=>parseFloat(v));
              const a = vals[0], b = vals[1];
              appliedDeg = Math.round(Math.atan2(b, a) * (180/Math.PI));
            }
          }
          // normalize to [0,360)
          appliedDeg = ((appliedDeg % 360) + 360) % 360;
          // pointer on the wheel points downward (90deg in canvas coordinates)
          const pointerAngle = 90;
          // which segment center is currently at the pointer? compute difference
          const angleAtPointer = (pointerAngle - appliedDeg + 360) % 360;
          const landedIdx = Math.floor(angleAtPointer / seg) % discounts.length;
          const discount = discounts[landedIdx];
          resEl.textContent = `Вам випала знижка ${discount}% — вона застосована до вашого замовлення`;
          try{ localStorage.setItem('activeDiscount', String(discount)); }catch(e){}
          try{ localStorage.setItem('promoSpun', '1'); }catch(e){}
          showPromoBadge(discount);
        }catch(e){
          // fallback to previously chosen index on error
          const discount = discounts[idx];
          resEl.textContent = `Вам випала знижка ${discount}% — вона застосована до вашого замовлення`;
          try{ localStorage.setItem('activeDiscount', String(discount)); }catch(e){}
          try{ localStorage.setItem('promoSpun', '1'); }catch(e){}
          showPromoBadge(discount);
        }
        spinning = false; spinBtn.disabled = true;
        spinBtn.textContent = 'Крутили!';
      });
    });
    // allow clicking the fixed center overlay to start spin as well
    if(spinCenter){
      spinCenter.style.cursor = 'pointer';
      spinCenter.addEventListener('click', function(){ spinBtn.click(); });
    }

    closeBtn.addEventListener('click', () => { overlay.remove(); try{ localStorage.setItem('promoSpun','1'); }catch(e){} });

    // cancel on backdrop click
    overlay.addEventListener('click', (ev) => { if(ev.target === overlay){ overlay.remove(); try{ localStorage.setItem('promoSpun','1'); }catch(e){} } });
  }

  function showPromoBadge(discount){
    try{
      let b = document.getElementById('promoBadge');
      if(!b){ b = document.createElement('div'); b.id = 'promoBadge'; b.className = 'promo-badge'; document.body.appendChild(b); }
      b.textContent = `Знижка ${discount}% застосована`;
      // clicking badge opens order page or shows modal with details
      b.style.cursor = 'pointer';
      b.onclick = function(){
        // if user hasn't spun (edge-case) open full modal; otherwise navigate to order page to use discount
        try{
          const spun = localStorage.getItem('promoSpun');
          if(!spun){ createPromoModal(); }
          else { window.location.href = '/order'; }
        }catch(e){ window.location.href = '/order'; }
      };
    }catch(e){ }
  }

  // show badge if discount already present
  try{
    const active = localStorage.getItem('activeDiscount');
    // Only show promo badge on homepage or on individual dish pages
    try{
      const p = (location && location.pathname) ? location.pathname : '/';
      if(active && (p === '/' || p === '/index.html' || p.startsWith('/dish'))) showPromoBadge(active);
    }catch(e){ if(active) showPromoBadge(active); }
  }catch(e){}

  // show promo modal only on homepage (or when explicitly forced via ?promo=1 or #promo)
  try{
    const path = location.pathname || '/';
    const force = (location.search && location.search.indexOf('promo=1') !== -1) || (location.hash === '#promo');
    const spun = localStorage.getItem('promoSpun');
    const isHome = (path === '/' || path === '/index.html');
    if(force || isHome){
      // force=true ensures modal is shown on homepage reloads
      setTimeout(() => createPromoModal(true), 900);
    }
  }catch(e){ /* do not auto-show modal on error */ }

  // Ensure order form submits include discount and attempt to refresh totals on order pages
  try{
    if(location.pathname && location.pathname.startsWith('/order')){
      const raw = localStorage.getItem('activeDiscount');
      let activeDisc = 0;
      try{
        if(raw){ const m = String(raw).match(/-?\d+(?:\.\d+)?/); activeDisc = m ? parseFloat(m[0]) : 0; }
      }catch(e){ activeDisc = 0 }
      const discInput = document.getElementById('discountInput');
      const infoEl = document.getElementById('discountInfo');
      if(discInput) discInput.value = String(activeDisc);
      if(infoEl && activeDisc) infoEl.textContent = `Знижка ${activeDisc}% застосована`;

      const orderForm = document.getElementById('orderForm');
      if(orderForm){
        orderForm.addEventListener('submit', function(ev){
          try{
            const di = document.getElementById('discountInput');
            const raw2 = localStorage.getItem('activeDiscount');
            let ad = 0;
            try{ if(raw2){ const m2 = String(raw2).match(/-?\d+(?:\.\d+)?/); ad = m2 ? parseFloat(m2[0]) : 0; } }catch(e){ ad = 0 }
            if(di) di.value = String(ad);
          }catch(e){}
        });
      }

      // If page provides a renderItems function, call it to refresh totals
      try{ if(typeof window.renderItems === 'function') window.renderItems(); }catch(e){}
    }
  }catch(e){}
});