import pandas as pd
from xgboost import XGBRegressor
import joblib

df = pd.read_csv('../csv/coches_net_live.csv')
df['Selling_Price'] = df['Selling_Price'].str.replace('€', '').str.replace('.', '').str.strip().astype(float)
df['Kms_Driven'] = df['Kms_Driven'].str.replace('km', '').str.replace('.', '').str.strip().astype(int)
df['cc'] = df['cc'].str.replace('cv', '').str.strip().astype(int)
df['Age'] = 2026 - df['Year']

# 2. Preparar Features
X = df.drop(['Selling_Price', 'Year', 'Car_Name', 'Ref'], axis=1)
X = pd.get_dummies(X, columns=['Brand', 'Fuel_Type', 'Location'], drop_first=True)
y = df['Selling_Price']

# 3. Entrenar modelo completo (usamos todos los datos para máxima potencia)
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X, y)

# 4. GUARDAR MODELO Y COLUMNAS
joblib.dump(model, '../models/tasador_model.pkl')
joblib.dump(X.columns.tolist(), '../models/model_columns.pkl')

print("✅ Modelo y columnas guardados correctamente.")