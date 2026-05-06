import pandas as pd
from xgboost import XGBRegressor
import joblib
import os

os.makedirs('models', exist_ok=True)

# 1. Cargar datos
df = pd.read_csv('csv/coches_net_total.csv')

# --- LIMPIEZA BÁSICA ---
df['Selling_Price'] = df['Selling_Price'].str.replace('€', '').str.replace('.', '').str.strip().astype(float)
df['Kms_Driven'] = df['Kms_Driven'].str.replace(r'\D', '', regex=True).astype(int)
df['cc'] = df['cc'].str.replace('cv', '').str.strip().astype(int)
df['Age'] = 2026 - df['Year']


# A. Extraer Marca, Modelo y Submodelo de forma universal (casi xd)
split_name = df['Car_Name'].str.split()
df['Brand'] = split_name.str[0].str.upper()
df['Model_Base'] = split_name.str[1].str.upper()
df['Sub_Model'] = split_name.str[2].str.upper().fillna('')

df['Gama'] = (df['Model_Base'] + " " + df['Sub_Model']).str.strip()

# B. Variable de Riesgo: (modelos viejos gama alta caros de mantener)
df['Luxury_Risk'] = df['cc'] * df['Age']

# C. Variable de Uso: 
df['Km_Per_Year'] = df['Kms_Driven'] / (df['Age'] + 1)

# 2. Preparar Features
# Eliminamos las columnas auxiliares que ya no necesitamos
features = ['Brand', 'Gama', 'Kms_Driven', 'cc', 'Age', 'Fuel_Type', 'Location', 'Luxury_Risk', 'Km_Per_Year', 'Etiqueta']
X = df[features]

# Convertimos a dummies
X = pd.get_dummies(X, columns=['Brand', 'Gama', 'Fuel_Type', 'Location', 'Etiqueta'], drop_first=True)
y = df['Selling_Price']

# 3. Entrenar modelo
model = XGBRegressor(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42)
model.fit(X, y)

# 4. GUARDAR MODELO Y COLUMNAS
joblib.dump(model, 'models/tasador_model.pkl')
joblib.dump(X.columns.tolist(), 'models/model_columns.pkl')

print(f"✅ Modelo entrenado con {X.shape[1]} variables.")
print(f"✅ Se han identificado {df['Gama'].nunique()} gamas de vehículos diferentes.")