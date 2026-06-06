from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class NERExtractor:
    def __init__(self, model_name="Leo97/KoELECTRA-small-v3-modu-ner"):
        logger.info(f"Loading NER model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
            self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")
            # Label mapping for Korean model (Leo97/KoELECTRA labels: PS, OG, LC, DT, TI, etc.)
            self.label_map = {
                "PS": "PER",
                "OG": "ORG",
                "LC": "LOC",
                "PER": "PER", # Fallback for other models
                "ORG": "ORG",
                "LOC": "LOC"
            }
        except Exception as e:
            logger.error(f"Error loading NER model: {e}")
            self.nlp = None

    def extract_entities(self, text):
        if not text or not self.nlp:
            return {}
        
        try:
            results = self.nlp(text[:1000]) # Limit length for performance
            entities = {
                "PER": [],  # Persons
                "ORG": [],  # Organizations (Hacker groups, companies)
                "LOC": [],  # Locations
                "MISC": []  # Miscellaneous
            }
            
            for res in results:
                label = res['entity_group']
                word = res['word']
                
                # Map label to our standard format
                mapped_label = self.label_map.get(label, "MISC")
                
                if mapped_label in entities:
                    if word not in entities[mapped_label]:
                        entities[mapped_label].append(word)
            
            return entities
        except Exception as e:
            logger.error(f"Error during NER extraction: {e}")
            return {}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractor = NERExtractor()
    
    # Test with English
    test_text_en = "Lazarus Group attacked Sony Pictures in 2014. The FBI investigated the case in Washington."
    print(f"EN Text: {test_text_en}")
    print(f"Extracted Entities (EN): {extractor.extract_entities(test_text_en)}")
    
    print("-" * 30)
    
    # Test with Korean
    test_text_ko = "라자루스 그룹은 2014년 소니 픽처스를 공격했습니다. FBI는 워싱턴에서 이 사건을 조사했습니다."
    print(f"KO Text: {test_text_ko}")
    print(f"Extracted Entities (KO): {extractor.extract_entities(test_text_ko)}")
