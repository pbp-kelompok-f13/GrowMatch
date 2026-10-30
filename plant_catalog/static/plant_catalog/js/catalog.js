document.addEventListener("DOMContentLoaded", function () {
    const filterForm = document.querySelector(".pc-toolbar");
    const filterToggle = document.getElementById("filterToggle");
    const filterToggleText = document.getElementById("filterToggleText");
    const filterPanel = document.getElementById("filterPanel");
    const searchInput = document.querySelector(".pc-search-input");
    const filterSelects = filterForm.querySelectorAll("select");

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
                filterForm.requestSubmit();
            }, 500);
        });
    }

    // Terapkan filter otomatis saat pilihan berubah
    filterSelects.forEach(function (select) {
        select.addEventListener("change", function () {
            filterForm.requestSubmit();
        });
    });
});