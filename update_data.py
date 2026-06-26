import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 수집할 타겟 종목 리스트 (필요한 종목을 여기에 추가하세요)
# 한국 주식은 뒤에 .KS(코스피) 또는 .KQ(코스닥)를 붙여야 합니다.
TARGET_TICKERS = [
    "005930.KS", "000660.KS", "035720.KS", # 한국: 삼성전자, SK하이닉스, 카카오
    "AAPL", "NVDA", "TSLA", "MSFT"         # 미국: 애플, 엔비디아, 테슬라, 마이크로소프트
]

DATA_DIR = "data"

def fetch_and_save_data(ticker, days=520):
    try:
        print(f"[{ticker}] 데이터 수집 시작...")
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)
        
        # yfinance를 통한 데이터 다운로드 (GitHub 서버 내부이므로 포트 차단 없음)
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if df is None or df.empty:
            print(f"[{ticker}] 수집된 데이터가 없습니다.")
            return False
            
        # MultiIndex 컬럼 평탄화 (yfinance 최신 버전 대응)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
            
        df.columns = [c.capitalize() for c in df.columns]
        needed = ["Open", "High", "Low", "Close", "Volume"]
        
        if any(c not in df.columns for c in needed):
            print(f"[{ticker}] 필수 컬럼이 누락되었습니다.")
            return False
            
        # 데이터 정제 및 결측치 제거
        df = df[needed].copy().dropna(subset=["Close"]).apply(pd.to_numeric, errors="coerce").dropna()
        
        if len(df) < 30:
            print(f"[{ticker}] 유효한 데이터가 30일 미만입니다.")
            return False
            
        # CSV 파일로 저장
        file_path = os.path.join(DATA_DIR, f"{ticker}.csv")
        df.to_csv(file_path)
        print(f"[{ticker}] 성공적으로 저장되었습니다. ({len(df)}행)")
        return True
        
    except Exception as e:
        print(f"[{ticker}] 에러 발생: {e}")
        return False

if __name__ == "__main__":
    # 데이터 저장용 폴더 생성
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    success_count = 0
    for tk in TARGET_TICKERS:
        if fetch_and_save_data(tk):
            success_count += 1
            
    print(f"\n데이터 갱신 완료: 총 {len(TARGET_TICKERS)}개 중 {success_count}개 성공.")