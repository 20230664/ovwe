import duckdb
import random
from datetime import datetime, timedelta

random.seed(42)

def generate_dummy_data():
    conn = duckdb.connect("overwatch.duckdb")

    # 기존 더미 데이터 초기화
    for t in ['ErHistory', 'Performance', 'Player_Role', 'Match_info', 'player']:
        conn.execute(f"DELETE FROM {t}")
    conn.execute("DROP SEQUENCE IF EXISTS seq_perf_id")
    conn.execute("CREATE SEQUENCE seq_perf_id START 1")

    conn.execute("DROP SEQUENCE IF EXISTS seq_history_id")
    conn.execute("CREATE SEQUENCE seq_history_id START 1")

    # 1. 플레이어 생성
    players = [f"Player{i}#{random.randint(1000,9999)}" for i in range(1, 11)]
    conn.executemany("INSERT OR IGNORE INTO player VALUES (?)", [(p,) for p in players])

    # 2. 영웅을 역할군별로 그룹화
    hero_rows = conn.execute("SELECT Hero_id, role_id FROM Hero").fetchall()
    heroes_by_role = {}
    for h_id, role_id in hero_rows:
        heroes_by_role.setdefault(role_id, []).append(h_id)
    role_ids = list(heroes_by_role.keys())

    # 3. 맵 ID
    map_ids = [r[0] for r in conn.execute("SELECT map_id FROM Map").fetchall()]

    # 4. Match_info 생성 (result 없음 -> Performance에만 저장)
    matches = []
    base_time = datetime(2026, 5, 1, 18, 0, 0)
    for i in range(1, 51):
        match_id = f"MATCH_{i:04d}"
        map_id = random.choice(map_ids)
        play_at = base_time + timedelta(hours=i * 3)
        result = random.choice(['승리', '패배', '무승부'])  # ← 추가
        matches.append((match_id, map_id, play_at, result))

    conn.executemany("INSERT OR IGNORE INTO Match_info VALUES (?, ?, ?, ?)", matches)

    # 5. Player_Role (시작 ER)
    player_roles = []
    current_er = {}
    for p in players:
        for r in role_ids:
            start_er = random.randint(1000, 4000)
            player_roles.append((p, r, start_er))
            current_er[(p, r)] = start_er

    conn.executemany("INSERT OR IGNORE INTO Player_Role VALUES (?, ?, ?)", player_roles)

    # 6. Performance + ErHistory 생성
    performances = []
    er_history = []

    for match_id, map_id, play_at, result in matches:
        participants = random.sample(players, 5)
        result = random.choice(['승리', '패배', '무승부'])

        # ER 변동값
        if result == '승리':
            er_change = random.randint(27, 30)
        elif result == '패배':
            er_change = -random.randint(27, 30)
        else:
            er_change = 0

        for p in participants:
            role_id = random.choice(role_ids)
            same_role_heroes = heroes_by_role[role_id]
            main_hero = random.choice(same_role_heroes)

            total_kills = random.randint(0, 25)
            total_deaths = random.randint(0, 15)

            # 역할군별 딜/힐 비중 다르게
            if role_id == 'support':
                total_damage = random.randint(1000, 6000)
                total_healing = random.randint(6000, 12000)
            elif role_id == 'tank':
                total_damage = random.randint(5000, 12000)
                total_healing = random.randint(0, 1000)
            else:  # dps
                total_damage = random.randint(8000, 15000)
                total_healing = random.randint(0, 500)

            total_play_time = random.randint(300, 900)

            # 세그먼트 개수 (같은 역할군 내에서만 교체)
            n_seg = random.choice([1, 1, 2, 3])
            n_seg = min(n_seg, len(same_role_heroes))

            if n_seg <= 1 or total_play_time <= 60 * (n_seg - 1):
                hero_list = [main_hero]
                bounds = [0, total_play_time]
            else:
                other_candidates = [h for h in same_role_heroes if h != main_hero]
                other_heroes = random.sample(other_candidates, n_seg - 1)
                hero_list = [main_hero] + other_heroes
                cuts = sorted(random.sample(range(60, total_play_time, 60), n_seg - 1))
                bounds = [0] + cuts + [total_play_time]

            for idx, hero_id in enumerate(hero_list):
                seg_start, seg_end = bounds[idx], bounds[idx + 1]
                seg_play_time = seg_end - seg_start
                ratio = seg_play_time / total_play_time

                switched_at = play_at + timedelta(seconds=seg_start)

                performances.append((
                    p, hero_id, match_id,
                    round(total_kills * ratio),
                    round(total_deaths * ratio),
                    round(total_damage * ratio),
                    round(total_healing * ratio),
                    seg_play_time,
                    switched_at
                ))

            # ER 변동 이력 (경기당 1건)
            if er_change != 0:
                er_history.append((p, role_id, er_change, play_at))
                current_er[(p, role_id)] = current_er.get((p, role_id), 0) + er_change

    conn.executemany("""
        INSERT INTO Performance
        (BattleTag, Hero_id, Match_id, kill_count, deaths, damage, healing, play_time, switched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, performances)

    conn.executemany("""
        INSERT INTO ErHistory (BattleTag, role_id, changed_er, recorded_at)
        VALUES (?, ?, ?, ?)
    """, er_history)

    # 7. Player_Role 최종 ER 업데이트 (변동 누적 반영)
    for (p, r), final_er in current_er.items():
        conn.execute("UPDATE Player_Role SET current_er = ? WHERE BattleTag = ? AND role_id = ?", (final_er, p, r))

    print("더미 데이터 생성 완료!\n")
    print(conn.execute("SELECT * FROM player").df())
    print(conn.execute("SELECT * FROM Performance LIMIT 10").df())
    print(conn.execute("SELECT * FROM ErHistory LIMIT 5").df())
    print(conn.execute("SELECT * FROM Player_Role LIMIT 5").df())

    conn.close()

if __name__ == "__main__":
    generate_dummy_data()