
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import date

app = Flask(__name__)
app.secret_key = "kunci_aplikasi_penjualan"


def koneksi_database():
    try:
        koneksi = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_penjualan"
        )
        return koneksi

    except Error as e:
        print("Gagal terhubung ke database:", e)
        return None


@app.route("/")
def index():
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal. Periksa MySQL dan konfigurasi database."

    try:
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pelanggan")
        jumlah_pelanggan = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM barang")
        jumlah_barang = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transaksi")
        jumlah_transaksi = cursor.fetchone()[0]

        return render_template(
            "index.html",
            jumlah_pelanggan=jumlah_pelanggan,
            jumlah_barang=jumlah_barang,
            jumlah_transaksi=jumlah_transaksi
        )

    except Error as e:
        return f"Terjadi kesalahan saat membaca data: {e}"

    finally:
        if db.is_connected():
            cursor.close()
            db.close()

@app.route("/pelanggan")
def pelanggan():
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT id_pelanggan, nama_pelanggan, alamat, no_hp
            FROM pelanggan
            ORDER BY id_pelanggan
        """)

        data_pelanggan = cursor.fetchall()

        return render_template(
            "pelanggan/index.html",
            pelanggan=data_pelanggan
        )

    except Error as e:
        return f"Gagal mengambil data pelanggan: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/pelanggan/tambah", methods=["GET", "POST"])
def tambah_pelanggan():
    if request.method == "POST":
        id_pelanggan = request.form["id_pelanggan"].strip()
        nama = request.form["nama_pelanggan"].strip()
        alamat = request.form["alamat"].strip()
        no_hp = request.form["no_hp"].strip()

        if not id_pelanggan or not nama:
            flash("ID pelanggan dan nama wajib diisi.", "error")
            return redirect(url_for("tambah_pelanggan"))

        db = koneksi_database()

        if db is None:
            return "Koneksi database gagal."

        cursor = None

        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO pelanggan
                (id_pelanggan, nama_pelanggan, alamat, no_hp)
                VALUES (%s, %s, %s, %s)
            """, (id_pelanggan, nama, alamat, no_hp))

            db.commit()
            flash("Pelanggan berhasil ditambahkan.", "success")
            return redirect(url_for("pelanggan"))

        except Error as e:
            db.rollback()
            flash(f"Gagal menambahkan pelanggan: {e}", "error")

        finally:
            if cursor is not None:
                cursor.close()
            db.close()

    return render_template("pelanggan/tambah.html")


@app.route("/pelanggan/edit/<id_pelanggan>", methods=["GET", "POST"])
def edit_pelanggan(id_pelanggan):
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()

        if request.method == "POST":
            nama = request.form["nama_pelanggan"].strip()
            alamat = request.form["alamat"].strip()
            no_hp = request.form["no_hp"].strip()

            if not nama:
                flash("Nama pelanggan wajib diisi.", "error")
                return redirect(
                    url_for("edit_pelanggan",
                            id_pelanggan=id_pelanggan)
                )

            cursor.execute("""
                UPDATE pelanggan
                SET nama_pelanggan = %s, alamat = %s, no_hp = %s
                WHERE id_pelanggan = %s
            """, (nama, alamat, no_hp, id_pelanggan))

            db.commit()
            flash("Data pelanggan berhasil diperbarui.", "success")
            return redirect(url_for("pelanggan"))

        cursor.execute("""
            SELECT id_pelanggan, nama_pelanggan, alamat, no_hp
            FROM pelanggan
            WHERE id_pelanggan = %s
        """, (id_pelanggan,))

        data = cursor.fetchone()

        if data is None:
            return "Pelanggan tidak ditemukan.", 404

        return render_template("pelanggan/edit.html", data=data)

    except Error as e:
        db.rollback()
        return f"Gagal memproses data pelanggan: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/pelanggan/hapus/<id_pelanggan>", methods=["POST"])
def hapus_pelanggan(id_pelanggan):
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM pelanggan
            WHERE id_pelanggan = %s
        """, (id_pelanggan,))

        if cursor.rowcount == 0:
            flash("Pelanggan tidak ditemukan.", "error")
        else:
            db.commit()
            flash("Pelanggan berhasil dihapus.", "success")

    except Error as e:
        db.rollback()
        flash(
            f"Gagal menghapus pelanggan. "
            f"Pastikan pelanggan tidak digunakan dalam transaksi. Detail: {e}",
            "error"
        )

    finally:
        if cursor is not None:
            cursor.close()
        db.close()

    return redirect(url_for("pelanggan"))

@app.route("/barang")
def barang():
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT id_barang, nama_barang, harga, stok
            FROM barang
            ORDER BY id_barang
        """)

        data_barang = cursor.fetchall()

        return render_template(
            "barang/index.html",
            barang=data_barang
        )

    except Error as e:
        return f"Gagal mengambil data barang: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/barang/tambah", methods=["GET", "POST"])
