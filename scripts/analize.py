import pandas as pd
import joblib

# 1. Cargar el modelo y las columnas maestras
try:
    model = joblib.load('models/tasador_model.pkl')
    model_columns = joblib.load('models/model_columns.pkl')
    print("✅ Modelo cargado correctamente.")
except FileNotFoundError:
    print("❌ Error: No se encuentran 'tasador_model.pkl' o 'model_columns.pkl'.")
    print("Debes entrenar el modelo primero.")
    exit()

# 2. Cargar datos nuevos del Scraper
df = pd.read_csv('csv/coches_net_total.csv')

df_proc = df.copy()

# Limpiamos strings a números
df_proc['Selling_Price'] = df['Selling_Price'].str.replace('€', '').str.replace('.', '').str.strip().astype(float)
df_proc['Kms_Driven'] = df['Kms_Driven'].str.replace('km', '').str.replace('.', '').str.strip().astype(int)
df_proc['cc'] = df['cc'].str.replace('cv', '').str.strip().astype(int)
df_proc['Age'] = 2026 - df['Year']

# Extraemos la Marca (Primera palabra)
df_proc['Brand'] = df['Brand']

X = df_proc[['Brand', 'Kms_Driven', 'cc', 'Age', 'Fuel_Type', 'Location']]

X = pd.get_dummies(X)

X = X.reindex(columns=model_columns, fill_value=0)

# 5. Predicción masiva
print("🔮 Calculando precios justos...")
precios_predichos = model.predict(X)

# 6. Creación de la tabla de resultados
resultados = pd.DataFrame({
    'Car_Name': df['Car_Name'],
    'Real_Price': df_proc['Selling_Price'],
    'Predicted_Price': precios_predichos,
    'URL': df['Ref']
})

# Cálculo de la oportunidad
# Si el precio predicho es mayor al real, es una ganga potencial
resultados['Oportunidad_%'] = ((resultados['Predicted_Price'] - resultados['Real_Price']) / resultados['Predicted_Price']) * 100

# 7. Filtrado y Formateo
chollos = resultados.sort_values(by='Oportunidad_%', ascending=False)

print("\n--- 🚀 TOP 10 MEJORES OPORTUNIDADES ENCONTRADAS ---")
# Mostramos el Top 10 por pantalla
top_10 = chollos.head(10)
print(top_10[['Car_Name', 'Real_Price', 'Predicted_Price', 'Oportunidad_%']])

# 8. Guardar resultados
try:
    chollos.to_excel("excel/analisis_csv.xlsx", index=False)
    print("\n✅ Análisis completo. Archivo 'analisis_csv.xlsx' generado.")
except ImportError:
    chollos.to_csv("excel/analisis_nuevo.csv", index=False)
    print("\n✅ Análisis completo. Archivo 'analisis_compras_real.csv' generado (Instala 'openpyxl' para Excel).")