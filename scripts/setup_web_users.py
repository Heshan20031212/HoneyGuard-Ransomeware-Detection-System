import subprocess
from honeyguard.database.connection import get_db_connection

def setup_users():
    # Generate bcrypt hashes via PHP
    cmd_admin = ['C:\\xampp\\php\\php.exe', '-r', 'echo password_hash("admin123", PASSWORD_DEFAULT);']
    admin_hash = subprocess.check_output(cmd_admin).decode('utf-8').strip()

    cmd_user = ['C:\\xampp\\php\\php.exe', '-r', 'echo password_hash("user123", PASSWORD_DEFAULT);']
    user_hash = subprocess.check_output(cmd_user).decode('utf-8').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cur.execute("""
    INSERT INTO users (username, password_hash, role, full_name, email, is_active)
    VALUES 
        ('admin', %s, 'admin', 'System Administrator', 'admin@honeyguard.local', 1),
        ('user', %s, 'user', 'Security Analyst', 'analyst@honeyguard.local', 1)
    ON DUPLICATE KEY UPDATE 
        password_hash=VALUES(password_hash),
        role=VALUES(role),
        full_name=VALUES(full_name),
        is_active=1;
    """, (admin_hash, user_hash))

    conn.commit()
    cur.execute("SELECT id, username, role, full_name, email, is_active FROM users")
    rows = cur.fetchall()
    print("Seeded users successfully:")
    for r in rows:
        print(f" - ID: {r['id']}, User: {r['username']}, Role: {r['role']}, Name: {r['full_name']}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    setup_users()
