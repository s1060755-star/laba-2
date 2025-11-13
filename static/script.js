document.addEventListener("DOMContentLoaded", () => {
  console.log("Velvet Bite loaded 🍰");
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');

  // --- Відкривання/закривання меню ---
  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
    menuToggle.classList.toggle('active');
  });

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
    
    // Обробка відправки форми
    signUpForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Показуємо спінер або змінюємо текст кнопки
      submitBtn.innerHTML = 'Вхід...';
      submitBtn.disabled = true;
      
      // Збираємо дані форми
      const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
      };
      
      // Відправляємо дані на сервер
      fetch('/signUp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Перенаправляємо на сторінку акаунта при успішному вході
          window.location.href = '/account';
        } else {
          alert(data.message || 'Помилка входу');
          submitBtn.innerHTML = 'Увійти';
          submitBtn.disabled = false;
        }
      })
      .catch(error => {
        console.error('Помилка:', error);
        alert('Сталася помилка');
        submitBtn.innerHTML = 'Увійти';
        submitBtn.disabled = false;
      });
    });
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
});