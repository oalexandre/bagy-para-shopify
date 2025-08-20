import requests
import openpyxl
import json
import os
import pandas as pd
from time import sleep
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

API_BASE_URL = "https://api.dooca.store"
API_KEY = os.getenv("API_KEY")

# Verifica se a API_KEY foi carregada
if not API_KEY:
    raise ValueError("❌ API_KEY não encontrada no arquivo .env")

def get_cashback_balances():
    """Busca todos os saldos de cashback dos clientes"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    balances = []
    page = 1
    total_pages = None

    print("🔍 Buscando saldos de cashback dos clientes...")

    while True:
        url = f"{API_BASE_URL}/cashbacks/customers/balances"
        params = {
            "page": page, 
            "limit": 100,
            "sort": "-id"
        }
        
        print(f"➡️  Processando página {page}{'/' + str(total_pages) if total_pages else ''}...")
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erro na página {page}: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
            # Se for erro de parâmetros, tenta sem ordenação
            if response.status_code == 500 and "startsWith" in response.text:
                print("🔄 Tentando sem parâmetros de ordenação...")
                params_simple = {"page": page, "limit": 100}
                response = requests.get(url, headers=headers, params=params_simple)
                
                if response.status_code != 200:
                    print(f"❌ Erro mesmo sem ordenação: {response.status_code}")
                    break
            else:
                break

        data = response.json()
        
        # Primeira vez, descobre o total de páginas
        if total_pages is None:
            meta = data.get("meta", {})
            total_pages = meta.get("last_page", 1)
            total_records = meta.get("total", 0)
            print(f"🔎 Total de páginas: {total_pages}")
            print(f"💰 Total de clientes com cashback: {total_records}")

        # Adiciona os dados da página atual
        page_balances = data.get("data", [])
        balances.extend(page_balances)
        
        print(f"   📄 Registros nesta página: {len(page_balances)}")

        # Verifica se tem próxima página
        if page >= total_pages:
            break

        page += 1
        sleep(0.5)  # Pausa para evitar rate limiting

    print(f"✅ Total de saldos coletados: {len(balances)}")
    return balances

def export_balances_to_excel(balances, filename="cashback_saldos.xlsx"):
    """Exporta os saldos de cashback para Excel"""
    if not balances:
        print("❌ Nenhum saldo encontrado para exportar")
        return

    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Saldos Cashback"

    # Cabeçalhos
    headers = [
        "Customer ID",
        "Saldo (R$)",
        "Próxima Expiração",
        "Próxima Liberação"
    ]
    ws.append(headers)

    # Dados dos saldos
    for balance in balances:
        row = [
            balance.get("customer_id", ""),
            balance.get("balance", 0),
            balance.get("next_expiration", ""),
            balance.get("next_release", "")
        ]
        ws.append(row)

    # Formatação básica
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    wb.save(filepath)
    print(f"✅ Saldos exportados para: {filepath}")
    return filepath

def export_balances_to_json(balances, filename="cashback_saldos.json"):
    """Exporta saldos para JSON"""
    if not balances:
        print("⚠️  Nenhum saldo para exportar.")
        return

    # Cria a pasta imported se não existir
    imported_dir = "imported"
    os.makedirs(imported_dir, exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join(imported_dir, filename)

    print(f"💾 Exportando {len(balances)} saldos para {filepath}...")

    # Salva como JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(balances, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Arquivo {filepath} criado com sucesso!")
    return filepath

def generate_balances_summary_report(balances):
    """Gera um relatório resumido apenas dos saldos de cashback"""
    total_customers = len(balances)
    
    # Calcula totais dos saldos
    total_balance = sum(balance.get("balance", 0) for balance in balances)
    customers_with_balance = len([b for b in balances if b.get("balance", 0) > 0])
    customers_zero_balance = total_customers - customers_with_balance
    
    # Estatísticas dos saldos
    if customers_with_balance > 0:
        balances_values = [b.get("balance", 0) for b in balances if b.get("balance", 0) > 0]
        avg_balance = sum(balances_values) / len(balances_values)
        max_balance = max(balances_values)
        min_balance = min(balances_values)
    else:
        avg_balance = max_balance = min_balance = 0
    
    # Cria o relatório
    report_lines = [
        "💰 RELATÓRIO DE SALDOS CASHBACK",
        "=" * 50,
        "",
        "📊 RESUMO GERAL:",
        f"   👥 Total de clientes: {total_customers}",
        f"   💵 Clientes com saldo: {customers_with_balance}",
        f"   ⭕ Clientes com saldo zero: {customers_zero_balance}",
        f"   💰 Saldo total: R$ {total_balance:.2f}",
        "",
        "📈 ESTATÍSTICAS DOS SALDOS:",
        f"   📊 Saldo médio: R$ {avg_balance:.2f}",
        f"   🔝 Maior saldo: R$ {max_balance:.2f}",
        f"   🔻 Menor saldo: R$ {min_balance:.2f}",
        "",
        "📁 ARQUIVOS GERADOS:",
        "   - imported/cashback_saldos.xlsx",
        "   - imported/cashback_saldos.json"
    ]
    
    # Salva o relatório
    summary_file = "imported/cashback_saldos_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    # Exibe o relatório
    print("\n" + "\n".join(report_lines))
    print(f"\n📝 Resumo salvo em: {summary_file}")

def main():
    """Função principal"""
    print("💰 EXPORTADOR DE SALDOS CASHBACK BAGY")
    print("=" * 50)
    
    try:
        # Busca apenas saldos de cashback
        print("\n💰 Exportando saldos de cashback...")
        balances = get_cashback_balances()
        
        if not balances:
            print("❌ Nenhum saldo de cashback encontrado")
            return
        
        print("\n💾 Salvando arquivos...")
        
        # Exporta para Excel e JSON
        export_balances_to_excel(balances)
        export_balances_to_json(balances)
        
        # Gera relatório resumido apenas dos saldos
        print("\n📊 Gerando relatório...")
        generate_balances_summary_report(balances)
        
        print("\n🎉 Exportação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a exportação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    # Mostra ajuda se solicitado
    if "--help" in sys.argv or "-h" in sys.argv:
        print("💰 EXPORTADOR DE SALDOS CASHBACK BAGY")
        print("=" * 50)
        print("Uso:")
        print("  python3 importCashbackFromBagy.py           # Execução completa")
        print("  python3 importCashbackFromBagy.py --help    # Mostra esta ajuda")
        print()
        print("O script busca saldos de cashback dos clientes via API da Bagy.")
        print()
        print("Arquivos gerados:")
        print("  - imported/cashback_saldos.xlsx")
        print("  - imported/cashback_saldos.json")
        print("  - imported/cashback_saldos_summary.txt")
    else:
        main()
