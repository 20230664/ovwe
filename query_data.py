import duckdb

def get_db_conn():
    return duckdb.connect("overwatch.duckdb")

# 모든 영웅 목록 가져오기
def get_all_heroes():
    conn = get_db_conn()
    heroes = conn.execute("SELECT Hero_id, hero_name, role_id FROM Hero").fetchall()
    conn.close()
    return heroes

# 특정 영웅의 상세 정보 및 스킬 가져오기
def get_hero_full_detail(hero_id):
    conn = get_db_conn()
    # 영웅 기본 정보 + 역할 이름
    hero_info = conn.execute("""
        SELECT h.hero_name, r.role_name 
        FROM Hero h JOIN Role r ON h.role_id = r.role_id 
        WHERE h.Hero_id = ?
    """, [hero_id]).fetchone()
    
    # 해당 영웅의 스킬 정보
    abilities = conn.execute("SELECT ability_name, cooldown FROM HeroAbility WHERE Hero_id = ?", [hero_id]).fetchall()
    print("모든 데이터 입력 완료!")
    conn.close()
    return hero_info, abilities