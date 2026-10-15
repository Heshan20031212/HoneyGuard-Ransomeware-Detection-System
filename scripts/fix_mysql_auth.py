from honeyguard.database.connection import get_db_connection

def fix_auth():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'root'")
    cur.execute("ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'root'")
    cur.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION")
    cur.execute("ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'")
    cur.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION")
    cur.execute("FLUSH PRIVILEGES")
    
    cur.execute("SELECT user, host, plugin FROM mysql.user WHERE user = 'root'")
    print("Updated root users:")
    for u in cur.fetchall():
        print(u)

    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_auth()
