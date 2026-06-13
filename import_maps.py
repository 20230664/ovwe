import duckdb

def import_data():
    conn = duckdb.connect("overwatch.duckdb")

    # 1. 모드 데이터 삽입 (컬럼 명시)
    conn.execute("""
        INSERT OR IGNORE INTO Mode (mode_id, mode_name, description)
        SELECT mode_id, mode_name, description
        FROM read_csv('modes.csv', header=True)
    """)

    # 2. 맵 데이터 삽입 (컬럼 명시)
    conn.execute("""
        INSERT OR IGNORE INTO Map (map_id, mode_id, map_name, region)
        SELECT map_id, mode_id, map_name, region
        FROM read_csv('maps.csv', header=True)
    """)

    print("--- Mode 테이블 ---")
    print(conn.execute("SELECT * FROM Mode").df())

    print("\n--- Map 테이블 ---")
    print(conn.execute("SELECT * FROM Map").df())
    print("모든 데이터 입력 완료!")
    conn.close()

if __name__ == "__main__":
    import_data()