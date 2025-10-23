document.addEventListener("DOMContentLoaded", () => {
  console.log("Velvet Bite loaded 🍰");
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');

   // --- Відкривання/закривання меню + зміна вигляду кнопки ---
  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
    menuToggle.classList.toggle('active'); // 🔹 ДОДАНО — змінює іконку
  });
  

  // --- Показати більше позицій ---
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
