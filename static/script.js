document.addEventListener("DOMContentLoaded", () => {
  console.log("Velvet Bite loaded 🍰");
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');

  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
  });

});
