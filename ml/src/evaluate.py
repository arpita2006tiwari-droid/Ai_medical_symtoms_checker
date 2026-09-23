import pandas as pd
import os
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def evaluate_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')
    
    os.makedirs(reports_dir, exist_ok=True)
    
    # Load test set
    X_test = pd.read_csv(os.path.join(processed_dir, 'X_test.csv'))
    y_test = pd.read_csv(os.path.join(processed_dir, 'y_test.csv')).squeeze()
    
    models = {
        'Random Forest': 'symptom_random_forest.joblib',
        'Naive Bayes': 'symptom_naive_bayes.joblib',
        'Decision Tree': 'symptom_decision_tree.joblib'
    }
    
    results = []
    
    with open(os.path.join(reports_dir, 'model_evaluation.txt'), 'w') as f:
        f.write("MODEL EVALUATION\n\n")
        
        for name, filename in models.items():
            model_path = os.path.join(models_dir, filename)
            if not os.path.exists(model_path):
                print(f"Model file {filename} not found.")
                continue
                
            model = joblib.load(model_path)
            y_pred = model.predict(X_test)
            
            # Using weighted average due to potential class imbalance
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            results.append({
                'Model': name,
                'Accuracy': acc,
                'Precision': prec,
                'Recall': rec,
                'F1_Score': f1
            })
            
            f.write(f"{name}\n")
            f.write(f"Accuracy: {acc:.4f}\n")
            f.write(f"Precision: {prec:.4f}\n")
            f.write(f"Recall: {rec:.4f}\n")
            f.write(f"F1-score: {f1:.4f}\n\n")
            
            # Save confusion matrix for Random Forest
            if name == 'Random Forest':
                cm = confusion_matrix(y_test, y_pred)
                cm_df = pd.DataFrame(cm, index=model.classes_, columns=model.classes_)
                cm_df.to_csv(os.path.join(reports_dir, 'rf_confusion_matrix.csv'))
                
    # Save comparison report
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(reports_dir, 'model_comparison.csv'), index=False)
    print("Evaluation completed. Reports saved.")

if __name__ == "__main__":
    evaluate_models()
