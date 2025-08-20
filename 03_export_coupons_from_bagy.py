import requests
import openpyxl
from time import sleep
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

API_URL = "https://api.dooca.store/discounts"
API_KEY = os.getenv("API_KEY")

def get_all_discounts():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    discounts = []
    page = 1
    total_pages = None

    while True:
        response = requests.get(API_URL, headers=headers, params={"page": page})
        if response.status_code != 200:
            print(f"❌ Erro na requisição da página {page}: {response.status_code}")
            break

        data = response.json()
        if total_pages is None:
            total_pages = data.get("meta", {}).get("last_page", 1)
            print(f"🔎 Total de páginas: {total_pages}")
            print(f"🎟️ Total de cupons: {data.get('meta', {}).get('total', '?')}")

        print(f"➡️  Processando página {page} de {total_pages}...")

        discounts.extend(data.get("data", []))

        if not data.get("links", {}).get("next"):
            break

        page += 1
        sleep(0.350)

    return discounts

def export_discounts_to_excel(discounts, filename="cupons_dooca.xlsx"):
    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cupons"

    headers = [
        "id", "name", "codes", "date_from", "date_to", "single_usage", "usage_limit",
        "min_purchase", "max_purchase", "min_quantity", "max_quantity", "type",
        "value_type", "value", "coupon_allow_free_freight", "is_free_freight",
        "created_at", "updated_at", "prerequisite_customer_id",
        "prerequisite_customer_group_id", "prerequisite_quantity",
        "prerequisite_category_ids", "prerequisite_product_ids",
        "entitled_quantity", "entitled_category_ids", "entitled_product_ids",
        "fixed_freight_options", "zipcodes", "active"
    ]
    ws.append(headers)

    for d in discounts:
        row = [
            d.get("id"),
            d.get("name"),
            d.get("code"),  # mapeado como "codes"
            d.get("date_from"),
            d.get("date_to"),
            d.get("single_usage"),
            d.get("usage_limit"),
            d.get("min_purchase"),
            d.get("max_purchase"),
            d.get("min_quantity"),
            d.get("max_quantity"),
            d.get("type"),
            d.get("value_type"),
            d.get("value"),
            d.get("coupon_allow_free_freight"),
            d.get("is_free_freight"),
            d.get("created_at"),
            d.get("updated_at"),
            d.get("prerequisite_customer_id"),
            d.get("prerequisite_customer_group_id"),
            d.get("prerequisite_quantity"),
            ", ".join(map(str, d.get("prerequisite_category_ids", []))),
            ", ".join(map(str, d.get("prerequisite_product_ids", []))),
            d.get("entitled_quantity"),
            ", ".join(map(str, d.get("entitled_category_ids", []))),
            ", ".join(map(str, d.get("entitled_product_ids", []))),
            ", ".join(map(str, d.get("fixed_freight_options", []))),
            ", ".join(map(str, d.get("zipcodes", []))),
            d.get("active")
        ]
        ws.append(row)

    wb.save(filepath)
    print(f"✅ Arquivo salvo como {filepath}")

# Execução completa
cupons = get_all_discounts()
export_discounts_to_excel(cupons)
