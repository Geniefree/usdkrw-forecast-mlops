# src/inference.py
import pickle
import pandas as pd
import os

def predict_next_15m(
    data_path="data/processed/market_data_1m_24h_interpolated.csv", 
    model_path="data/processed/predict_model.pkl"
):

    # 1. 학습된 모델 불러오기
    if not os.path.exists(model_path):
        print(f" '{model_path}' 파일을 찾을 수 없습니다.")
        return

    with open(model_path, 'rb') as f:
        loaded_model = pickle.load(f)

    # 2. 예측에 사용할 변수
    features = ['BTC', 'JPY', 'WTI', 'GOLD', 'DXY']

    # 3. 최신 데이터 추출

    final_df = pd.read_csv(data_path, index_col=0)
    latest_row = final_df.iloc[-1]
    
    current_time = latest_row.name
    current_krw = latest_row['KRW']

    X_latest = latest_row[features].to_frame().T

    prediction = loaded_model.predict(X_latest)[0]

    print(f"\n=============================================")
    print(f"현재 시점: {current_time}")
    print(f"현재 KRW 환율: {current_krw:.2f}원")
    print("---------------------------------------------")
    if prediction == 1:
        print("[결과] 15분 뒤 원/달러 환율은 **상승**할 것으로 예측됩니다!")
    else:
        print("[결과] 15분 뒤 원/달러 환율은 **하락 또는 유지**될 것으로 예측됩니다!")
    print("=============================================\n")
    
    return prediction

# 단독으로 실행할 때를 위한 코드
if __name__ == "__main__":
    predict_next_15m()