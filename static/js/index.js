document.getElementById('header__menu').addEventListener('click', () => {
    document.getElementById('header__menu').classList.toggle('active');
    document.querySelector('nav').classList.toggle('active');
});

document.querySelector('.header__links').querySelectorAll('a').forEach((link) => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active');
    }
})

/*accordion*/
const accordions = document.getElementsByClassName('accordion');
for (const accordion of accordions) {
    const items = accordion.querySelectorAll('.accordion__item');
    for (const item of items) {
        item.querySelector('.accordion__item__header').addEventListener('click', () => {
            item.classList.toggle('hidden');

        });
    }
}