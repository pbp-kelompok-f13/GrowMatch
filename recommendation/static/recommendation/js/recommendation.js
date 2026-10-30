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
    button.textContent = "Matching...";
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
        showErrors(form, { __all__: ["Could not send your answers. Check your connection and try again."] });
    }

    button.disabled = false;
    button.innerHTML = originalLabel;
}

async function submitDelete(event) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!window.confirm("Delete this recommendation?")) return;

    try {
        const response = await fetch(form.action, {
            method: "POST",
            headers: AJAX_HEADERS,
            body: new FormData(form),
        });
        if (!response.ok) throw new Error(response.statusText);
    } catch (error) {
        window.alert("Could not delete. Please try again.");
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

function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

function renderPlantCard(plant) {
    const card = createElement("article", "rec-plant");
    const link = createElement("a", "rec-plant-link");
    link.href = plant.detail_url;

    const imageWrap = createElement("div", "rec-plant-image");
    if (plant.image_url) {
        const img = document.createElement("img");
        img.src = plant.image_url;
        img.alt = plant.name;
        img.loading = "lazy";
        imageWrap.append(img);
    }
    imageWrap.append(createElement("span", "rec-match", `${plant.match_percent}% match`));
    link.append(imageWrap, createElement("h3", "", plant.name));
    card.append(link);

    if (plant.scientific_name) {
        card.append(createElement("p", "rec-plant-latin", plant.scientific_name));
    }

    const reasons = createElement("ul", "rec-reasons");
    plant.reasons.forEach((reason) => reasons.append(createElement("li", "", reason)));
    card.append(reasons);
    return card;
}

function updateLookup(lookup) {
    const message = document.querySelector("[data-lookup-message]");
    const left = document.querySelector("[data-lookup-left]");
    message.textContent = lookup.message;
    message.hidden = !lookup.message;
    const noun = lookup.lookups_left === 1 ? "search" : "searches";
    left.textContent = `${lookup.lookups_left} extra ${noun} left today`;
    left.hidden = !lookup.enabled;
}

async function filterPlants(form) {
    const params = new URLSearchParams(new FormData(form));
    const list = document.querySelector("[data-plant-list]");
    const empty = document.querySelector("[data-plant-empty]");

    list.setAttribute("aria-busy", "true");
    try {
        const response = await fetch(`${form.dataset.jsonUrl}?${params}`, { headers: AJAX_HEADERS });
        if (!response.ok) throw new Error(response.statusText);
        const data = await response.json();
        const plants = data.plants;
        list.replaceChildren(...plants.map(renderPlantCard));
        empty.hidden = plants.length > 0;
        const count = document.querySelector("[data-plant-count]");
        const noun = plants.length === 1 ? "plant" : "plants";
        count.textContent = `${plants.length} ${noun} sorted by best match`;
        updateLookup(data.lookup);
        window.history.replaceState(null, "", `?${params}`);
    } catch (error) {
        window.alert("Could not load plants. Please try again.");
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
