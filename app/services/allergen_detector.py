import joblib
from app.core.config import MODEL_PATH, VECTORIZER_PATH, LABEL_BINARIZER_PATH
from app.core.constants import INGREDIENTS
from app.utils.text_processing import get_evidence

class AllergenDetector:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.tfidf = joblib.load(VECTORIZER_PATH)
        self.mlb = joblib.load(LABEL_BINARIZER_PATH)

    def detect(self, text: str) -> dict:
        X = self.tfidf.transform([text])
        predictions_proba = self.model.predict_proba(X)
        
        # Calculate threshold
        ingredient_count = len(text.split(','))
        base_threshold = 0.3
        
        if "CONTAINS" in text.upper():
            base_threshold = 0.25
            
        threshold = min(base_threshold + (ingredient_count * 0.01), 0.5)
        
        # Get predictions
        allergen_predictions = []
        for idx, label in enumerate(self.mlb.classes_):
            if not label:
                continue
                
            prob = predictions_proba[idx][0][1]
            evidence = get_evidence(text, label)
            
            if evidence and any("Contains statement:" in e for e in evidence):
                prob = min(prob * 1.2, 1.0)
            
            if prob > threshold or evidence:
                allergen_predictions.append({
                    "allergen": label,
                    "confidence": float(prob),
                    "evidence": evidence
                })
        
        return {
            "allergens": sorted(allergen_predictions, 
                              key=lambda x: x["confidence"], 
                              reverse=True),
            "input_text": text,
            "threshold_used": threshold
        } 