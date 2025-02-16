from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "model"
DATA_DIR = BASE_DIR / "data"

# Model files
MODEL_PATH = MODEL_DIR / "allergen_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
LABEL_BINARIZER_PATH = MODEL_DIR / "label_binarizer.pkl"

# Thresholds
BASE_THRESHOLD = 0.3
MAX_THRESHOLD = 0.5
INGREDIENT_THRESHOLD_FACTOR = 0.01 