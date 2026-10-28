// AJAX untuk form rekomendasi (create/edit) dan tombol hapus.
// Tanpa JavaScript, form tetap jalan lewat submit biasa.

const AJAX_HEADERS = { "X-Requested-With": "XMLHttpRequest" };

function showErrors(form, errors) {
    form.querySelectorAll("[data-error-for]").forEach((el) => {
        const messages = errors[el.dataset.errorFor] || [];
        el.textContent = messages.join(" ");
    });
}

async function submitRecommendationForm(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector("button[type=submit]");
    if (!button) return;

    const originalLabel = button.innerHTML;
    button.disabled = true;
    button.textContent = "Mencocokkan...";
    showErrors(form, {});

    try {
        const response = await fetch(form.action, {
            method: "POST",
            headers: AJAX_HEADERS,
            body: new FormData(form),
        });
        const data = await response.json();
        if (data.ok) {
            window.location.href = data.redirect_url;
            return;
        }
        showErrors(form, data.errors || {});
    } catch (error) {
        showErrors(form, { __all__: ["Gagal mengirim data. Cek koneksimu lalu coba lagi."] });
    }

    button.disabled = false;
    button.innerHTML = originalLabel;
}

async function submitDelete(event) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!window.confirm("Hapus rekomendasi ini?")) return;

    try {
        const response = await fetch(form.action, {
            method: "POST",
            headers: AJAX_HEADERS,
            body: new FormData(form),
        });
        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        window.alert("Gagal menghapus. Coba lagi.");
        return;
    }

    const item = form.closest("[data-history-item]");
    if (!item) {
        // Dihapus dari halaman detail, balik ke riwayat
        window.location.href = "/recommendation/history/";
        return;
    }
    item.remove();
    if (!document.querySelector("[data-history-item]")) {
        document.querySelector("[data-history-empty]").hidden = false;
    }
}

function renderPlantCard(plant) {
    const card = document.createElement("article");
    card.className = "card rec-plant";

    if (plant.image_url) {
        const img = document.createElement("img");
        img.src = plant.image_url;
        img.alt = plant.name;
        img.loading = "lazy";
        card.append(img);
    }

    const match = document.createElement("span");
    match.className = "rec-match";
    match.textContent = `${plant.match_percent}% match`;

    const name = document.createElement("h3");
    name.textContent = plant.name;
    card.append(match, name);

    if (plant.scientific_name) {
        const scientific = document.createElement("p");
        scientific.className = "muted";
        const italic = document.createElement("i");
        italic.textContent = plant.scientific_name;
        scientific.append(italic);
        card.append(scientific);
    }

    const reasons = document.createElement("ul");
    reasons.className = "rec-reasons";
    plant.reasons.forEach((reason) => {
        const item = document.createElement("li");
        item.textContent = reason;
        reasons.append(item);
    });
    card.append(reasons);
    return card;
}

async function filterPlants(form) {
    const params = new URLSearchParams(new FormData(form));
    const list = document.querySelector("[data-plant-list]");
    const empty = document.querySelector("[data-plant-empty]");

    list.setAttribute("aria-busy", "true");
    try {
        const response = await fetch(`${form.dataset.jsonUrl}?${params}`, { headers: AJAX_HEADERS });
        if (!response.ok) throw new Error(response.statusText);
        const plants = await response.json();
        list.replaceChildren(...plants.map(renderPlantCard));
        empty.hidden = plants.length > 0;
        window.history.replaceState(null, "", `?${params}`);
    } catch (error) {
        window.alert("Gagal memuat tanaman. Coba lagi.");
    }
    list.removeAttribute("aria-busy");
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-plant-filter]").forEach((form) => {
        form.addEventListener("change", () => filterPlants(form));
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            filterPlants(form);
        });
    });
    document.querySelectorAll("[data-ajax-form]").forEach((form) => {
        form.addEventListener("submit", submitRecommendationForm);
    });
    document.querySelectorAll("[data-ajax-delete]").forEach((form) => {
        form.addEventListener("submit", submitDelete);
    });
});
