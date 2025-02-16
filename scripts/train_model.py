from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB  # Change to Naive Bayes

# Update vectorizer settings
tfidf = TfidfVectorizer(
    ngram_range=(1, 2),  # Use bigrams
    max_features=5000,   # Increase features
    min_df=2,           # Minimum document frequency
    stop_words='english'
)

# Use Naive Bayes instead of Logistic Regression
model = MultinomialNB() 