import duckdb

def init_db():
    conn = duckdb.connect("overwatch.duckdb")

    tables = [
        'Performance_Segment',
        'Performance', 
        'ErHistory', 
        'Player_Role', 
        'HeroAbility', 
        'Match_info', 
        'Hero', 
        'Map', 
        'player', 
        'Role', 
        'Mode'
    ]
    for t in tables:
         conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.execute("DROP SEQUENCE IF EXISTS seq_perf_id")
    conn.execute("DROP SEQUENCE IF EXISTS seq_history_id")
    conn.execute("DROP SEQUENCE IF EXISTS seq_ability_id")

    conn.execute("CREATE SEQUENCE seq_perf_id START 1")
    conn.execute("CREATE SEQUENCE seq_history_id START 1")
    conn.execute("CREATE SEQUENCE seq_ability_id START 1")


    # 사용자
    conn.execute("""
        CREATE TABLE player (
            BattleTag VARCHAR PRIMARY KEY
        )
    """)
    # 역할군
    conn.execute("""
        CREATE TABLE Role (
            role_id VARCHAR PRIMARY KEY,
            role_name VARCHAR,
            description VARCHAR
        )
    """)
    # 맵 모드
    conn.execute("""
        CREATE TABLE Mode (
            mode_id VARCHAR PRIMARY KEY,
            mode_name VARCHAR,
            description VARCHAR
        )
    """)
    # 영웅
    conn.execute("""
        CREATE TABLE Hero (
            Hero_id VARCHAR PRIMARY KEY,
            hero_name VARCHAR,
            role_id VARCHAR,
            FOREIGN KEY (role_id) REFERENCES Role(role_id)
        )
    """)
    # 영웅 능력
    conn.execute("""
        CREATE TABLE HeroAbility (
            ability_id INTEGER PRIMARY KEY DEFAULT nextval('seq_ability_id'),
            Hero_id VARCHAR,
            ability_name VARCHAR,
            cooldown VARCHAR,
            FOREIGN KEY (Hero_id) REFERENCES Hero(Hero_id)
        )
    """)
    # 맵
    conn.execute("""
        CREATE TABLE Map (
            map_id VARCHAR PRIMARY KEY,
            mode_id VARCHAR,
            map_name VARCHAR,
            region VARCHAR,
            FOREIGN KEY (mode_id) REFERENCES Mode(mode_id)
        )
    """)
    # 경기 (result 없음 -> Performance로 이동)
    conn.execute("""
        CREATE TABLE Match_info (
            Match_id VARCHAR PRIMARY KEY,
            map_id VARCHAR,
            play_at TIMESTAMP,
            result VARCHAR,   -- ← 여기로 이동
            FOREIGN KEY (map_id) REFERENCES Map(map_id)
        )
    """)
    # 플레이어 역할 점수
    conn.execute("""
        CREATE TABLE Player_Role (
            BattleTag VARCHAR,
            role_id VARCHAR,
            current_er INTEGER,
            PRIMARY KEY (BattleTag, role_id),
            FOREIGN KEY (BattleTag) REFERENCES player(BattleTag),
            FOREIGN KEY (role_id) REFERENCES Role(role_id)
        )
    """)
    # 점수 변동 이력
    conn.execute("""
        CREATE TABLE ErHistory (
            history_id INTEGER PRIMARY KEY DEFAULT nextval('seq_history_id'),
            BattleTag VARCHAR,
            role_id VARCHAR,
            changed_er INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (BattleTag) REFERENCES player(BattleTag),
            FOREIGN KEY (role_id) REFERENCES Role(role_id)
        )
    """)
    # 퍼포먼스 (perf_id, result, switched_at 추가 / er_change 제거 / Performance_Segment 통합)
    conn.execute("""
        CREATE TABLE Performance (
            perf_id INTEGER PRIMARY KEY DEFAULT nextval('seq_perf_id'),
            BattleTag VARCHAR,
            Hero_id VARCHAR,
            Match_id VARCHAR,
            kill_count INTEGER,
            deaths INTEGER,
            damage INTEGER,
            healing INTEGER,
            play_time INTEGER,
            switched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (BattleTag) REFERENCES player(BattleTag),
            FOREIGN KEY (Hero_id) REFERENCES Hero(Hero_id),
            FOREIGN KEY (Match_id) REFERENCES Match_info(Match_id)
        )
    """)
    print("데이터베이스 초기화 성공!")
    conn.close()

if __name__ == "__main__":
    init_db()