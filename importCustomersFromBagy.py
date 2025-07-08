import requests
import openpyxl
from time import sleep
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

API_URL = "https://api.dooca.store/customers"
API_KEY = os.getenv("API_KEY")

def get_all_customers():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    customers = []
    page = 1
    total_pages = None
    total_customers = None

    while True:
        response = requests.get(API_URL, headers=headers, params={"page": page})
        if response.status_code != 200:
            print(f"❌ Erro na requisição da página {page}: {response.status_code}")
            break

        data = response.json()
        if total_pages is None:
            total_pages = data.get("meta", {}).get("last_page", 1)
            total_customers = data.get("meta", {}).get("total", "?")
            print(f"🔎 Total de páginas: {total_pages}")
            print(f"👥 Total de clientes esperados: {total_customers}")

        print(f"➡️  Processando página {page} de {total_pages}...")

        new_customers = data.get("data", [])
        customers.extend(new_customers)

        print(f"📥 Baixados {len(customers)} de {total_customers} clientes até agora\n")
        if not data.get("links", {}).get("next"):
            break

        page += 1
        # sleep(0.350)

    return customers

def export_to_excel(customers, filename="clientes_dooca.xlsx"):
    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clientes"

    headers = [
        "ID", "Nome", "Email", "CPF/CNPJ", "Telefone", "Data de Nascimento", "Sexo",
        "Cidade", "Estado", "CEP", "Rua", "Número", "Complemento", "Bairro"
    ]
    ws.append(headers)

    for c in customers:
        addr = c.get("address") or {}
        row = [
            c.get("id"),
            c.get("name"),
            c.get("email"),
            c.get("cgc"),
            c.get("phone"),
            c.get("birthday"),
            c.get("gender"),
            addr.get("city"),
            addr.get("state"),
            addr.get("zipcode"),
            addr.get("street"),
            addr.get("number"),
            addr.get("detail"),
            addr.get("district"),
        ]
        ws.append(row)

    wb.save(filepath)
    print(f"✅ Arquivo salvo como {filepath}")

# Execução completa sem limite de páginas
clientes = get_all_customers()
export_to_excel(clientes)
