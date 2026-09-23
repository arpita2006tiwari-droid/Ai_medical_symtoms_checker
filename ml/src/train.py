import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier

def train_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    models_dir = os.path.join(base_dir, 'models')
    
    os.makedirs(models_dir, exist_ok=True)
    
    # Load processed data
    df = pd.read_csv(os.path.join(processed_dir, 'processed_symptom_dataset.csv'))
    
    X = df.drop(columns=['Disease'])
    y = df['Disease']
    
    # Train/test split (80/20) with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save test set for evaluation script
    X_test.to_csv(os.path.join(processed_dir, 'X_test.csv'), index=False)
    y_test.to_csv(os.path.join(processed_dir, 'y_test.csv'), index=False)
    
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    joblib.dump(rf, os.path.join(models_dir, 'symptom_random_forest.joblib'))
    
    print("Training Naive Bayes...")
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    joblib.dump(nb, os.path.join(models_dir, 'symptom_naive_bayes.joblib'))
    
    print("Training Decision Tree...")
    dt = DecisionTreeClassifier(random_state=42, class_weight='balanced')
    dt.fit(X_train, y_train)
    joblib.dump(dt, os.path.join(models_dir, 'symptom_decision_tree.joblib'))
    
    print("All models trained and saved successfully.")

if __name__ == "__main__":
    train_models()
