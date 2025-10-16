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


let allItems = []; // store all items

async function loadItemsFromCSV() {
    const response = await fetch("items.csv");
    const text = await response.text();

    const lines = text.split("\n").filter(l => l.trim() !== "");
    const container = document.querySelector(".itemsContainer");
    const counter = document.getElementById("shopNumber");

    // ignore header
    allItems = lines.slice(1).map(line => {
        const [name, theme, price, image, link] = line.split(";");
        return { 
            name: name.trim(), 
            theme: theme.trim(), 
            price: parseFloat(price), 
            image: image.trim(), 
            link: link.trim() 
        };
    });

    counter.textContent = `${allItems.length} article${allItems.length > 1 ? "s" : ""}`;

    renderItems(allItems);
    createThemeButtons(allItems);
}

loadItemsFromCSV();

function renderItems(items) {
  const container = document.querySelector(".itemsContainer");
  container.innerHTML = ""; // clear previous items

  items.forEach(item => {
    const itemHTML = `
      <div class="item" data-link="${item.link}">
        <div class="itemIMGContainer">
          <img class="itemIMG" src="${item.image}" />
        </div>
        <div class="bottomTexts">
          <div class="bottomText1">
            <h2 class="title">${item.name}</h2>
            <h2 class="title">${item.theme}</h2>
          </div>
          <div class="bottomText2">
            <h2 class="price">${item.price.toFixed(2)}€</h2>
            <div class="stars">
              <span class="star filled">★</span>
              <span class="star filled">★</span>
              <span class="star filled">★</span>
              <span class="star filled">★</span>
              <span class="star">★</span>
            </div>
          </div>
        </div>
      </div>
    `;
    container.insertAdjacentHTML("beforeend", itemHTML);
  });
}

// Create theme filter buttons
function createThemeButtons(items) {
  const themeContainer = document.getElementById("themeButtons");
  themeContainer.innerHTML = "";

  // Count items per theme
  const themeCount = {};
  items.forEach(item => {
    themeCount[item.theme] = (themeCount[item.theme] || 0) + 1;
  });

  // "All" button
  const allBtn = document.createElement("button");
  allBtn.textContent = `Tous (${items.length})`;
  allBtn.onclick = () => renderItems(allItems);
  themeContainer.appendChild(allBtn);

  // Theme buttons
  Object.entries(themeCount).forEach(([theme, count]) => {
    const btn = document.createElement("button");
    btn.textContent = `${theme} (${count})`;
    btn.onclick = () => {
      const filtered = allItems.filter(i => i.theme === theme);
      renderItems(filtered);
    };
    themeContainer.appendChild(btn);
  });
}

// Bouton de filtre mobile
const filterToggle = document.createElement("button");
filterToggle.id = "filterToggle";
filterToggle.textContent = "Filtrer ▼";
document.querySelector(".mainPage").insertBefore(filterToggle, document.getElementById("themeButtons"));

filterToggle.addEventListener("click", () => {
  const themeButtons = document.getElementById("themeButtons");
  const isOpen = themeButtons.classList.toggle("open");
  filterToggle.textContent = isOpen ? "Filtrer ▲" : "Filtrer ▼";
});

const themeButtonsContainer = document.getElementById('themeButtons');

// Event delegation pour gérer les clics
themeButtonsContainer.addEventListener('click', (e) => {
  const clickedButton = e.target;
  if (clickedButton.tagName === 'BUTTON') {
    // Retire active de tous les boutons
    themeButtonsContainer.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
    // Ajoute active au bouton cliqué
    clickedButton.classList.add('active');
  }
});

// Active le premier bouton dès qu'il est généré
const observer = new MutationObserver(() => {
  const firstButton = themeButtonsContainer.querySelector('button');
  if (firstButton && !firstButton.classList.contains('active')) {
    firstButton.classList.add('active');
  }
});

// Observe les ajouts dans le conteneur
observer.observe(themeButtonsContainer, { childList: true });