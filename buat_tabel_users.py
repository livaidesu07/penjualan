from app import koneksi_database

db = koneksi_database()

if db:
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            nama_lengkap VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """)

    db.commit()

    print("Tabel users berhasil dibuat di Aiven!")

    cursor.close()
    db.close()
else:
    print("Gagal terhubung ke database Aiven.")