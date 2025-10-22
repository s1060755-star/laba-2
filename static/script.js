document.addEventListener("DOMContentLoaded", () => {
  console.log("Velvet Bite loaded 🍰");
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');

  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
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
