document.querySelectorAll('.carousel').forEach(carousel => {
  let index = 0;
  const images = carousel.querySelectorAll('.carousel-image');
  const prev = carousel.querySelector('.prev');
  const next = carousel.querySelector('.next');

  // Créer les points
  const dotsContainer = document.createElement('div');
  dotsContainer.className = 'carousel-dots';
  images.forEach((img, i) => {
    const dot = document.createElement('span');
    if(i===0) dot.classList.add('active');
    dot.addEventListener('click', () => {
      index = i;
      showImage(index);
    });
    dotsContainer.appendChild(dot);
  });
  carousel.appendChild(dotsContainer);
  const dots = dotsContainer.querySelectorAll('span');

  function showImage(i) {
    images.forEach(img => img.classList.remove('active'));
    images[i].classList.add('active');
    dots.forEach(d => d.classList.remove('active'));
    dots[i].classList.add('active');
  }

  prev.addEventListener('click', () => {
    index = (index - 1 + images.length) % images.length;
    showImage(index);
  });

  next.addEventListener('click', () => {
    index = (index + 1) % images.length;
    showImage(index);
  });

  // Support glisser sur mobile
  let startX = 0;
  carousel.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
  });
  carousel.addEventListener('touchend', e => {
    let endX = e.changedTouches[0].clientX;
    if(endX - startX > 50) { // glisser vers la droite
      index = (index - 1 + images.length) % images.length;
      showImage(index);
    } else if(startX - endX > 50) { // glisser vers la gauche
      index = (index + 1) % images.length;
      showImage(index);
    }
  });

  showImage(index);
});
