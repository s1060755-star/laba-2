document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('list');
  const form = document.getElementById('dishForm');
  const messages = document.getElementById('messages');

  function showMessage(text, type='success'){
    messages.innerHTML = `<div class="msg ${type}">${text}</div>`;
    setTimeout(()=>{messages.innerHTML=''}, 4000);
  }

  async function loadList(){
    listEl.textContent = 'Завантаження...';
    try{
      const res = await fetch('/api/dishes');
      if(!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      let data = await res.json();
      if(!Array.isArray(data)) data = [];
      if(data.length === 0) {
        listEl.innerHTML = '<em>Немає страв</em>';
        return;
      }
      listEl.innerHTML = '';
      data.forEach(d => {
        const el = document.createElement('div');
          el.className = 'dish';
          const name = escapeHtml(d.name||'');
          const desc = escapeHtml(d.description||'');
          const price = d.price!=null?d.price:'-';
          // left wrapper ensures consistent alignment for name/description
          el.innerHTML = `<div class="left"><div class="name">${name}</div><div class="muted">${desc}</div></div><div class="controls"><div class="price">${price}</div><button class="dish-btn" data-id="${d.id}">Видалити</button></div>`;
        // attach delete handler
        const btn = el.querySelector('.dish-btn');
        if(btn){
          btn.addEventListener('click', async (ev)=>{
            ev.preventDefault();
            const id = btn.getAttribute('data-id');
            if(!confirm('Видалити страву #' + id + '?')) return;
            try{
              const res = await fetch('/api/dishes/' + encodeURIComponent(id), { method: 'DELETE' });
              if(res.ok){
                showMessage('Страва видалена', 'success');
                loadList();
              } else {
                let body = '';
                try{ body = await res.json(); }catch(e){ body = await res.text(); }
                showMessage('Помилка видалення: ' + (body.message || body.error || JSON.stringify(body)), 'error');
              }
            }catch(err){
              showMessage('Помилка мережі при видаленні', 'error');
              console.error(err);
            }
          });
        }
        listEl.appendChild(el);
      });
    }catch(err){
      listEl.innerHTML = '<div class="msg error">Помилка завантаження</div>';
      console.error(err);
    }
  }

  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
  }

  form.addEventListener('submit', async e=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    // convert numeric fields
    if(data.price) data.price = parseFloat(data.price);
    if(data.calories) data.calories = parseInt(data.calories);
    try{
      const res = await fetch('/api/dishes', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      if(res.status === 201){
        const json = await res.json();
        showMessage('Страва додана', 'success');
        form.reset();
        loadList();
      } else {
        let body = '';
        try{ body = await res.json(); }catch(e){ body = await res.text(); }
        showMessage('Помилка: ' + (body.message || body.error || JSON.stringify(body)), 'error');
      }
    }catch(err){
      showMessage('Помилка мережі', 'error');
      console.error(err);
    }
  });

  loadList();
});
