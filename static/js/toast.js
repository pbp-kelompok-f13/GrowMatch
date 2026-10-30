let toastTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toastComponent = document.getElementById("toast-component");
    const toastTitle = document.getElementById("toast-title");
    const toastMessage = document.getElementById("toast-message");
    const toastIcon = document.getElementById("toast-icon");

    if (!toastComponent) return;

    // Hapus class tipe sebelumnya
    toastComponent.classList.remove("toast-success", "toast-error", "toast-normal");

    // Terapkan class dan icon berdasarkan tipe
    if (type === "success") {
        toastComponent.classList.add("toast-success");
        toastIcon.textContent = "✓";
    } else if (type === "error") {
        toastComponent.classList.add("toast-error");
        toastIcon.textContent = "!";
    } else {
        toastComponent.classList.add("toast-normal");
        toastIcon.textContent = "i";
    }

    // Perbarui konten teks
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Batalkan timer sebelumnya jika toast masih tampil
    clearTimeout(toastTimer);

    // Tampilkan popover dan jalankan animasi muncul
    if (!toastComponent.matches(":popover-open")) {
        toastComponent.showPopover();
        void toastComponent.offsetHeight; // Paksa browser menghitung style agar transisi berjalan
    }

    toastComponent.classList.remove("toast-hidden");
    toastComponent.classList.add("toast-show");

    // Hilang otomatis setelah durasi selesai
    toastTimer = setTimeout(hideToast, duration);
}

function hideToast() {
    const toastComponent = document.getElementById("toast-component");

    if (!toastComponent) return;

    // Batalkan timer yang masih berjalan
    clearTimeout(toastTimer);

    // Jalankan animasi keluar
    toastComponent.classList.remove("toast-show");
    toastComponent.classList.add("toast-hidden");

    // Tutup popover setelah animasi selesai
    toastTimer = setTimeout(() => {
        if (toastComponent.matches(":popover-open")) {
            toastComponent.hidePopover();
        }
    }, 200);
}