def tambah_barang():
    if request.method == "POST":
        id_barang = request.form["id_barang"].strip()
        nama = request.form["nama_barang"].strip()
        harga = request.form["harga"].strip()
        stok = request.form["stok"].strip()

        if not id_barang or not nama or not harga or not stok:
            flash("Semua kolom wajib diisi.", "error")
            return redirect(url_for("tambah_barang"))

        try:
            harga = float(harga)
            stok = int(stok)

            if harga < 0 or stok < 0:
                raise ValueError

        except ValueError:
            flash("Harga dan stok harus berupa angka yang valid.", "error")
            return redirect(url_for("tambah_barang"))

        db = koneksi_database()

        if db is None:
            return "Koneksi database gagal."

        cursor = None

        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO barang (id_barang, nama_barang, harga, stok)
                VALUES (%s, %s, %s, %s)
            """, (id_barang, nama, harga, stok))

            db.commit()
            flash("Barang berhasil ditambahkan.", "success")
            return redirect(url_for("barang"))

        except Error as e:
            db.rollback()
            flash(f"Gagal menambahkan barang: {e}", "error")

        finally:
            if cursor is not None:
                cursor.close()
            db.close()

    return render_template("barang/tambah.html")


@app.route("/barang/edit/<id_barang>", methods=["GET", "POST"])
def edit_barang(id_barang):
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()

        if request.method == "POST":
            nama = request.form["nama_barang"].strip()
            harga = request.form["harga"].strip()
            stok = request.form["stok"].strip()

            if not nama or not harga or not stok:
                flash("Semua kolom wajib diisi.", "error")
                return redirect(
                    url_for("edit_barang", id_barang=id_barang)
                )

            try:
                harga = float(harga)
                stok = int(stok)

                if harga < 0 or stok < 0:
                    raise ValueError

            except ValueError:
                flash("Harga dan stok harus berupa angka yang valid.", "error")
                return redirect(
                    url_for("edit_barang", id_barang=id_barang)
                )

            cursor.execute("""
                UPDATE barang
                SET nama_barang = %s, harga = %s, stok = %s
                WHERE id_barang = %s
            """, (nama, harga, stok, id_barang))

            db.commit()
            flash("Data barang berhasil diperbarui.", "success")
            return redirect(url_for("barang"))

        cursor.execute("""
            SELECT id_barang, nama_barang, harga, stok
            FROM barang
            WHERE id_barang = %s
        """, (id_barang,))

        data = cursor.fetchone()

        if data is None:
            return "Barang tidak ditemukan.", 404

        return render_template("barang/edit.html", data=data)

    except Error as e:
        db.rollback()
        return f"Gagal memproses data barang: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/barang/hapus/<id_barang>", methods=["POST"])
def hapus_barang(id_barang):
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM barang
            WHERE id_barang = %s
        """, (id_barang,))

        if cursor.rowcount == 0:
            flash("Barang tidak ditemukan.", "error")
        else:
            db.commit()
            flash("Barang berhasil dihapus.", "success")

    except Error as e:
        db.rollback()
        flash(
            f"Gagal menghapus barang. Barang mungkin sudah digunakan "
            f"dalam transaksi. Detail: {e}",
            "error"
        )

    finally:
        if cursor is not None:
            cursor.close()
        db.close()

    return redirect(url_for("barang"))

def buat_id_transaksi(cursor):
    cursor.execute("""
        SELECT id_transaksi
        FROM transaksi
        WHERE id_transaksi LIKE 'TRX%'
        ORDER BY id_transaksi DESC
        LIMIT 1
    """)
    hasil = cursor.fetchone()

    nomor = int(hasil[0][3:]) + 1 if hasil else 1
    return f"TRX{nomor:07d}"


