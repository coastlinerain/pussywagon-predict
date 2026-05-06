import pandas as pd
import joblib
from sklearn.metrics import r2_score

# 1. Cargar el modelo y las columnas maestras
try:
    model = joblib.load('models/tasador_model.pkl')
    model_columns = joblib.load('models/model_columns.pkl')
    print("✅ Modelo cargado correctamente.")
except FileNotFoundError:
    print("❌ Error: No se encuentran los archivos en /models/. Entrena el modelo primero.")
    exit()

# 2. Cargar datos nuevos
df = pd.read_csv('csv/coches_net_total.csv')
df_proc = df.copy()

# 3. Limpieza y Procesamiento
df_proc['Selling_Price'] = df['Selling_Price'].str.replace('€', '').str.replace('.', '').str.strip().astype(float)
df['Kms_Driven'] = df['Kms_Driven'].str.replace(r'\D', '', regex=True).astype(int)
df_proc['cc'] = df['cc'].str.replace('cv', '').str.strip().astype(int)
df_proc['Age'] = 2026 - df['Year']

# --- logica de gammas ---
split_name = df['Car_Name'].str.split()
df_proc['Brand'] = split_name.str[0].str.upper()
df_proc['Model_Base'] = split_name.str[1].str.upper()
df_proc['Sub_Model'] = split_name.str[2].str.upper().fillna('')
df_proc['Gama'] = (df_proc['Model_Base'] + " " + df_proc['Sub_Model']).str.strip()

# --- VARIABLES DE CÁLCULO ---
df_proc['Luxury_Risk'] = df_proc['cc'] * df_proc['Age']
df_proc['Km_Per_Year'] = df_proc['Kms_Driven'] / (df_proc['Age'] + 1)

# 4. Seleccionar las columnas
features = ['Brand', 'Gama', 'Kms_Driven', 'cc', 'Age', 'Fuel_Type', 'Location', 'Luxury_Risk', 'Km_Per_Year', 'Etiqueta']
X = df_proc[features]

# Convertir a dummies
X = pd.get_dummies(X)

# Alinear columnas con el entrenamiento
X = X.reindex(columns=model_columns, fill_value=0)

print("🔮 Calculando precios justos con el nuevo motor de Gamas...")
precios_predichos = model.predict(X)

resultados = pd.DataFrame({
    'Car_Name': df['Car_Name'],
    'Modelo': df_proc['Model_Base'],
    'Sub-Model': df_proc['Sub_Model'],
    'Gama': df_proc['Gama'],
    'Kms': df_proc['Kms_Driven'],
    'Ubicacion': df['Location'],
    'Cv': df_proc['cc'],
    'Year': df['Year'],
    'Fuel': df_proc['Fuel_Type'],
    'Etiqueta': df['Etiqueta'],
    'Real_Price': df_proc['Selling_Price'],
    'Predicted_Price': precios_predichos,
    'URL': df['Ref'],
})

# Cálculo de la oportunidad
resultados['Oportunidad_%'] = ((resultados['Predicted_Price'] - resultados['Real_Price']) / resultados['Predicted_Price']) * 100

# Filtrado
chollos = resultados.sort_values(by='Oportunidad_%', ascending=False)

output_file = "excel/analisis.xlsx"
try:
    chollos.to_excel(output_file, index=False)
    print(f"\n✅ Análisis completo. Archivo '{output_file}' generado.")
except:
    chollos.to_csv("excel/analisis.csv", index=False)
    print("\n✅ Guardado como CSV (instala openpyxl para Excel).")

# Mostrar Top 5
print("\n🔥 TOP 5 GITANADAS!!!")
print(chollos[['Car_Name', 'Real_Price', 'Predicted_Price', 'Oportunidad_%']].head(5))

precision = r2_score(df_proc['Selling_Price'], precios_predichos)

print(f"Precisión del modelo en este lote: {precision:.4f}")

if precision < 0.70:
    print("⚠️  Aviso: La precisión es baja. Los chollos encontrados podrían no ser reales.")
elif precision > 0.95:
    print("Precisión excelente: El modelo clava los precios de este mercado.")