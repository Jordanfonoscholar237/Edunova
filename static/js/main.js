const toggle = document.querySelector('[data-menu-toggle]');
const nav = document.querySelector('[data-nav-links]');
if (toggle && nav) {
  toggle.addEventListener('click', () => nav.classList.toggle('open'));
}
setTimeout(() => {
  document.querySelectorAll('.flash').forEach((flash) => {
    flash.style.opacity = '0';
    flash.style.transform = 'translateY(-8px)';
    setTimeout(() => flash.remove(), 300);
  });
}, 5000);
