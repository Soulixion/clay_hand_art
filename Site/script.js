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
