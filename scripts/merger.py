import pandas as pd
import glob
import os

def merge_car_csvs(output_filename="csv/coches_net_total.csv"):
    archivos = glob.glob("csv/coches_net_*.csv")
    
    if not archivos:
        print("❌ No se encontraron archivos CSV para unir.")
        return

    print(f"📂 Encontrados {len(archivos)} archivos. Empezando fusión...")

    lista_df = []

    for archivo in archivos:
        try:
            # Leemos cada fragmento
            df_temp = pd.read_csv(archivo)
            lista_df.append(df_temp)
            print(f"✅ Leído: {archivo} ({len(df_temp)} filas)" )
        except Exception as e:
            print(f"⚠️ Error al leer {archivo}: {e}")

    df_total = pd.concat(lista_df, ignore_index=True)

    antes = len(df_total)
    df_total.drop_duplicates(subset=['Ref'], inplace=True)
    después = len(df_total)

    df_total.to_csv(output_filename, index=False)
    
    print("-" * 30)
    print(f"🏆 Fusión completada: {output_filename}")
    print(f"📊 Filas totales iniciales: {antes}")
    print(f"✨ Filas tras eliminar duplicados: {después}")
    print(f"🧹 Se eliminaron {antes - después} anuncios repetidos.")

if __name__ == "__main__":
    merge_car_csvs()