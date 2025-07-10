from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time
import random
from datetime import datetime


#https://es.wallapop.com/search?keywords=Auriculares&category_id=24200&source=seo_landing

# ✅ Lista de URLs y nombres de archivo
urls_info = [
    {"nombre": "ordenadores", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=ordenadores"},
    {"nombre": "portatiles", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=portatil"},
    {"nombre": "impresoras3d", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=impresoras3D"},
    {"nombre": "monitores", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=monitor"},
    {"nombre": "juegos", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=juegos"},
    {"nombre": "auriculares", "url": "https://es.wallapop.com/source=search_box&category_id=24200&keywords=auriculares"},
    {"nombre": "iphones", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=iphon"},
    {"nombre": "tabl_digi", "url": "https://es.wallapop.com/search?source=search_box&category_id=24200&keywords=tabletas+digitalizadores"}
]

# ✅ Configuraciones generales
LIMITE_PRODUCTOS = 5000
WAIT_TIME = 4

# ⚙️ Configurar navegador
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

# 🔁 Ejecutar scraping para cada URL
for item in urls_info:
    nombre = item["nombre"]
    url = item["url"]
    print(f"\n🚀 Iniciando scraping para: {nombre} ({url})")
    driver.get(url)
    time.sleep(WAIT_TIME)

    # 🔁 Scroll dinámico
    prev_count = -1
    scrolls = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2.5, 4))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 400);")
        time.sleep(5)

        productos = driver.find_elements(By.CSS_SELECTOR, "a.item-card_ItemCard--vertical__FiFz6")
        current_count = len(productos)
        print(f"🔄 Scroll #{scrolls + 1}: {current_count} productos")

        if current_count >= LIMITE_PRODUCTOS:
            print(f"✅ Límite de {LIMITE_PRODUCTOS} productos alcanzado.")
            break

        if current_count == prev_count:
            print("✅ No se cargan más productos. Fin del scroll.")
            break

        prev_count = current_count
        scrolls += 1

    # 📦 Guardar CSV
    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"{nombre}_wallapop_{fecha_hora}.csv"

    with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Título", "Precio", "URL", "Imagen"])

        urls_vistas = set()
        count = 0

        for producto in productos:
            if count >= LIMITE_PRODUCTOS:
                break
            try:
                url_producto = producto.get_attribute("href")
                if url_producto in urls_vistas:
                    continue
                urls_vistas.add(url_producto)

                titulo = producto.find_element(By.CSS_SELECTOR, "h3.item-card_ItemCard__title__8eq2b").text.strip()
                precio = producto.find_element(By.CSS_SELECTOR, "strong.item-card_ItemCard__price__D3QWU").text.strip()
                imagen = producto.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

                print(f"✅ {titulo} | {precio}")
                writer.writerow([titulo, precio, url_producto, imagen])
                count += 1
            except Exception as e:
                print("⚠️ Producto omitido:", e)

    print(f"📁 Archivo guardado: {nombre_archivo}")

driver.quit()
print("\n🎉 Scraping finalizado para todas las categorías.")
