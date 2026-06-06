import pandas as pd
import numpy as np
from prophet import Prophet
import os
import matplotlib.pyplot as plt

def generate_forecast():
    print("Loading Global Cybersecurity Threats Dataset...")
    # Find base project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))
    
    path = os.path.join(project_root, 'data/raw/Global_Cybersecurity_Threats_2015-2024.csv')
    
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return

    df = pd.read_csv(path)
    
    # 1. 시계열 데이터 구성을 위해 연도별 위협 건수 집계
    yearly_counts = df.groupby('Year').size().reset_index(name='y')
    yearly_counts.columns = ['ds', 'y']
    yearly_counts['ds'] = pd.to_datetime(yearly_counts['ds'].astype(str) + '-01-01')
    
    print("Historical Year-over-Year Data:")
    print(yearly_counts)

    # 2. Prophet 모델 학습
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(yearly_counts)

    # 3. 향후 5년 예측 (2025~2029)
    future = model.make_future_dataframe(periods=5, freq='YE')
    forecast = model.predict(future)

    # 4. 결과 시각화 및 저장
    print("\nForecast Results (Future 5 Years):")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(5))

    # 데이터베이스 연동을 위한 결과 저장
    output_dir = os.path.join(project_root, 'newseye-news-crawler/ml/forecast')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    forecast_summary = forecast[['ds', 'yhat']].copy()
    forecast_summary['ds'] = forecast_summary['ds'].dt.year
    forecast_summary.to_csv(os.path.join(output_dir, 'yearly_threat_forecast.csv'), index=False)
    
    print(f"\n✅ Forecast generated and saved to {output_dir}")

if __name__ == "__main__":
    generate_forecast()
