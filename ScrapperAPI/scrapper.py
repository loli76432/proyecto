import requests
import csv
from collections import defaultdict
from datetime import datetime
import time
import os

def timestamp_to_date(ts):
    try:
        return datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ""

def main(stop_event):
    os.system('cls' if os.name == 'nt' else 'clear')

    max_productos = 50000
    batch_save = 100
    pause_seconds = 0.5
    csv_file = "productosv3.csv"

    productos_vistos = set()
    if os.path.exists(csv_file):
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                productos_vistos.add(row["ID"])
        print(f"Se cargaron {len(productos_vistos)} IDs ya existentes desde {csv_file}")

    headers = {
        "accept-language": "es-ES;q=1.0",
        "mpid": "-3496566536215138340",
        "x-deviceid": "eUheXFi8S7-YjWtZ3k5Wvx:f8765ae5d89e3aff",
        "x-devicetoken": "52716367-4247-4891-9416-ef2cfbe64895",
        "x-deviceos": "1",
        "x-appversion": "10271000",
        "x-semanticversion": "1.271.0",
        "x-locationaccuracy": "10.0",
        "x-locationlatitude": "31.24916",
        "x-locationlongitude": "121.4878983",
        "host": "api.wallapop.com",
        "connection": "Keep-Alive",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.12.0"
    }

    search_url = "https://api.wallapop.com/api/v3/search"
    user_url_template = "https://api.wallapop.com/api/v3/users/{}"

    productos_detalle = []
    categorias_contador = defaultdict(int)

    
    next_page_token = "eyJhbGciOiJIUzI1NiJ9.eyJwYXJhbXMiOnsic2VhcmNoUmVxdWVzdFBhcmFtcyI6eyJsYXRpdHVkZSI6MzEuMjQ5MTYsImxvbmdpdHVkZSI6MTIxLjQ4Nzg5OCwiY2F0ZWdvcnlfaWQiOjI0MjAwLCJvcmRlcl9ieSI6InByaWNlX2xvd190b19oaWdoIiwic291cmNlIjoibm9uZSIsInNlYXJjaF9pZCI6IjY2MzdjMmQ2LTkzODMtNDRkMS1hMWJiLWY5ZGIxNjVkMjAxNiJ9LCJuZXh0UGFnZVBhcmFtcyI6eyJvZmZzZXQiOjgwLCJzdGVwIjowLCJpdGVtc19jb3VudCI6ODAsInNlY3Rpb25faXRlbXNfY291bnQiOjgwLCJpbnRlcm5hbF9zZWFyY2hfaWQiOiI1OTg5M2VlNC1mOWI1LTRjNjQtODMyZC1kZjQyYWRhMGMwZDgiLCJjb3VudHJ5X2NvZGUiOiJDTiIsImNpdHkiOiLmsZ_mub7kuaEo57qq5b-15p2RLOWMl-iWm-WutuWhmCnnrYkiLCJyZWdpb24iOiLkuIrmtbfluIIiLCJwb3N0YWxfY29kZSI6IjIwMDQzNyIsInNlY3Rpb25fdHlwZSI6ImNhdGVnb3J5X2ZlZWRfcmVzdWx0cyJ9fSwiZXhwIjoxNzUyNTczNzExfQ.XoUkhtCb1aIleq4zeaU6aqgz-zgEMWuQh0razyw92Fg"

    def guardar_csv():
        modo = "a" if os.path.exists(csv_file) else "w"
        with open(csv_file, mode=modo, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if modo == "w":
                writer.writerow([
                    "ID", "User ID", "Category ID", "Título", "Descripción", "Precio",
                    "Ciudad", "Región", "Región2", "Código Postal",
                    "URL Imagen", "Reservado",
                    "Es Enviable", "Usuario Permite Envío", "Favorito",
                    "Creado En", "Modificado En",
                    "Es Favoritable", "Está Refurbished", "Perfil Top", "Tiene Garantía",
                    "Categorías", "Enlace",
                    "User Micro Name", "User Gender", "User City", "User Register Date",
                    "User Image URL", "User Web Slug", "User URL Share"
                ])
            writer.writerows(productos_detalle)

    def guardar_categorias():
        with open("categoriasv3.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Categoría", "Cantidad"])
            for nombre_categoria, cantidad in categorias_contador.items():
                writer.writerow([nombre_categoria, cantidad])

    while next_page_token and len(productos_vistos) < max_productos:
        if stop_event.is_set():
            print("Stop event recibido. Deteniendo scraper...")
            break

        querystring = {
            "next_page": next_page_token,
            "country_code": "ES"
        }

        r = requests.get(search_url, headers=headers, params=querystring)
        if r.status_code != 200:
            print(f"Error al obtener datos: {r.status_code}")
            break

        data = r.json()
        items = data.get("data", {}).get("section", {}).get("payload", {}).get("items", [])

        for item in items:
            if stop_event.is_set():
                print("Stop event recibido dentro del loop. Deteniendo scraper...")
                break

            product_id = item.get("id")
            if product_id in productos_vistos:
                continue
            productos_vistos.add(product_id)

            print(f"Agregando producto ID: {product_id}")

            title = item.get("title", "")
            description = item.get("description", "").replace("\n", " ").strip()
            price_amount = item.get("price", {}).get("amount", 0)
            currency = item.get("price", {}).get("currency", "")
            price_str = f"{price_amount:.2f} {currency}" if currency else f"{price_amount:.2f}"

            city = item.get("location", {}).get("city", "")
            region = item.get("location", {}).get("region", "")
            postal_code = item.get("location", {}).get("postal_code", "")
            region2 = item.get("location", {}).get("region2", "")

            user_id = item.get("user_id", "")
            category_id = item.get("category_id", "")

            images = item.get("images", [])
            image_url = images[0]["urls"]["big"] if images else ""

            reserved_flag = item.get("reserved", {}).get("flag", False)
            shipping_info = item.get("shipping", {})
            item_is_shippable = shipping_info.get("item_is_shippable", False)
            user_allows_shipping = shipping_info.get("user_allows_shipping", False)
            favorited_flag = item.get("favorited", {}).get("flag", False)

            created_at = timestamp_to_date(item.get("created_at", 0))
            modified_at = timestamp_to_date(item.get("modified_at", 0))

            is_favoriteable_flag = item.get("is_favoriteable", {}).get("flag", False)
            is_refurbished_flag = item.get("is_refurbished", {}).get("flag", False)
            is_top_profile_flag = item.get("is_top_profile", {}).get("flag", False)
            has_warranty_flag = item.get("has_warranty", {}).get("flag", False)

            categorias = [cat["name"] for cat in item.get("taxonomy", [])]
            categorias_str = " > ".join(categorias)

            for cat in categorias:
                categorias_contador[cat] += 1

            slug = item.get("web_slug", "")
            web_url = f"https://es.wallapop.com/item/{slug}" if slug else ""

            user_data = {}
            if user_id:
                user_response = requests.get(user_url_template.format(user_id), headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                time.sleep(pause_seconds)

            user_micro_name = user_data.get("micro_name", "")
            user_gender = user_data.get("gender", "")
            user_location = user_data.get("location", {}).get("city", "")
            user_register_date = timestamp_to_date(user_data.get("register_date", 0))
            user_image_url = user_data.get("image", {}).get("urls_by_size", {}).get("original", "")
            user_web_slug = user_data.get("web_slug", "")
            user_url_share = user_data.get("url_share", "")

            productos_detalle.append([
                product_id, user_id, category_id, title, description, price_str,
                city, region, region2, postal_code,
                image_url, reserved_flag,
                item_is_shippable, user_allows_shipping, favorited_flag,
                created_at, modified_at,
                is_favoriteable_flag, is_refurbished_flag, is_top_profile_flag, has_warranty_flag,
                categorias_str, web_url,
                user_micro_name, user_gender, user_location, user_register_date,
                user_image_url, user_web_slug, user_url_share
            ])

            if len(productos_detalle) % batch_save == 0:
                guardar_csv()
                guardar_categorias()
                print(f"Guardado parcial: {len(productos_detalle)} productos nuevos")
                productos_detalle.clear()
                time.sleep(pause_seconds * 2)

            if len(productos_vistos) >= max_productos:
                break

        next_page_token = data.get("meta", {}).get("next_page")
        print(f"Siguiente página: {next_page_token}")
        time.sleep(pause_seconds)

    if productos_detalle:
        guardar_csv()
        print(f"Guardado final: {len(productos_detalle)} productos nuevos")
    guardar_categorias()

    print(f"Productos Scrapeados con Éxito: {len(productos_vistos)}")

if __name__ == "__main__":
    import threading
    stop_event = threading.Event()
    main(stop_event)
