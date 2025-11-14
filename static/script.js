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
});