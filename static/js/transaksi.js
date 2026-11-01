
document.addEventListener("DOMContentLoaded", function () {

    const daftarBarang = document.getElementById("daftar-barang");
    const tombolTambah = document.getElementById("tombol-tambah");
    const totalElement = document.getElementById("total");
    const templateBarang = document.getElementById("opsi-barang");

    function formatRupiah(angka) {
        return "Rp " + Number(angka).toLocaleString("id-ID");
    }

    function tambahBarang() {
        const row = document.createElement("div");
        row.className = "item-row";

        const pilihanBarang = document.createElement("select");
        pilihanBarang.name = "id_barang[]";
        pilihanBarang.className = "pilih-barang";
        pilihanBarang.required = true;

        const pilihanAwal = document.createElement("option");
        pilihanAwal.value = "";
        pilihanAwal.textContent = "-- Pilih Barang --";
        pilihanBarang.appendChild(pilihanAwal);

        // Salin pilihan barang dari template HTML
        const opsi = templateBarang.content.cloneNode(true);
        pilihanBarang.appendChild(opsi);

        const inputJumlah = document.createElement("input");
        inputJumlah.type = "number";
        inputJumlah.name = "jumlah[]";
        inputJumlah.className = "jumlah";
        inputJumlah.min = "1";
        inputJumlah.value = "1";
        inputJumlah.required = true;

        const subtotal = document.createElement("div");
        subtotal.className = "subtotal";
        subtotal.textContent = formatRupiah(0);

        const kolomBarang = document.createElement("div");
        const labelBarang = document.createElement("label");
        labelBarang.textContent = "Barang";
        kolomBarang.appendChild(labelBarang);
        kolomBarang.appendChild(pilihanBarang);

        const kolomJumlah = document.createElement("div");
        const labelJumlah = document.createElement("label");
        labelJumlah.textContent = "Jumlah";
        kolomJumlah.appendChild(labelJumlah);
        kolomJumlah.appendChild(inputJumlah);

        const kolomSubtotal = document.createElement("div");
        const labelSubtotal = document.createElement("label");
        labelSubtotal.textContent = "Subtotal";
        kolomSubtotal.appendChild(labelSubtotal);
        kolomSubtotal.appendChild(subtotal);

        const kolomHapus = document.createElement("div");
        const tombolHapus = document.createElement("button");
        tombolHapus.type = "button";
        tombolHapus.className = "btn btn-danger";
        tombolHapus.textContent = "Hapus";

        kolomHapus.appendChild(tombolHapus);

        row.appendChild(kolomBarang);
        row.appendChild(kolomJumlah);
        row.appendChild(kolomSubtotal);
        row.appendChild(kolomHapus);

        daftarBarang.appendChild(row);

        pilihanBarang.addEventListener("change", hitungTotal);
        inputJumlah.addEventListener("input", hitungTotal);

        tombolHapus.addEventListener("click", function () {
            row.remove();
            hitungTotal();
        });

        hitungTotal();
    }

    function hitungTotal() {
        let total = 0;

        const semuaBaris = daftarBarang.querySelectorAll(".item-row");

        semuaBaris.forEach(function (row) {

            const pilihan = row.querySelector(".pilih-barang");
            const jumlahInput = row.querySelector(".jumlah");
            const subtotalBox = row.querySelector(".subtotal");

            const option = pilihan.options[pilihan.selectedIndex];

            const harga = Number(option.dataset.harga || 0);
            const stok = Number(option.dataset.stok || 0);
            const jumlah = Number(jumlahInput.value || 0);

            const subtotal = harga * jumlah;

            subtotalBox.textContent = formatRupiah(subtotal);

            if (pilihan.value !== "") {
                jumlahInput.max = stok;
            } else {
                jumlahInput.removeAttribute("max");
            }

            if (pilihan.value !== "" && jumlah > stok) {
                jumlahInput.setCustomValidity(
                    "Jumlah melebihi stok yang tersedia."
                );
            } else {
                jumlahInput.setCustomValidity("");
            }

            total += subtotal;
        });

        totalElement.textContent = formatRupiah(total);
    }

    tombolTambah.addEventListener("click", tambahBarang);
    
    tambahBarang();

});