def buat_id_detail(cursor):
    cursor.execute("""
        SELECT id_detail
        FROM detail_transaksi
        WHERE id_detail LIKE 'DTL%'
        ORDER BY id_detail DESC
        LIMIT 1
    """)
    hasil = cursor.fetchone()

    nomor = int(hasil[0][3:]) + 1 if hasil else 1
    return f"DTL{nomor:07d}"

@app.route("/transaksi")
def transaksi():
    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                t.id_transaksi,
                t.tanggal,
                p.nama_pelanggan,
                COALESCE(SUM(dt.subtotal), 0) AS total
            FROM transaksi t
            JOIN pelanggan p
                ON t.id_pelanggan = p.id_pelanggan
            LEFT JOIN detail_transaksi dt
                ON t.id_transaksi = dt.id_transaksi
            GROUP BY
                t.id_transaksi,
                t.tanggal,
                p.nama_pelanggan
            ORDER BY t.tanggal DESC
        """)

        data_transaksi = cursor.fetchall()

        return render_template(
            "transaksi/index.html",
            transaksi=data_transaksi
        )

    except Error as e:
        return f"Gagal mengambil data transaksi: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/transaksi/tambah", methods=["GET", "POST"])
def tambah_transaksi():

    db = koneksi_database()

    if db is None:
        return "Koneksi database gagal."

    cursor = None

    try:
        cursor = db.cursor()

        if request.method == "POST":

            id_pelanggan = request.form.get("id_pelanggan", "").strip()
            daftar_barang = request.form.getlist("id_barang[]")
            daftar_jumlah = request.form.getlist("jumlah[]")
            tanggal_transaksi = request.form.get("tanggal") or date.today()

            if not id_pelanggan:
                flash("Pilih pelanggan terlebih dahulu.", "error")
                return redirect(url_for("tambah_transaksi"))

            if not daftar_barang:
                flash("Tambahkan minimal satu barang.", "error")
                return redirect(url_for("tambah_transaksi"))

            if len(daftar_barang) != len(daftar_jumlah):
                flash("Data barang tidak valid.", "error")
                return redirect(url_for("tambah_transaksi"))

            jumlah_per_barang = {}

            for id_barang, jumlah_text in zip(daftar_barang, daftar_jumlah):

                if not id_barang:
                    continue

                try:
                    jumlah = int(jumlah_text)
                except (ValueError, TypeError):
                    flash("Jumlah barang harus berupa angka.", "error")
                    return redirect(url_for("tambah_transaksi"))

                if jumlah <= 0:
                    flash("Jumlah barang harus lebih dari 0.", "error")
                    return redirect(url_for("tambah_transaksi"))

                jumlah_per_barang[id_barang] = (
                    jumlah_per_barang.get(id_barang, 0) + jumlah
                )

            if not jumlah_per_barang:
                flash("Pilih minimal satu barang.", "error")
                return redirect(url_for("tambah_transaksi"))

            db.start_transaction()

            cursor.execute("""
                SELECT id_pelanggan
                FROM pelanggan
                WHERE id_pelanggan = %s
            """, (id_pelanggan,))

            if cursor.fetchone() is None:
                db.rollback()
                flash("Pelanggan tidak ditemukan.", "error")
                return redirect(url_for("tambah_transaksi"))

            daftar_item = []
            total_transaksi = 0

            for id_barang, jumlah in jumlah_per_barang.items():

                cursor.execute("""
                    SELECT nama_barang, harga, stok
                    FROM barang
                    WHERE id_barang = %s
                    FOR UPDATE
                """, (id_barang,))

                barang = cursor.fetchone()

                if barang is None:
                    db.rollback()
                    flash("Barang tidak ditemukan.", "error")
                    return redirect(url_for("tambah_transaksi"))

                nama_barang, harga, stok = barang

                if jumlah > stok:
                    db.rollback()
                    flash(
                        f"Stok {nama_barang} tidak mencukupi. "
                        f"Stok tersedia: {stok}.",
                        "error"
                    )
                    return redirect(url_for("tambah_transaksi"))

                subtotal = harga * jumlah
                total_transaksi += subtotal

                daftar_item.append({
                    "id_barang": id_barang,
                    "jumlah": jumlah,
                    "subtotal": subtotal
                })

            id_transaksi = buat_id_transaksi(cursor)

            cursor.execute("""
                INSERT INTO transaksi
                (id_transaksi, tanggal, id_pelanggan)
                VALUES (%s, %s, %s)
            """, (
                id_transaksi,
                tanggal_transaksi,
                id_pelanggan
            ))

            for item in daftar_item:

                id_detail = buat_id_detail(cursor)

                cursor.execute("""
                    INSERT INTO detail_transaksi
                    (id_detail, id_transaksi, id_barang, jumlah, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_detail,
                    id_transaksi,
                    item["id_barang"],
                    item["jumlah"],
                    item["subtotal"]
                ))

                cursor.execute("""
                    UPDATE barang
                    SET stok = stok - %s
                    WHERE id_barang = %s
                """, (
                    item["jumlah"],
                    item["id_barang"]
                ))

            db.commit()

            flash(
                f"Transaksi {id_transaksi} berhasil disimpan. "
                f"Total: Rp {total_transaksi:,.0f}",
                "success"
            )

            return redirect(url_for("transaksi"))

        cursor.execute("""
            SELECT id_pelanggan, nama_pelanggan
            FROM pelanggan
            ORDER BY nama_pelanggan
        """)

        data_pelanggan = cursor.fetchall()

        cursor.execute("""
            SELECT id_barang, nama_barang, harga, stok
            FROM barang
            WHERE stok > 0
            ORDER BY nama_barang
        """)

        data_barang = cursor.fetchall()

        return render_template(
            "transaksi/tambah.html",
            pelanggan=data_pelanggan,
            barang=data_barang,
            tanggal_hari_ini=date.today().isoformat()
        )

    except Error as e:
        db.rollback()
        flash(f"Gagal menyimpan transaksi: {e}", "error")
        return redirect(url_for("tambah_transaksi"))

    finally:
        if cursor is not None:
            cursor.close()
        db.close()


