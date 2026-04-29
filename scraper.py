import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    # Configuración: ¿Cuántas páginas quieres scrapear?
    NUM_PAGINAS = 5 
    coches_data = []

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for i in range(1, NUM_PAGINAS + 1):
            # Construimos la URL dinámica con el parámetro pg
            url = f"https://www.coches.net/segunda-mano/?PriceMax=15000&pg={i}"
            print(f"--- Extrayendo Página {i}: {url} ---")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                if i == 1:
                    try:
                        await page.click("button:has-text('Aceptar')", timeout=5000)
                        print("Cookies aceptadas.")
                    except:
                        pass

                await page.wait_for_selector(".sui-AtomCard-info", timeout=10000)
                items = await page.query_selector_all(".sui-AtomCard-info")

                for item in items:
                    try:
                        title = await item.query_selector(".mt-CardAd-infoHeaderTitle")
                        price = await item.query_selector(".mt-CardAdPrice-cashAmount")
                        attributes = await item.query_selector_all(".mt-CardAd-attrItem")
                        
                        nombre = await title.inner_text() if title else "N/A"
                        precio = await price.inner_text() if price else "0"
                        attr_list = [await a.inner_text() for a in attributes]
                        
                        coches_data.append({
                            "Car_Name": nombre,
                            "Selling_Price": precio,
                            "Year": attr_list[1] if len(attr_list) > 1 else None,
                            "Kms_Driven": attr_list[2] if len(attr_list) > 2 else None,
                            "Fuel_Type": attr_list[0] if len(attr_list) > 0 else None
                        })
                    except:
                        continue
                
                # IMPORTANTE: Pausa de cortesía para evitar bloqueos
                print(f"Página {i} completada. Esperando...")
                await asyncio.sleep(2) 

            except Exception as e:
                print(f"Error en página {i}: {e}")
                break # Si una página falla críticamente, paramos

        await browser.close()

        if coches_data:
            df = pd.DataFrame(coches_data)
            # Eliminar duplicados si los hay (a veces los destacados se repiten)
            df = df.drop_duplicates()
            df.to_csv("coches_net_live.csv", index=False)
            print(f"\n¡Éxito! Total de ofertas guardadas: {len(df)}")
        else:
            print("No se extrajo nada.")

if __name__ == "__main__":
    asyncio.run(main())