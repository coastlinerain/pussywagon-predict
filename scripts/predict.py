import pandas as pd
import joblib

model = joblib.load('../models/tasador_model.pkl')
model_columns = joblib.load('../models/model_columns.pkl')

def tasar_coche(brand, kms, fuel, cv, location, age):
   nuevo_coche = pd.DataFrame([{
        'Brand': brand.upper(), # Aseguramos mayúsculas
        'Kms_Driven': kms,
        'cc': cv,
        'Age': age,
        'Fuel_Type': fuel,
        'Location': location
    }])
   nuevo_coche = pd.get_dummies(nuevo_coche)
   nuevo_coche = nuevo_coche.reindex(columns=model_columns, fill_value=0)
   prediccion = model.predict(nuevo_coche)[0]
   return prediccion

# --- EJEMPLO DE USO ---
# Imagina que ves un anuncio: 80.000km, Diesel, 150cv, Madrid, 5 años (2021)
precio_estimado = tasar_coche("MERCEDES-BENZ", 190000, 'Diesel', 150, 'Gipuzkoa', 5)

print(f"\nSegún el mercado, este coche debería costar: {precio_estimado:,.2f} €")