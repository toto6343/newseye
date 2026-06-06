import pandas as pd
from fastapi import APIRouter
import os

from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from pydantic import BaseModel
from typing import List

from app.services.report_service import report_service
from app.services.graph_service import graph_service
from app.models.news import News
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/generate-report")
async def generate_report(
    count: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generates and returns a PDF security report of the latest high-risk news.
    """
    # Fetch high risk news
    high_risk_news = db.query(News).filter(News.is_analyzed == True) \
                                   .order_by(News.risk_level.desc(), News.crawled_at.desc()) \
                                   .limit(count).all()
    
    if not high_risk_news:
        raise HTTPException(status_code=404, detail="No analyzed news found to generate report.")
        
    file_path = report_service.generate_security_report(high_risk_news, "user@example.com")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/pdf'
    )

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_news(request: ChatRequest):
    # 1. Search relevant documents
    search_results = await rag_service.query(request.query, n_results=5)
    
    documents = search_results.get("documents", [[]])[0]
    metadatas = search_results.get("metadatas", [[]])[0]
    
    # 2. Generate answer using LLM
    answer = await llm_service.generate_answer(request.query, documents)
    
    # 3. Format sources
    sources = []
    for meta in metadatas:
        sources.append({
            "title": meta.get("title", "Unknown"),
            "url": meta.get("url", "#"),
            "source": meta.get("source", "Unknown")
        })
        
    return {
        "answer": answer,
        "sources": sources
    }

@router.get("/yearly-trend")
async def get_yearly_trend():
    forecast_path = find_forecast_path()
    if not forecast_path:
        return {"error": "Forecast data not found."}
    
    df = pd.read_csv(forecast_path)
    # Filter out duplicate years
    df = df.groupby('ds')['yhat'].mean().reset_index()
    
    return {
        "labels": df['ds'].astype(int).tolist(),
        "values": df['yhat'].tolist()
    }

@router.get("/forecast")
async def get_forecast():
    forecast_path = find_forecast_path()
    if not forecast_path:
        return {"error": "Forecast data not found."}
    
    df = pd.read_csv(forecast_path)
    # Filter out duplicate years and keep the latest or mean
    df = df.groupby('ds')['yhat'].mean().reset_index()
    
    data = []
    for _, row in df.iterrows():
        data.append({
            "year": int(row['ds']),
            "threats": round(float(row['yhat']), 2)
        })
    return data

@router.get("/graph")
async def get_knowledge_graph(limit: int = 100):
    """
    Returns graph data (nodes and links) from Neo4j for visualization.
    """
    return graph_service.get_graph_data(limit=limit)

def find_forecast_path():
    possible_paths = [
        '../newseye-news-crawler/ml/forecast/yearly_threat_forecast.csv',
        './newseye-news-crawler/ml/forecast/yearly_threat_forecast.csv',
        '../data/forecast/yearly_threat_forecast.csv'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None
