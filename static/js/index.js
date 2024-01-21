document.getElementById('header__menu').addEventListener('click', () => {
    document.getElementById('header__menu').classList.toggle('active');
    document.querySelector('nav').classList.toggle('active');
});

/*set link that matches current url class to active*/
document.querySelector('.header__links').querySelectorAll('a').forEach((link) => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active');
    }
})