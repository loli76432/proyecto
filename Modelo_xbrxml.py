from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd

helb = (r'F:\00Proyecto_final\Datos\resultado.csv')
df = pd.read_csv(helb)
df.head(2)

# Features relevantes
features = ['Título','Imagen', 'marca', 'marca_categoria',
       'marca_caracteristicas', 'marca_confianza', 'marca_alternativas']
target = 'Precio'

# Codificación simple de categóricas
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), features)
])

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor())
])

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model.fit(X_train, y_train)

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")

import joblib 
joblib.dump(model, r"F:\00Proyecto_final\Scripts\modelos_xbx\modelo_xbrxml.pkl")