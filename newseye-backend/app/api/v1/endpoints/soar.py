from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.news import News
from app.middleware.auth import get_current_active_user
import json

router = APIRouter(prefix="/soar", tags=["soar"])

@router.get("/rules/firewall/{news_id}")
async def generate_firewall_rules(
    news_id: int, 
    type: str = "iptables",
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_active_user)
):
    """
    Generates blocking rules (iptables or AWS SG) based on malicious IPs found in a specific news article.
    """
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
        
    if not news.ioc_data or not news.ioc_data.get("details"):
        return {"message": "No IoCs found in this article to generate rules for.", "rules": []}

    malicious_ips = [
        detail["ioc"] for detail in news.ioc_data["details"] 
        if detail.get("type") == "ip" and detail.get("status") in ["malicious", "suspicious"]
    ]
    
    if not malicious_ips:
        return {"message": "No malicious IPs found to block.", "rules": []}

    rules = []
    if type == "iptables":
        for ip in malicious_ips:
            rules.append(f"iptables -A INPUT -s {ip} -j DROP")
            rules.append(f"iptables -A OUTPUT -d {ip} -j DROP")
    elif type == "aws":
        sg_rules = []
        for ip in malicious_ips:
            sg_rules.append({
                "IpProtocol": "-1",
                "IpRanges": [{"CidrIp": f"{ip}/32", "Description": f"Blocked via NewsEye Alert (News ID: {news_id})"}]
            })
        rules.append(json.dumps(sg_rules, indent=2))
    else:
        raise HTTPException(status_code=400, detail="Unsupported rule type. Use 'iptables' or 'aws'.")

    return {
        "news_id": news_id,
        "type": type,
        "ip_count": len(malicious_ips),
        "rules": rules
    }

@router.post("/dispatch/{news_id}")
async def dispatch_alert(
    news_id: int,
    channel: str = "slack",
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_active_user)
):
    """
    Mocks dispatching a critical threat alert to Slack, Jira, or email.
    """
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")

    # In a real scenario, this would use incoming webhooks or Jira REST API
    return {
        "status": "success",
        "message": f"Successfully dispatched alert for '{news.title}' to {channel.upper()}.",
        "dispatched_data": {
            "title": f"[CRITICAL] {news.title}",
            "cves": news.cve_ids,
            "risk_level": news.risk_level,
            "url": news.url
        }
    }
