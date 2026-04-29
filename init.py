import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 1. Cargar datos
df = pd.read_csv('car_data.csv')

# 2. Ingeniería de Variables
df['Age'] = 2026 - df['Year']

# 3. Preparar los datos para el modelo (Quitamos el nombre aquí para el encoding)
# Pero guardamos una copia de los nombres vinculada al índice
car_names = df['Car_Name']

# Creamos el set de entrenamiento eliminando lo que no es numérico/útil
X_total = df.drop(['Selling_Price', 'Year', 'Car_Name'], axis=1)
X_total = pd.get_dummies(X_total, columns=['Fuel_Type', 'Seller_Type', 'Transmission'], drop_first=True)
y_total = df['Selling_Price']

# 4. Split (usamos random_state para que los resultados sean reproducibles)
X_train, X_test, y_train, y_test = train_test_split(X_total, y_total, test_size=0.2, random_state=42)

# 5. Entrenar
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 6. Evaluación y Resultados
score = model.score(X_test, y_test)
print(f"Precisión (R^2 Score): {score:.4f}")

# Creamos la tabla final usando el índice de X_test para recuperar los nombres
test_results = pd.DataFrame(index=X_test.index)
test_results['Car_Name'] = df.loc[X_test.index, 'Car_Name'] # Recuperamos el nombre original
test_results['Real_Price'] = y_test
test_results['Predicted_Price'] = model.predict(X_test)

# Calculamos oportunidad
test_results['Oportunidad_%'] = ((test_results['Predicted_Price'] - test_results['Real_Price']) / test_results['Predicted_Price']) * 100

print("\n--- ANÁLISIS DE OPORTUNIDADES ---")
# Ordenamos de mayor a menor oportunidad
print(test_results[['Car_Name', 'Real_Price', 'Predicted_Price', 'Oportunidad_%']].sort_values(by='Oportunidad_%', ascending=False))