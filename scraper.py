import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def main():
    # This is the recommended usage. All pages created will have stealth applied:
    async with Stealth().use_async(async_playwright()) as p:
                 
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://www.coches.net/segunda-mano/?PriceMax=15000"
        print(f"Navegando a: {url}")
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
		# Aceptar cookies
        try:
            await page.click("button:has-text('Aceptar')", timeout=5000)
            print("Cookies aceptadas.")
        except:
            print("No se encontró el botón de cookies o ya se aceptaron.")

        coches_data = []
        
		# Esperar a que los anuncios carguen en el DOM
        await page.wait_for_selector(".sui-AtomCard-info", timeout=10000)
        items = await page.query_selector_all(".sui-AtomCard-info")
        for item in items:
            try:
                title = await item.query_selector(".mt-CardAd-infoHeaderTitle") # El título suele ser un h2
                price = await item.query_selector(".mt-CardAdPrice-cashAmount")
                attributes = await item.query_selector_all(".mt-CardAd-attrItem")
                
                nombre = await title.inner_text() if title else "N/A"
                precio = await price.inner_text() if price else "0"
                
                attr_list = [await a.inner_text() for a in attributes]
                
                coches_data.append({
                    "Car_Name": nombre,
                    "Selling_Price": precio,
                    "Year": attr_list[1] if len(attr_list) > 0 else None,
                    "Kms_Driven": attr_list[2] if len(attr_list) > 1 else None,
                    "Fuel_Type": attr_list[0] if len(attr_list) > 2 else None
                })
            except Exception as e:
                continue
        await browser.close()
        if coches_data:
                     df = pd.DataFrame(coches_data)
                     df.to_csv("coches_net_live.csv", index=False)
                     print(f"¡Hecho! Se han guardado {len(df)} ofertas en coches_net_live.csv.")
                     print(df.head()) # Ver una muestra
        else:
                     print("No se pudieron extraer datos. Puede que los selectores CSS hayan cambiado.")

asyncio.run(main())