@app.route("/laporan")
def laporan():
    db = koneksi_database()

    if db is None:
        flash("Koneksi database gagal.", "error")
        return redirect(url_for("index"))

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            t.id_transaksi,
            t.tanggal,
            p.nama_pelanggan,
            COALESCE(SUM(dt.subtotal), 0) AS total
        FROM transaksi t
        JOIN pelanggan p
            ON t.id_pelanggan = p.id_pelanggan
        LEFT JOIN detail_transaksi dt
            ON t.id_transaksi = dt.id_transaksi
        GROUP BY
            t.id_transaksi,
            t.tanggal,
            p.nama_pelanggan
        ORDER BY t.tanggal DESC
    """)

    data_laporan = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "laporan/index.html",
        laporan=data_laporan
    )


@app.route("/laporan/detail/<id_transaksi>")
def detail_laporan(id_transaksi):
    db = koneksi_database()

    if db is None:
        flash("Koneksi database gagal.", "error")
        return redirect(url_for("laporan"))

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            t.id_transaksi,
            t.tanggal,
            p.nama_pelanggan,
            p.alamat,
            p.no_hp
        FROM transaksi t
        JOIN pelanggan p
            ON t.id_pelanggan = p.id_pelanggan
        WHERE t.id_transaksi = %s
    """, (id_transaksi,))

    data_transaksi = cursor.fetchone()

    if data_transaksi is None:
        cursor.close()
        db.close()
        flash("Data transaksi tidak ditemukan.", "error")
        return redirect(url_for("laporan"))

    cursor.execute("""
        SELECT
            b.nama_barang,
            b.harga,
            dt.jumlah,
            dt.subtotal
        FROM detail_transaksi dt
        JOIN barang b
            ON dt.id_barang = b.id_barang
        WHERE dt.id_transaksi = %s
    """, (id_transaksi,))

    detail_barang = cursor.fetchall()

    total = sum(float(item[3]) for item in detail_barang)

    cursor.close()
    db.close()

    return render_template(
        "laporan/detail.html",
        transaksi=data_transaksi,
        detail_barang=detail_barang,
        total=total
    )

@app.route("/laporan/rekapitulasi")
def rekapitulasi_laporan():
    db = koneksi_database()

    if db is None:
        flash("Koneksi database gagal.", "error")
        return redirect(url_for("laporan"))

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            COUNT(DISTINCT t.id_transaksi) AS jumlah_transaksi,
            COALESCE(SUM(dt.jumlah), 0) AS total_barang_terjual,
            COALESCE(SUM(dt.subtotal), 0) AS total_pendapatan
        FROM transaksi t
        LEFT JOIN detail_transaksi dt
            ON t.id_transaksi = dt.id_transaksi
    """)

    rekap = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "laporan/rekapitulasi.html",
        rekap=rekap
    )

if __name__ == "__main__":
    app.run(debug=True)