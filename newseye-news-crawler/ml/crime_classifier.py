import re
import torch
import os
from transformers import BertTokenizer, BertForSequenceClassification

class CrimeClassifier:
    def __init__(self, model_path=None):
        self.crime_types = ['phishing', 'ransomware', 'hacking', 'fraud', 'malware', 'stalking', 'crypto_crime']
        self.model = None
        self.tokenizer = None
        
        # Load trained model if path exists
        if model_path and os.path.exists(model_path):
            try:
                self.tokenizer = BertTokenizer.from_pretrained(model_path)
                self.model = BertForSequenceClassification.from_pretrained(model_path)
                self.model.eval()
                print(f"✅ Loaded trained model from {model_path}")
                
                label_path = os.path.join(os.path.dirname(model_path), "labels.txt")
                if os.path.exists(label_path):
                    with open(label_path, "r") as f:
                        self.crime_types = [line.strip() for line in f.readlines()]
            except Exception as e:
                print(f"⚠️ Error loading model: {e}. Falling back to keyword-based classification.")

        # Keyword mappings (fallback)
        self.keywords = {
            'ransomware': ['ransomware', 'cryptolocker', 'wannacry'],
            'crypto_crime': ['crypto', 'bitcoin', 'ethereum', 'exchange', 'wallet', 'blockchain', 'cryptocurrency'],
            'stalking': ['stalking', 'spyware', 'stalkerware', 'tracking', 'surveillance'],
            'phishing': ['phishing', 'smishing', 'vishing', 'spoofing', 'credential theft'],
            'malware': ['malware', 'virus', 'trojan', 'worm', 'rootkit', 'botnet', 'rat'],
            'fraud': ['fraud', 'scam', 'nigerian', 'extortion', 'lottery'],
            'hacking': ['hacking', 'exploit', 'vulnerability', 'breach', 'ddos', 'zero-day', 'injection']
        }

    def classify(self, text: str) -> dict:
        # Use BERT if available
        if self.model and self.tokenizer:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                confidence, index = torch.max(probs, dim=-1)
                best_type = self.crime_types[index.item()]
                return {
                    'crime_type': best_type,
                    'confidence': confidence.item()
                }

        # Fallback to keyword-based
        text = text.lower()
        scores = {ct: 0 for ct in self.crime_types}
        for ct, kws in self.keywords.items():
            for kw in kws:
                if kw in text:
                    scores[ct] += 1
        
        best_type = max(scores, key=scores.get)
        if scores[best_type] == 0:
            best_type = 'hacking'
            
        return {
            'crime_type': best_type,
            'confidence': min(1.0, scores[best_type] * 0.2)
        }

    def extract_keywords(self, text: str) -> list:
        # Simple keyword extraction
        found = []
        text = text.lower()
        for ct, kws in self.keywords.items():
            for kw in kws:
                if kw in text:
                    found.append(kw)
        return list(set(found))[:10]
