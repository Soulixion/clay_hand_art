let btnTop = document.getElementById("btnTop");

window.onscroll = function () 
{
    if (document.documentElement.scrollTop > 1000) {
        btnTop.style.display = "block";
    } else {
        btnTop.style.display = "none";
    }
};

btnTop.addEventListener("click", function () 
{
    window.scrollTo({ top: 0, behavior: "smooth" });
});

// Désactiver la redirection au clic sur la carte entière (si present)
// On gère maintenant l'ouverture via un bouton dédié '.view-btn'
const viewButtons = document.querySelectorAll('.view-btn');
viewButtons.forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    const link = this.getAttribute('data-link') || this.href;
    if (link) {
      window.open(link, '_blank');
    }
  });
});

// Listen for clicks on visible 'Ajouter au panier' buttons
document.addEventListener('click', function(e) {
  const btn = e.target.closest('.add-cart-btn');
  if (!btn) return;
  e.preventDefault();
  const id = btn.getAttribute('data-id') || btn.closest('.item')?.getAttribute('data-id');
  const link = btn.closest('.item')?.getAttribute('data-link');
  console.log('Add to cart clicked, id=', id, 'link=', link);

  if (!id) {
    console.warn('No data-id on button or parent item. Falling back to open link.');
    if (link) window.open(link, '_blank');
    return;
  }

  // Try direct SDK AddToCart with retry attempt
  const tryAdd = async () => {
    for (let i = 0; i < 6; i++) { // up to ~600ms
      if (typeof cartPaypal !== 'undefined' && cartPaypal.AddToCart) {
        try {
          cartPaypal.AddToCart({ id: id });
          console.log('Called cartPaypal.AddToCart for id', id);
          return true;
        } catch (err) {
          console.error('cartPaypal.AddToCart threw', err);
          return false;
        }
      }
      await new Promise(r => setTimeout(r, 100));
    }
    return false;
  }

  tryAdd().then(success => {
    if (!success) {
      console.warn('cartPaypal not available or AddToCart failed; opening fallback link');
      if (link) window.open(link, '_blank');
    }
  });
});
