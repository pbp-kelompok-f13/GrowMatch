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
    button.textContent = button.dataset.submitLabel;
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

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-ajax-form]").forEach((form) => {
        form.addEventListener("submit", submitRecommendationForm);
    });
    document.querySelectorAll("[data-ajax-delete]").forEach((form) => {
        form.addEventListener("submit", submitDelete);
    });
});
