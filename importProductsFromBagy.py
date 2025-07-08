import requests
import openpyxl
import json
import os
from time import sleep
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

API_URL = "https://api.dooca.store/products"
API_KEY = os.getenv("API_KEY")

# Verifica se a API_KEY foi carregada
if not API_KEY:
    raise ValueError("❌ API_KEY não encontrada no arquivo .env")

def get_all_products():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    products = []
    page = 1
    total_pages = None

    while True:
        response = requests.get(API_URL, headers=headers, params={"page": page})
        if response.status_code != 200:
            print(f"❌ Erro na página {page}: {response.status_code}")
            break

        data = response.json()
        if total_pages is None:
            total_pages = data.get("meta", {}).get("last_page", 1)
            print(f"🔎 Total de páginas: {total_pages}")
            print(f"📦 Total de produtos: {data.get('meta', {}).get('total', '?')}")

        print(f"➡️  Processando página {page} de {total_pages}...")
        products.extend(data.get("data", []))

        if not data.get("links", {}).get("next"):
            break

        page += 1
        sleep(0.350)

    return products

def export_products_to_excel(products, filename="produtos_dooca.xlsx"):
    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Produtos"

    # Pegamos os campos da primeira entrada para gerar os cabeçalhos
    first_product = products[0]
    headers = list(first_product.keys())
    ws.append(headers)

    for p in products:
        row = [json.dumps(p.get(h)) if isinstance(p.get(h), (dict, list)) else p.get(h) for h in headers]
        ws.append(row)

    wb.save(filepath)
    print(f"✅ Arquivo Excel salvo como {filepath}")

def export_products_to_json(products, filename="produtos.json"):
    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ Arquivo JSON salvo como {filepath}")

# Execução completa
produtos = get_all_products()
export_products_to_excel(produtos)
export_products_to_json(produtos)
