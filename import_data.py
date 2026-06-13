import duckdb

def import_data():
    conn = duckdb.connect("overwatch.duckdb")
    
   
    # 데이터 삽입 (CSV 구조와 테이블 구조가 1:1로 맞아야 함)
    # csv 파일 헤더가 테이블 컬럼과 동일한지 확인하세요!
    conn.execute("INSERT OR IGNORE INTO Hero SELECT * FROM read_csv('heroes.csv', header=True)")
    conn.execute("INSERT OR IGNORE INTO HeroAbility SELECT * FROM read_csv('abilities.csv', header=True)")
    
    print("모든 데이터 입력 완료!")
    conn.close()

if __name__ == "__main__":
    import_data()