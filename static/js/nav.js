const header = document.querySelector(".site-header");
const navToggle = document.querySelector(".nav-toggle");

function setMenuOpen(open) {
  header.classList.toggle("is-open", open);
  navToggle.setAttribute("aria-expanded", String(open));
  navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
}

if (header && navToggle) {
  navToggle.addEventListener("click", () => {
    setMenuOpen(!header.classList.contains("is-open"));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && header.classList.contains("is-open")) {
      setMenuOpen(false);
      navToggle.focus();
    }
  });
}
