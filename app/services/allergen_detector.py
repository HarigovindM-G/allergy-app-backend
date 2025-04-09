import joblib
from app.core.config import MODEL_PATH, VECTORIZER_PATH, LABEL_BINARIZER_PATH
from app.core.constants import INGREDIENTS
from app.utils.text_processing import get_evidence

class AllergenDetector:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.tfidf = joblib.load(VECTORIZER_PATH)
        self.mlb = joblib.load(LABEL_BINARIZER_PATH)
        
        # Adjusted thresholds - lowered for better detection of direct ingredients
        self.primary_threshold = 0.35    # For direct ingredients
        self.secondary_threshold = 0.25   # For "may contain" statements

    def detect(self, text: str) -> dict:
        X = self.tfidf.transform([text])
        predictions_proba = self.model.predict_proba(X)
        
        # Use instance thresholds
        primary_threshold = self.primary_threshold
        secondary_threshold = self.secondary_threshold
        
        allergen_predictions = []
        for idx, label in enumerate(self.mlb.classes_):
            if not label:
                continue
                
            prob = predictions_proba[idx][0][1]
            evidence = get_evidence(text, label)
            
            if evidence:
                # Direct ingredients or "Contains" statements
                if any("Contains statement:" in e for e in evidence) or any(term.lower() in text.lower() for term in INGREDIENTS[label]):
                    # Increase confidence for direct ingredient mentions
                    prob = min(prob * 1.5, 1.0)  # Increased from 1.2 to 1.5
                    if prob >= primary_threshold:
                        allergen_predictions.append({
                            "allergen": label,
                            "confidence": float(prob),
                            "evidence": evidence
                        })
                # "May contain" statements
                elif any("may contain" in e.lower() or "traces of" in e.lower() for e in evidence):
                    if prob >= secondary_threshold:
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
            "threshold_used": primary_threshold
        }

    def detect_allergens(self, text: str) -> list[dict]:
        allergens = []
        predictions = self.model.predict_proba(self.tfidf.transform([text]))[0]
        
        for idx, confidence in enumerate(predictions):
            allergen = self.mlb.classes_[idx]
            evidence = get_evidence(text, allergen)
            
            # Only include high confidence predictions with evidence
            if evidence and confidence >= self.primary_threshold:
                allergens.append({
                    "allergen": allergen,
                    "confidence": float(confidence),
                    "evidence": evidence
                })
            # Include lower confidence predictions only for "may contain" statements
            elif evidence and "may contain" in str(evidence).lower() and confidence >= self.secondary_threshold:
                allergens.append({
                    "allergen": allergen,
                    "confidence": float(confidence),
                    "evidence": evidence
                })
                
        return sorted(allergens, key=lambda x: x["confidence"], reverse=True) 