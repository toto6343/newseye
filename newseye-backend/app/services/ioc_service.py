import re
import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class IoCService:
    # Regex patterns for IoCs
    IP_PATTERN = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    DOMAIN_PATTERN = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
    SHA256_PATTERN = r'\b[a-fA-F0-9]{64}\b'

    # Cache to save API calls (Memory-based)
    # Format: { (type, value): result_dict }
    _cache = {}

    @classmethod
    def extract_iocs(cls, text: str) -> dict:
        """
        Extracts IPs, Domains, and SHA-256 hashes from text using regex.
        """
        if not text:
            return {"ips": [], "domains": [], "hashes": []}

        ips = list(set(re.findall(cls.IP_PATTERN, text)))
        domains = list(set(re.findall(cls.DOMAIN_PATTERN, text, re.IGNORECASE)))
        hashes = list(set(re.findall(cls.SHA256_PATTERN, text)))
        
        return {
            "ips": ips,
            "domains": domains,
            "hashes": hashes
        }

    @classmethod
    def check_threat_intel(cls, iocs: dict) -> dict:
        """
        Checks IoCs against VirusTotal and AbuseIPDB with caching and saving mode.
        """
        results = {
            "malicious_count": 0,
            "details": []
        }
        
        vt_api_key = settings.VIRUSTOTAL_API_KEY
        abuse_api_key = settings.ABUSEIPDB_API_KEY

        def _check_vt(ioc_value: str, ioc_type: str) -> dict:
            cache_key = ("vt", ioc_type, ioc_value)
            if cache_key in cls._cache:
                return cls._cache[cache_key]
                
            if not vt_api_key:
                return None
            try:
                vt_type = "ip-addresses" if ioc_type == "ip" else "domains" if ioc_type == "domain" else "files"
                url = f"https://www.virustotal.com/api/v3/{vt_type}/{ioc_value}"
                headers = {"x-apikey": vt_api_key}
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    res = {
                        "ioc": ioc_value, 
                        "type": ioc_type, 
                        "status": "malicious" if malicious > 0 else "suspicious" if suspicious > 0 else "clean", 
                        "source": "VirusTotal", 
                        "positives": malicious,
                        "reputation": data.get("data", {}).get("attributes", {}).get("reputation", 0)
                    }
                    cls._cache[cache_key] = res
                    return res
            except Exception as e:
                logger.error(f"VT API Error: {e}")
            return None

        def _check_abuseipdb(ip: str) -> dict:
            cache_key = ("abuse", "ip", ip)
            if cache_key in cls._cache:
                return cls._cache[cache_key]

            if not abuse_api_key:
                return None
            try:
                url = 'https://api.abuseipdb.com/api/v2/check'
                params = {'ipAddress': ip, 'maxAgeInDays': '90'}
                headers = {'Accept': 'application/json', 'Key': abuse_api_key}
                response = requests.get(url, headers=headers, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    score = data.get("abuseConfidenceScore", 0)
                    res = {
                        "ioc": ip,
                        "type": "ip",
                        "status": "malicious" if score > 50 else "suspicious" if score > 10 else "clean",
                        "source": "AbuseIPDB",
                        "confidence_score": score,
                        "country": data.get("countryCode"),
                        "isp": data.get("isp")
                    }
                    cls._cache[cache_key] = res
                    return res
            except Exception as e:
                logger.error(f"AbuseIPDB API Error: {e}")
            return None

        # Process Domains (VT only) - Using Saving Mode Limits
        for domain in iocs.get("domains", [])[:settings.OSINT_MAX_DOMAINS_PER_NEWS]:
            vt_res = _check_vt(domain, "domain")
            if vt_res:
                if vt_res["status"] in ["malicious", "suspicious"]: results["malicious_count"] += 1
                results["details"].append(vt_res)

        # Process IPs (VT + AbuseIPDB)
        for ip in iocs.get("ips", [])[:settings.OSINT_MAX_IPS_PER_NEWS]:
            # VT Check
            vt_res = _check_vt(ip, "ip")
            if vt_res:
                if vt_res["status"] in ["malicious", "suspicious"]: results["malicious_count"] += 1
                results["details"].append(vt_res)
            
            # AbuseIPDB Check
            abuse_res = _check_abuseipdb(ip)
            if abuse_res:
                if abuse_res["status"] in ["malicious", "suspicious"]: results["malicious_count"] += 1
                results["details"].append(abuse_res)

        # Process Hashes (VT only)
        for h in iocs.get("hashes", [])[:1]:
            vt_res = _check_vt(h, "sha256")
            if vt_res:
                if vt_res["status"] in ["malicious", "suspicious"]: results["malicious_count"] += 1
                results["details"].append(vt_res)

        return results

    @classmethod
    def _get_mock_results(cls, iocs: dict) -> dict:
        # Internal helper for mock data if needed
        return {"malicious_count": 0, "details": [], "note": "No API keys configured"}

    @classmethod
    def _mock_check(cls, ioc_value: str, ioc_type: str) -> dict:
        if ioc_type == "domain" and "malicious" in ioc_value.lower():
            return {"ioc": ioc_value, "type": ioc_type, "status": "malicious", "source": "Mock VT"}
        if ioc_type == "ip" and ioc_value.startswith("192"):
            return {"ioc": ioc_value, "type": ioc_type, "status": "suspicious", "source": "Mock VT"}
        return {"ioc": ioc_value, "type": ioc_type, "status": "clean", "source": "Mock VT"}

ioc_service = IoCService()
