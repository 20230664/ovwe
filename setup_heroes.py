import duckdb

def setup_hero_data():
    conn = duckdb.connect("overwatch.duckdb")

    conn.execute("DELETE FROM HeroAbility;")
    conn.execute("DELETE FROM Hero;")

    conn.execute("""
        INSERT OR IGNORE INTO Role VALUES
        ('tank', '돌격', '팀의 전방을 지키며 피해를 흡수하고, 적의 진입을 방해합니다.'),
        ('dps', '공격', '적을 공격하고 처치하여 전투 우위를 확보합니다.'),
        ('support', '지원', '아군을 치유하거나 강화하여 팀의 지속력을 높입니다.')
    """)
    conn.execute("INSERT INTO Hero SELECT * FROM read_csv('heroes.csv', header=True)")
    conn.execute("INSERT INTO HeroAbility SELECT * FROM read_csv('abilities.csv', header=True)")

    print("영웅/스킬 데이터 삽입 완료!")
    conn.close()

if __name__ == "__main__":
    setup_hero_data()