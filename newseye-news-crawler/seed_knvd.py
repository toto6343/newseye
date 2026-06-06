import json
import os
from sqlalchemy.orm import Session
from database import SessionLocal, CrimeType
from config import Config

def seed_initial_crime_types():
    db = SessionLocal()
    try:
        for ct_name in Config.CRIME_TYPES:
            exists = db.query(CrimeType).filter(CrimeType.name == ct_name).first()
            if not exists:
                new_ct = CrimeType(
                    name=ct_name,
                    keywords=[],
                    description=f"{ct_name} 관련 범죄 유형"
                )
                db.add(new_ct)
        db.commit()
        print("✅ 초기 범죄 유형 데이터 삽입 완료")
    except Exception as e:
        db.rollback()
        print(f"❌ 초기 데이터 삽입 중 오류 발생: {e}")
    finally:
        db.close()

def process_knvd_data(json_file_path: str):
    """
    KNVD(한국 국가 취약점 DB) 데이터를 읽어 hacking, malware 키워드를 CrimeType 테이블에 업데이트합니다.
    """
    if not os.path.exists(json_file_path):
        print(f"⚠️ KNVD 데이터 파일이 없습니다: {json_file_path}")
        return

    db = SessionLocal()
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            knvd_data = json.load(f)

        # 예시: 취약점 데이터에서 키워드 추출 (CVE 번호, 소프트웨어 이름 등)
        new_keywords = set()
        for item in knvd_data:
            # 취약점 제목이나 설명에서 키워드 추출 로직
            title = item.get('title', '')
            if title:
                # 간단한 토큰화 (실제로는 더 복잡한 NLP 필요)
                words = title.split()
                for word in words:
                    if len(word) > 2:
                        new_keywords.add(word.lower())

        # Hacking 유형에 키워드 추가
        hacking_type = db.query(CrimeType).filter(CrimeType.name == 'hacking').first()
        if hacking_type:
            current_keywords = set(hacking_type.keywords or [])
            updated_keywords = list(current_keywords.union(new_keywords))
            hacking_type.keywords = updated_keywords
            db.commit()
            print(f"✅ KNVD 데이터를 통해 'hacking' 키워드 {len(new_keywords)}개 업데이트 완료")

    except Exception as e:
        db.rollback()
        print(f"❌ KNVD 데이터 처리 중 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    from database import init_db
    init_db()
    seed_initial_crime_types()
    # KNVD 데이터가 준비되면 아래 함수 호출 가능
    # process_knvd_data('data/knvd/knvd_latest.json')
