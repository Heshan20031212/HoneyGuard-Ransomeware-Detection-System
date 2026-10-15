from honeyguard.database.connection import get_db_connection

def inspect():
    conn = get_db_connection()
    cur = conn.cursor()
    for table in ['alerts', 'decoys', 'file_events', 'response_actions', 'benchmark_runs']:
        print(f"=== {table} ===")
        cur.execute(f"DESCRIBE {table}")
        for r in cur.fetchall():
            print(f"  {r['Field']} ({r['Type']})")
    cur.close()
    conn.close()

if __name__ == '__main__':
    inspect()
