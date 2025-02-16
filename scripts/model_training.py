#############################
# model_training.py
#############################
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, hamming_loss
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import precision_score

def preprocess_labels(labels):
    # Convert comma-separated string labels to lists
    return [set(l.split(',')) for l in labels]

def create_model():
    # Create text processing pipeline
    text_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=3000,
            min_df=2,
            max_df=0.95,
            analyzer='word',
            token_pattern=r'(?u)\b\w+\b|\([^)]*\)|\b\w+\s+\w+\b'
        )),
    ])

    # Create classifier pipeline
    clf_pipeline = Pipeline([
        ('rf', RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42
        ))
    ])

    return Pipeline([
        ('text', text_pipeline),
        ('clf', MultiOutputClassifier(clf_pipeline))
    ])

def train_model():
    # Load and preprocess data
    df = pd.read_csv("data/allergen_dataset.csv")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['ingredient_text'],
        df['allergens'].str.get_dummies(sep=','),
        test_size=0.2,
        random_state=42
    )
    
    # Create and train model
    model = create_model()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_proba = model.predict_proba(X_test)
    
    # Calibrate confidence scores
    for i, label in enumerate(y_train.columns):
        print(f"\nMetrics for {label}:")
        proba = y_pred_proba[i][:, 1]
        # Calculate and print precision at different thresholds
        for threshold in [0.3, 0.5, 0.7]:
            pred = (proba >= threshold).astype(int)
            print(f"Precision at {threshold}: {precision_score(y_test.iloc[:, i], pred):.3f}")

def main():
    # 1. Load dataset
    df = pd.read_csv("data/allergen_dataset.csv")
    
    # 2. Preprocess labels
    labels = preprocess_labels(df['allergens'])
    
    # 3. Convert labels to multi-hot encoding
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(labels)
    
    # 4. Enhanced TF-IDF vectorization
    tfidf = TfidfVectorizer(
        ngram_range=(1, 3),  # Include up to trigrams
        max_features=3000,    # Reduced from 5000 to prevent overfitting
        min_df=2,            # Ignore terms that appear in less than 2 documents
        max_df=0.95,         # Ignore terms that appear in more than 95% of documents
        stop_words='english',
        token_pattern=r'(?u)\b\w+\b|\([^)]*\)',  # Include words and parenthetical phrases
        strip_accents='unicode'
    )
    X = tfidf.fit_transform(df['ingredient_text'])
    
    # 5. Split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )
    
    # 6. Initialize RandomForest with better parameters to prevent overfitting
    base_classifier = RandomForestClassifier(
        n_estimators=200,           # More trees
        max_depth=10,               # Limit depth to prevent overfitting
        min_samples_split=5,        # Require more samples to split
        min_samples_leaf=2,         # Require more samples in leaves
        max_features='sqrt',        # Use sqrt of features for each tree
        class_weight='balanced',    # Handle class imbalance
        n_jobs=-1,
        random_state=42
    )
    
    # 7. Train model
    model = MultiOutputClassifier(base_classifier, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 8. Detailed evaluation
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    print("Training Metrics:")
    print(f"Hamming Loss: {hamming_loss(y_train, y_pred_train):.4f}")
    print("\nTest Metrics:")
    print(f"Hamming Loss: {hamming_loss(y_test, y_pred_test):.4f}")
    
    # Print detailed metrics for each allergen
    print("\nDetailed Classification Report:")
    for i, allergen in enumerate(mlb.classes_):
        print(f"\nMetrics for {allergen}:")
        print(classification_report(
            y_test[:, i],
            y_pred_test[:, i],
            target_names=['No', 'Yes']
        ))
    
    # 9. Feature importance analysis
    feature_names = tfidf.get_feature_names_out()
    for i, allergen in enumerate(mlb.classes_):
        importances = model.estimators_[i].feature_importances_
        top_features = sorted(zip(importances, feature_names), reverse=True)[:10]
        print(f"\nTop 10 important features for {allergen}:")
        for importance, feature in top_features:
            print(f"{feature}: {importance:.4f}")
    
    # 10. Save the model and preprocessing objects
    joblib.dump(model, "model/allergen_model.pkl")
    joblib.dump(tfidf, "model/tfidf_vectorizer.pkl")
    joblib.dump(mlb, "model/label_binarizer.pkl")

if __name__ == "__main__":
    main()
