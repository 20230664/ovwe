import flet as ft
import duckdb
from datetime import timedelta

def get_db_data(query, params=()):
    conn = duckdb.connect("overwatch.duckdb")
    try:
        data = conn.execute(query, params).fetchall()
    except Exception as e:
        data = []
        print(f"DB 오류: {e}")
    conn.close()
    return data

def main(page: ft.Page):
    page.title = "오버워치 정보 시스템"
    page.scroll = ft.ScrollMode.AUTO
    content_area = ft.Column()
    page.add(content_area)

    role_info = {
        "Tank": {"title": "돌격 (Tank)", "desc": "팀의 전방을 지키며 피해를 흡수하고, 적의 진입을 방해합니다."},
        "Damage": {"title": "공격 (Damage)", "desc": "적을 공격하고 처치하여 전투 우위를 확보합니다."},
        "Support": {"title": "지원 (Support)", "desc": "아군을 치유하거나 강화하여 팀의 지속력을 높입니다."}
    }

    # ---------------- 메인 메뉴 ----------------
    def show_main_menu(e=None):
        content_area.controls.clear()
        content_area.controls.append(ft.Column([
            ft.Text("메인 메뉴", size=30, weight="bold"),
            ft.Row([
                ft.ElevatedButton("영웅", on_click=show_hero_list),
                ft.ElevatedButton("역할군", on_click=show_role_list),
                ft.ElevatedButton("모드", on_click=show_mode_list),
                ft.ElevatedButton("맵", on_click=show_map_list),
                ft.ElevatedButton("선수 검색", on_click=show_player_search)
            ])
        ]))
        page.update()

    # ---------------- 영웅 ----------------
    def show_hero_detail(h_id):
        hero_info = get_db_data("SELECT hero_name FROM Hero WHERE Hero_id = ?", (h_id,))
        abilities = get_db_data("SELECT ability_name, cooldown FROM HeroAbility WHERE hero_id = ?", (h_id,))
        content_area.controls.clear()

        content_area.controls.append(
            ft.Image(src=f"heroes/{h_id}.png", width=200, height=200, fit='cover', border_radius=8)
        )
        content_area.controls.append(ft.Text(f"영웅: {hero_info[0][0]}", size=25, weight="bold"))
        for ab_name, cd in abilities:
            content_area.controls.append(ft.Text(f"스킬: {ab_name} | 쿨타임: {cd}초"))
        content_area.controls.append(ft.ElevatedButton("목록으로 돌아가기", on_click=show_hero_list))
        page.update()

    def show_hero_list(e):
        heroes = get_db_data("SELECT Hero_id, hero_name FROM Hero")
        content_area.controls.clear()
        content_area.controls.append(ft.Text("영웅 목록", size=20, weight="bold"))

        hero_cards = []
        for h_id, name in heroes:
            card = ft.Container(
                content=ft.Column([
                    ft.Image(
                        src=f"heroes/{h_id}.png",
                        width=120,
                        height=120,
                        fit="cover",
                        border_radius=8
                    ),
                    ft.Text(name, size=14, weight="bold", text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.GREY_900,
                on_click=lambda e, hid=h_id: show_hero_detail(hid),
                ink=True,
            )
            hero_cards.append(card)

        content_area.controls.append(
            ft.Row(controls=hero_cards, wrap=True, spacing=10, run_spacing=10)
        )
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
        page.update()

    # ---------------- 역할군 ----------------
    def show_role_list(e):
        content_area.controls.clear()
        for key in role_info:
            content_area.controls.append(ft.ElevatedButton(key, on_click=lambda e, r=key: show_role_detail(r)))
        content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
        page.update()

    def show_role_detail(role_key):
        info = role_info[role_key]
        content_area.controls.clear()
        content_area.controls.append(ft.Column([
            ft.Text(info["title"], size=25, weight="bold"),
            ft.Text(f"설명: {info['desc']}"),
            ft.ElevatedButton("목록으로", on_click=show_role_list)
        ]))
        page.update()

    # ---------------- 모드 ----------------
    def show_mode_list(e):
        modes = get_db_data("SELECT mode_id, mode_name FROM Mode")
        content_area.controls.clear()
        content_area.controls.append(ft.Text("게임 모드 목록", size=20))
        for m_id, name in modes:
            content_area.controls.append(ft.ElevatedButton(name, on_click=lambda e, mid=m_id: show_mode_detail(mid)))
        content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
        page.update()

    def show_mode_detail(m_id):
        mode_data = get_db_data("SELECT mode_name FROM Mode WHERE mode_id = ?", (m_id,))
        if mode_data:
            name = mode_data[0][0]
            content_area.controls.clear()
            content_area.controls.append(ft.Column([
                ft.Text(name, size=25, weight="bold"),
                ft.ElevatedButton("목록으로", on_click=show_mode_list)
            ]))
            page.update()

    # ---------------- 맵 ----------------
    def show_map_list(e):
        maps = get_db_data("SELECT map_id, map_name FROM Map")
        content_area.controls.clear()
        content_area.controls.append(ft.Text("맵 목록", size=20, weight="bold"))

        map_buttons = []
        for m_id, name in maps:
            map_buttons.append(
                ft.ElevatedButton(name, on_click=lambda e, mid=m_id: show_map_detail(mid))
            )

        content_area.controls.append(
            ft.Row(controls=map_buttons, wrap=True, spacing=10, run_spacing=10)
        )
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
        page.update()

    def show_map_detail(m_id):
        map_data = get_db_data("""
            SELECT mp.map_name, mp.region, mo.mode_name
            FROM Map mp
            JOIN Mode mo ON mp.mode_id = mo.mode_id
            WHERE mp.map_id = ?
        """, (m_id,))
        if map_data:
            name, region, mode_name = map_data[0]
            content_area.controls.clear()
            content_area.controls.append(ft.Column([
                ft.Text(f"맵 이름: {name}", size=25, weight="bold"),
                ft.Text(f"지역: {region}"),
                ft.Text(f"모드: {mode_name}"),
                ft.ElevatedButton("목록으로", on_click=show_map_list)
            ]))
            page.update()

    # ---------------- 선수 검색 ----------------
    def show_player_search(e=None):
        content_area.controls.clear()
        tag_input = ft.TextField(label="배틀태그 입력 (예: Player#1234)", width=300)

        def search_click(e):
            show_player_profile(tag_input.value)

        content_area.controls.append(ft.Column([
            ft.Text("선수 검색", size=25, weight="bold"),
            tag_input,
            ft.ElevatedButton("검색", on_click=search_click),
            ft.ElevatedButton("메인으로", on_click=show_main_menu)
        ]))
        page.update()

    # ---------------- 퍼포먼스 분석 ----------------
    def show_player_performance(battle_tag):
        content_area.controls.clear()

        if not battle_tag:
            content_area.controls.append(ft.Text("배틀태그를 입력해주세요."))
            content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
            page.update()
            return

        player_exists = get_db_data("SELECT BattleTag FROM player WHERE BattleTag = ?", (battle_tag,))
        if not player_exists:
            content_area.controls.append(ft.Text(f"'{battle_tag}' 플레이어를 찾을 수 없습니다."))
            content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
            page.update()
            return

        summary = get_db_data("""
            SELECT 
                COUNT(*) AS games,
                SUM(kill_count), SUM(deaths), SUM(damage), SUM(healing), SUM(play_time)
            FROM Performance
            WHERE BattleTag = ?
        """, (battle_tag,))

        games, kills, deaths, damage, healing, play_time = summary[0]
        games = games or 0
        kills = kills or 0
        deaths = deaths or 0
        damage = damage or 0
        healing = healing or 0
        play_time = play_time or 0
        kda = round(kills / deaths, 2) if deaths > 0 else kills

        hero_stats = get_db_data("""
            SELECT h.hero_name,
                COUNT(*) AS plays,
                SUM(p.kill_count), SUM(p.deaths), SUM(p.damage), SUM(p.healing)
            FROM Performance p
            JOIN Hero h ON p.Hero_id = h.Hero_id
            WHERE p.BattleTag = ?
            GROUP BY h.hero_name
            ORDER BY plays DESC
        """, (battle_tag,))

        recent_matches = get_db_data("""
            SELECT m.Match_id, m.play_at, m.result, h.hero_name,
                p.kill_count, p.deaths, p.damage, p.healing
            FROM Performance p
            JOIN Match_info m ON p.Match_id = m.Match_id
            JOIN Hero h ON p.Hero_id = h.Hero_id
            WHERE p.BattleTag = ?
            ORDER BY m.play_at DESC, p.switched_at DESC
            LIMIT 10
        """, (battle_tag,))

        content_area.controls.append(ft.Text(f"{battle_tag} 퍼포먼스 분석", size=25, weight="bold"))
        content_area.controls.append(ft.Divider())

        content_area.controls.append(ft.Text("종합 통계", size=18, weight="bold"))
        content_area.controls.append(ft.Text(f"총 경기 수: {games}"))
        content_area.controls.append(ft.Text(f"총 킬: {kills} | 총 데스: {deaths} | KDA: {kda}"))
        content_area.controls.append(ft.Text(f"총 딜량: {damage} | 총 힐량: {healing} | 총 플레이타임: {play_time}초"))
        content_area.controls.append(ft.Divider())

        content_area.controls.append(ft.Text("영웅별 통계", size=18, weight="bold"))
        if hero_stats:
            for name, plays, hk, hd, hdmg, hh in hero_stats:
                content_area.controls.append(
                    ft.Text(f"{name} | 플레이 {plays}회 | 킬 {hk} 데스 {hd} | 딜 {hdmg} 힐 {hh}")
                )
        else:
            content_area.controls.append(ft.Text("기록 없음"))
        content_area.controls.append(ft.Divider())

        content_area.controls.append(ft.Text("최근 경기 (최대 10개)", size=18, weight="bold"))
        if recent_matches:
            for mid, play_at, result, hero, k, d, dmg, heal in recent_matches:
                content_area.controls.append(
                    ft.Text(f"[{play_at}] {hero} | {result} | K{k} D{d} | 딜{dmg} 힐{heal}")
                )
        else:
            content_area.controls.append(ft.Text("경기 기록 없음"))

        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Row([
            ft.ElevatedButton("프로필로", on_click=lambda e: show_player_profile(battle_tag)),
            ft.ElevatedButton("다시 검색", on_click=show_player_search),
            ft.ElevatedButton("메인으로", on_click=show_main_menu)
        ]))
        page.update()

    # ---------------- 프로필 ----------------
    def show_player_profile(battle_tag):
        content_area.controls.clear()

        player_exists = get_db_data("SELECT BattleTag FROM player WHERE BattleTag = ?", (battle_tag,))
        if not player_exists:
            content_area.controls.append(ft.Text(f"'{battle_tag}' 플레이어를 찾을 수 없습니다."))
            content_area.controls.append(ft.ElevatedButton("다시 검색", on_click=show_player_search))
            content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
            page.update()
            return

        roles = get_db_data("""
            SELECT r.role_name, pr.current_er
            FROM Player_Role pr
            JOIN Role r ON pr.role_id = r.role_id
            WHERE pr.BattleTag = ?
        """, (battle_tag,))

        # 경기별 결과 (Match_id 단위로 그룹화, result는 해당 경기의 대표값 사용)
        recent = get_db_data("""
            SELECT m.Match_id, m.result, m.play_at
                FROM Performance p
                JOIN Match_info m ON p.Match_id = m.Match_id
                WHERE p.BattleTag = ?
                GROUP BY m.Match_id, m.result, m.play_at
                ORDER BY m.play_at DESC
                LIMIT 10
        """, (battle_tag,))

        wins = sum(1 for r in recent if r[1] == '승리')
        total = len(recent)
        win_rate = round(wins / total * 100) if total else 0

        # 최근 점수 변동 이력
        er_history = get_db_data("""
            SELECT r.role_name, eh.changed_er, eh.recorded_at
            FROM ErHistory eh
            JOIN Role r ON eh.role_id = r.role_id
            WHERE eh.BattleTag = ?
            ORDER BY eh.recorded_at DESC
            LIMIT 5
        """, (battle_tag,))

        content_area.controls.append(ft.Text("사용자 프로필 조회", size=25, weight="bold"))
        content_area.controls.append(ft.Text(f"사용자 배틀태그: {battle_tag}"))
        content_area.controls.append(ft.Divider())

        content_area.controls.append(ft.Text("포지션별 경쟁전 점수", size=18, weight="bold"))
        role_row = ft.Row([ft.Text(f"{name}: {er}점") for name, er in roles], spacing=30)
        content_area.controls.append(role_row)

        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text("최근 전적 요약", size=18, weight="bold"))
        content_area.controls.append(ft.Text(f"최근 {total}경기 승률: {win_rate}% ({wins}승 {total-wins}패)"))

        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text("최근 점수 변동 이력", size=18, weight="bold"))
        if er_history:
            for role_name, changed, recorded_at in er_history:
                sign = "+" if changed > 0 else ""
                color = ft.Colors.GREEN if changed > 0 else (ft.Colors.RED if changed < 0 else ft.Colors.GREY)
                content_area.controls.append(
                    ft.Text(f"[{recorded_at}] {role_name}: {sign}{changed}", color=color)
                )
        else:
            content_area.controls.append(ft.Text("변동 이력 없음"))

        content_area.controls.append(ft.Divider())
        content_area.controls.append(
            ft.ElevatedButton("상세 경기 리스트 보기", on_click=lambda e: show_match_list(battle_tag))
        )
        content_area.controls.append(
            ft.ElevatedButton("퍼포먼스 분석 보기", on_click=lambda e: show_player_performance(battle_tag))
        )
        content_area.controls.append(ft.ElevatedButton("메인으로", on_click=show_main_menu))
        page.update()

    # ---------------- 경기 리스트 ----------------
    def show_match_list(battle_tag):
        content_area.controls.clear()

        matches = get_db_data("""
            SELECT m.Match_id, m.play_at, mp.map_name, m.result
                FROM Performance p
                JOIN Match_info m ON p.Match_id = m.Match_id
                JOIN Map mp ON m.map_id = mp.map_id
                WHERE p.BattleTag = ?
                GROUP BY m.Match_id, m.play_at, mp.map_name, m.result
                ORDER BY m.play_at DESC
        """, (battle_tag,))

        content_area.controls.append(ft.Text(f"{battle_tag} 경기 기록", size=25, weight="bold"))
        content_area.controls.append(ft.Divider())

        if not matches:
            content_area.controls.append(ft.Text("경기 기록이 없습니다."))

        for match_id, play_at, map_name, result in matches:
            result_color = ft.Colors.GREEN if result == '승리' else (ft.Colors.RED if result == '패배' else ft.Colors.GREY)

            row = ft.Row([
                ft.Container(ft.Text(str(play_at)), width=170, alignment=ft.Alignment(0, 0)),
                ft.Container(ft.Text(map_name), width=120, alignment=ft.Alignment(0, 0)),
                ft.Container(ft.Text(result, color=result_color, weight="bold"), width=80, alignment=ft.Alignment(0, 0)),
            ])

            content_area.controls.append(
                ft.ElevatedButton(
                    content=row,
                    on_click=lambda e, mid=match_id: show_match_detail(battle_tag, mid)
                )
            )

        content_area.controls.append(ft.Divider())
        content_area.controls.append(
            ft.ElevatedButton("프로필로", on_click=lambda e: show_player_profile(battle_tag))
        )
        content_area.controls.append(
            ft.ElevatedButton("메인으로", on_click=show_main_menu)
        )
        page.update()

    # ---------------- 경기 상세 ----------------
    def show_match_detail(battle_tag, match_id):
        content_area.controls.clear()

        info = get_db_data("""
            SELECT m.Match_id, m.play_at, m.result, mp.map_name, mo.mode_name, mp.region
            FROM Match_info m
            JOIN Map mp ON m.map_id = mp.map_id
            JOIN Mode mo ON mp.mode_id = mo.mode_id
            WHERE m.Match_id = ?
        """, (match_id,))[0]

        heroes = get_db_data("""
            SELECT h.hero_name
            FROM Performance p
            JOIN Hero h ON p.Hero_id = h.Hero_id
            WHERE p.BattleTag = ? AND p.Match_id = ?
            ORDER BY p.switched_at
        """, (battle_tag, match_id))

        switch_count = max(0, len(heroes) - 1)
        final_result = info[2]   # ← Match_info.result 사용

        content_area.controls.append(ft.Text("경기 정보 상세 조회", size=25, weight="bold"))
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text(f"경기 코드: {info[0]}"))
        content_area.controls.append(ft.Text(f"경기 일시: {info[1]}"))
        content_area.controls.append(ft.Text(f"맵 이름: {info[3]} | 게임 모드: {info[4]} | 배경 국가: {info[5]}"))
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text("플레이 요약", size=18, weight="bold"))
        content_area.controls.append(ft.Text(f"최종 결과: {final_result}"))
        content_area.controls.append(ft.Text(f"영웅 교체 횟수: {switch_count}회"))
        content_area.controls.append(ft.Text(f"참여 영웅: {', '.join(h[0] for h in heroes)}"))

        content_area.controls.append(
            ft.ElevatedButton("이 경기의 영웅 교체 타임라인 분석하기",
                            on_click=lambda e: show_match_timeline(battle_tag, match_id))
        )
        content_area.controls.append(
            ft.ElevatedButton("경기 리스트로", on_click=lambda e: show_match_list(battle_tag))
        )
        page.update()

    # ---------------- 영웅 교체 타임라인 (switched_at 기반) ----------------
    def show_match_timeline(battle_tag, match_id):
        content_area.controls.clear()

        segments = get_db_data("""
            SELECT h.hero_name, p.kill_count, p.deaths, p.damage, p.healing,
                p.play_time, p.switched_at
            FROM Performance p
            JOIN Hero h ON p.Hero_id = h.Hero_id
            WHERE p.BattleTag = ? AND p.Match_id = ?
            ORDER BY p.switched_at
        """, (battle_tag, match_id))

        match_info = get_db_data("""
            SELECT mp.map_name, m.play_at
            FROM Match_info m JOIN Map mp ON m.map_id = mp.map_id
            WHERE m.Match_id = ?
        """, (match_id,))[0]

        content_area.controls.append(ft.Text("플레이어 영웅교체 타임라인 정보 조회", size=22, weight="bold"))
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text(f"경기 요약: {match_info[0]} | {match_info[1]}"))
        content_area.controls.append(ft.Divider())

        if not segments:
            content_area.controls.append(ft.Text("타임라인 기록이 없습니다."))
            content_area.controls.append(
                ft.ElevatedButton("경기 상세로", on_click=lambda e: show_match_detail(battle_tag, match_id))
            )
            page.update()
            return

        rows = []
        for i, (hero, k, d, dmg, heal, play_time, switched_at) in enumerate(segments):
            start = switched_at
            if i + 1 < len(segments):
                end = segments[i + 1][6]
            else:
                end = switched_at + timedelta(seconds=play_time or 0)
            rows.append((hero, k, d, dmg, heal, start, end))

        content_area.controls.append(ft.Text("영웅 교체 타임라인", size=18, weight="bold"))
        timeline_text = " ── ".join(
            f"[{r[0]}] ({r[5].strftime('%H:%M:%S')}~{r[6].strftime('%H:%M:%S')})" for r in rows
        )
        content_area.controls.append(ft.Text(timeline_text))
        content_area.controls.append(ft.Divider())

        header = ft.Row([
            ft.Text("영웅", width=80, weight="bold"),
            ft.Text("처치", width=60, weight="bold"),
            ft.Text("데스", width=60, weight="bold"),
            ft.Text("딜량", width=80, weight="bold"),
            ft.Text("힐량", width=80, weight="bold"),
            ft.Text("시간", width=180, weight="bold"),
        ])
        content_area.controls.append(header)

        best_dpm_hero, best_dpm = None, -1
        for hero, k, d, dmg, heal, start, end in rows:
            duration = (end - start).total_seconds()
            dpm = round(dmg / (duration / 60), 0) if duration > 0 else 0
            if dpm > best_dpm:
                best_dpm, best_dpm_hero = dpm, hero

            content_area.controls.append(ft.Row([
                ft.Text(hero, width=80),
                ft.Text(str(k), width=60),
                ft.Text(str(d), width=60),
                ft.Text(f"{dmg:,}", width=80),
                ft.Text(f"{heal:,}", width=80),
                ft.Text(f"{start.strftime('%H:%M:%S')} ~ {end.strftime('%H:%M:%S')}", width=180),
            ]))

        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Text("시스템 분석 결과", size=18, weight="bold"))
        content_area.controls.append(ft.Text(f"본 경기 최고 효율 영웅: {best_dpm_hero} (DPM: {best_dpm:,.0f})"))

        content_area.controls.append(
            ft.ElevatedButton("경기 상세로", on_click=lambda e: show_match_detail(battle_tag, match_id))
        )
        page.update()

    # 초기 화면 실행
    show_main_menu()

ft.app(target=main, assets_dir="assets")