const form = document.querySelector('form');
const loader = document.getElementById('loader');
document.body.classList.remove("no-scroll");

form.addEventListener('submit', () => {
window.scrollTo(0,0);
loader.style.display = 'flex';
document.body.classList.add("no-scroll");
});
