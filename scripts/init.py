import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 1. Cargar datos
df = pd.read_csv('csv/coches_net_live.csv')

df['Selling_Price'] = df['Selling_Price'].str.replace('€', '').str.replace('.', '').str.strip().astype(float)

df['Kms_Driven'] = df['Kms_Driven'].str.replace('km', '').str.replace('.', '').str.strip().astype(int)

df['cc'] = df['cc'].str.replace('cv', '').str.strip().astype(int)

df['Age'] = 2026 - df['Year']

car_info = df[['Car_Name', 'Ref']]

X_total = df.drop(['Selling_Price', 'Year', 'Car_Name', 'Ref'], axis=1)

# One-Hot Encoding para Fuel_Type y Location
X_total = pd.get_dummies(X_total, columns=['Fuel_Type', 'Location'], drop_first=True)

y_total = df['Selling_Price']

# 3. Split
X_train, X_test, y_train, y_test = train_test_split(X_total, y_total, test_size=0.2, random_state=42)

# 4. Entrenar
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 5. Evaluación y Resultados
score = model.score(X_test, y_test)
print(f"Precisión (R^2 Score) con datos reales: {score:.4f}")

# 6. Tabla Final de Oportunidades
test_results = pd.DataFrame(index=X_test.index)
test_results['Car_Name'] = df.loc[X_test.index, 'Car_Name']
test_results['Real_Price'] = y_test
test_results['Predicted_Price'] = model.predict(X_test)
test_results['URL'] = df.loc[X_test.index, 'Ref'] # Añadimos el link para ir directo

# Calculamos oportunidad
test_results['Oportunidad_%'] = ((test_results['Predicted_Price'] - test_results['Real_Price']) / test_results['Predicted_Price']) * 100

print("\n--- TOP 10 MEJORES OPORTUNIDADES ---")

top_gangas = test_results.sort_values(by='Oportunidad_%', ascending=False).head(10)
print(top_gangas[['Car_Name', 'Real_Price', 'Predicted_Price', 'Oportunidad_%']])

top_gangas.to_excel("excel/resultados_compra.xlsx")