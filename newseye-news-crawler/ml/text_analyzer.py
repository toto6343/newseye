import re

class TextAnalyzer:
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove multiple whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
