document.addEventListener("DOMContentLoaded", function () {
    const filterForm = document.querySelector(".pc-toolbar");
    const ajaxUrl = filterForm.dataset.ajaxUrl;
    const filterToggle = document.getElementById("filterToggle");
    const filterToggleText = document.getElementById("filterToggleText");
    const filterPanel = document.getElementById("filterPanel");
    const searchInput = document.querySelector(".pc-search-input");
    const filterSelects = filterForm.querySelectorAll("select");
    const plantResults = document.getElementById("plantResults");

    let searchTimer;

    // Buka atau tutup panel filter
    function setFilterOpen(open) {
        if (open) {
            filterPanel.removeAttribute("hidden");
            filterToggleText.textContent = "Hide filters";
            filterToggle.setAttribute("aria-expanded", "true");
        } else {
            filterPanel.setAttribute("hidden", "");
            filterToggleText.textContent = "Filters";
            filterToggle.setAttribute("aria-expanded", "false");
        }
    }

    // Ambil hasil tanaman dengan AJAX tanpa reload halaman
    async function updatePlants() {
        const params = new URLSearchParams(new FormData(filterForm));

        try {
            const response = await fetch(`${ajaxUrl}?${params.toString()}`);

            if (!response.ok) {
                throw new Error("Failed to load plants.");
            }

            const html = await response.text();
            plantResults.innerHTML = html;

            // Perbarui URL browser tanpa reload halaman
            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.replaceState({}, "", newUrl);
        } catch (error) {
            console.error(error);
        }
    }

    // Toggle filter saat tombol Filters ditekan
    filterToggle.addEventListener("click", function () {
        setFilterOpen(filterPanel.hasAttribute("hidden"));
    });

    // Biarkan panel terbuka kalau ada filter aktif
    const hasActiveFilter = Array.from(filterSelects).some(function (select) {
        return select.value !== "";
    });

    if (hasActiveFilter) {
        setFilterOpen(true);
    }

    // Search otomatis setelah user berhenti mengetik
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            clearTimeout(searchTimer);

            searchTimer = setTimeout(function () {
                updatePlants();
            }, 500);
        });
    }

    // Terapkan filter otomatis saat pilihan berubah
    filterSelects.forEach(function (select) {
        select.addEventListener("change", function () {
            updatePlants();
        });
    });

    // Tombol Apply juga menggunakan AJAX
    filterForm.addEventListener("submit", function (event) {
        event.preventDefault();
        updatePlants();
    });
});