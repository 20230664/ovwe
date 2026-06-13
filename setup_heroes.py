import duckdb

def setup_hero_data():
    conn = duckdb.connect("overwatch.duckdb")

    conn.execute("DELETE FROM HeroAbility;")
    conn.execute("DELETE FROM Hero;")

    conn.execute("INSERT OR IGNORE INTO Role VALUES ('tank', '돌격'), ('dps', '공격'), ('support', '지원')")

    conn.execute("INSERT INTO Hero SELECT * FROM read_csv('heroes.csv', header=True)")
    conn.execute("INSERT INTO HeroAbility SELECT * FROM read_csv('abilities.csv', header=True)")

    print("영웅/스킬 데이터 삽입 완료!")
    conn.close()

if __name__ == "__main__":
    setup_hero_data()