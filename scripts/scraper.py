import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def auto_scroll(page):
    print("Haciendo scroll para cargar todos los anuncios...")
    for _ in range(8):
        await page.keyboard.press("PageDown")
        await asyncio.sleep(random.uniform(0.5, 1)) # Pausa corta entre scrolls
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(random.uniform(2, 5))

async def main():
    NUM_PAGINAS = 500 
    coches_data = []

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}, # Forzamos un tamaño de pantalla grande
            locale="es-ES",
    		timezone_id="Europe/Madrid"
        )
        page = await context.new_page()

        for i in range(201, NUM_PAGINAS + 1):
            url = f"https://www.coches.net/segunda-mano/?PriceMax=15000&pg={i}"
            print(f"\n--- Extrayendo Página {i}: {url} ---")
            
            try:
                await page.goto(url, wait_until="load", timeout=60000)
                
                if i == 201:
                    try:
                        await page.click("button#didomi-notice-agree-button", timeout=5000)
                        print("Cookies aceptadas.")
                    except:
                        pass

                await auto_scroll(page)

                await page.wait_for_selector(".sui-AtomCard-info", timeout=15000)
                items = await page.query_selector_all(".sui-AtomCard-info")
                print(f"Encontrados {len(items)} contenedores de anuncios en esta página.")

                for item in items:
                    try:
                        title = await item.query_selector(".mt-CardAd-infoHeaderTitle") 
                        price = await item.query_selector(".mt-CardAdPrice-cashAmount")
                        attributes = await item.query_selector_all(".mt-CardAd-attrItem")
                        link_element = await item.query_selector(".mt-CardAd-infoHeaderTitleLink")
                        relative_url = await link_element.get_attribute("href") if link_element else ""

                        full_url = f"https://www.coches.net{relative_url}" if relative_url else "N/A"
                        if not title or not price: continue

                        nombre = await title.inner_text()
                        precio = await price.inner_text()
                        brand = nombre.split(' ')[0].upper()
                        attr_list = [await a.inner_text() for a in attributes]
                        if len(attr_list) >= 3:
                            year = attr_list[1]
                            kms = attr_list[2]
                            fuel = attr_list[0]
                            ubicacion = attr_list[4]
                            cc = attr_list[3]
                        else:
                            year = kms = fuel = None

                        coches_data.append({
                            "Brand": brand,
                            "Car_Name": nombre,
                            "Selling_Price": precio,
                            "Year": year,
                            "Kms_Driven": kms,
                            "Fuel_Type": fuel,
                            "cc": cc,
                            "Location": ubicacion,
                            "Ref": full_url 
                        })
                    except Exception as e:
                        print(f"Error parseando un anuncio: {e}")
                        continue
                
                print(f"Total acumulado: {len(coches_data)} ofertas.")
                await asyncio.sleep(2) 

            except Exception as e:
                print(f"Error crítico en página {i}: {e}")
                break 

        await browser.close()

        if coches_data:
            df = pd.DataFrame(coches_data)
            df = df.drop_duplicates(subset=["Car_Name", "Selling_Price", "Kms_Driven"])
            df.to_csv("../csv/coches_net_live.csv", index=False)
            print(f"\n¡Éxito! Total de ofertas ÚNICAS guardadas: {len(df)}")
            print(df.head())
        else:
            print("No se extrajo nada. Revisa los selectores CSS.")

if __name__ == "__main__":
    asyncio.run(main())