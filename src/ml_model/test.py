import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, FunctionTransformer, StandardScaler
from xgboost import XGBClassifier
import joblib


# ----------------------------

# Load data
df = pd.read_csv('heart.csv')
df["ExerciseAngina"] = df["ExerciseAngina"].map({"No": 0, "Yes": 1})

X = df.drop(columns=['HeartDisease'])
y = df['HeartDisease']

# Feature groups
one_hot_cols = ['Sex', 'ChestPainType', 'RestingECG']
binary_cols = ['ExerciseAngina']
ordinal_cols = ['ST_Slope']
numeric_cols = X.drop(columns=one_hot_cols + binary_cols + ordinal_cols).columns.tolist()

# Preprocessor
preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), numeric_cols),
   
    ('ord', OrdinalEncoder(categories=[['Down', 'Flat', 'Up']]), ordinal_cols),
    ('onehot', OneHotEncoder(drop='first', sparse_output=False), one_hot_cols)
])

# Final pipeline
final_pipeline = Pipeline(steps=[
    ('preprocessing', preprocessor),
    ('classifier', XGBClassifier(
        use_label_encoder=False,
        eval_metric='logloss',
        subsample=1,
        n_estimators=100,
        max_depth=7,
        learning_rate=0.01,
        colsample_bytree=0.7,
        random_state=42
    ))
])

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
final_pipeline.fit(X_train, y_train)


# ----------------------------
joblib.dump(final_pipeline, 'heart_pipeline.joblib')
print("✅ Model pipeline saved as heart_pipeline.joblib")