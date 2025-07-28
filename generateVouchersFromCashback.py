import json
import requests
import os
import uuid
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações das APIs
API_BASE_URL = "https://api.dooca.store"
API_KEY = os.getenv("API_KEY")
SHOPIFY_SHOP_DOMAIN = os.getenv("SHOPIFY_SHOP_DOMAIN")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Verifica se as variáveis foram carregadas
if not API_KEY:
    raise ValueError("❌ API_KEY não encontrada no arquivo .env")

if not SHOPIFY_SHOP_DOMAIN or not SHOPIFY_ACCESS_TOKEN:
    print("⚠️  Variáveis do Shopify não encontradas. Executando apenas em modo de teste.")
    print("Configure SHOPIFY_SHOP_DOMAIN e SHOPIFY_ACCESS_TOKEN para criar cupons no Shopify.")
    SHOPIFY_ENABLED = False
else:
    SHOPIFY_ENABLED = True

def load_cashback_balances():
    """Carrega os saldos de cashback do arquivo JSON"""
    try:
        with open("imported/cashback_saldos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"📂 Arquivo carregado com {len(data)} registros")
        return data
    except FileNotFoundError:
        print("❌ Arquivo cashback_saldos.json não encontrado na pasta imported/")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {str(e)}")
        return []

def filter_positive_balances(balances, limit=10):
    """Filtra apenas saldos positivos e limita a quantidade"""
    positive_balances = []
    
    for balance in balances:
        # Verifica se tem customer_id e balance positivo
        if (balance.get("customer_id") and 
            balance.get("balance") and 
            float(balance.get("balance", 0)) > 0):
            positive_balances.append(balance)
            
            # Para quando atingir o limite
            if len(positive_balances) >= limit:
                break
    
    print(f"🔍 Encontrados {len(positive_balances)} saldos positivos (limitado a {limit})")
    return positive_balances

def get_customer_email(customer_id):
    """Busca o email do cliente via API da Bagy"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"{API_BASE_URL}/customers/{customer_id}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            customer_data = response.json()
            email = customer_data.get("email", "")
            name = customer_data.get("name", "Nome não disponível")
            return email, name
        else:
            print(f"⚠️  Erro ao buscar cliente {customer_id}: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Erro na requisição para cliente {customer_id}: {str(e)}")
        return None, None

def generate_voucher_code(customer_name, customer_id):
    """Gera um código único de voucher baseado no nome do cliente"""
    # Remove espaços e caracteres especiais do nome
    clean_name = ''.join(c.upper() for c in customer_name if c.isalnum())[:8]
    
    # Adiciona parte do customer_id para garantir unicidade
    customer_suffix = str(customer_id)[-4:]
    
    # Gera código no formato: CASHBACK-NOME-ID
    voucher_code = f"CASHBACK-{clean_name}-{customer_suffix}"
    
    return voucher_code

def parse_expiration_date(expiration_str):
    """Converte a data de expiração para o formato ISO do Shopify"""
    if not expiration_str or expiration_str == "Sem data de expiração":
        # Se não há data de expiração, define para 1 ano a partir de hoje
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=365)
        return future_date.strftime("%Y-%m-%dT23:59:59Z")
    
    try:
        # Tenta converter a data da Bagy para formato ISO
        # Formato esperado: "2025-08-15 08:14:22"
        dt = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT23:59:59Z")
    except:
        # Se falhar, usa 1 ano a partir de hoje
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=365)
        return future_date.strftime("%Y-%m-%dT23:59:59Z")

def find_shopify_customer_by_email(email):
    """Busca um cliente no Shopify pelo email"""
    if not SHOPIFY_ENABLED:
        return None
    
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Busca cliente pelo email
    url = f"https://{SHOPIFY_SHOP_DOMAIN}/admin/api/2024-07/customers/search.json"
    params = {
        "query": f"email:{email}",
        "limit": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            customers = response.json().get("customers", [])
            if customers:
                customer = customers[0]
                print(f"   👤 Cliente encontrado no Shopify: ID {customer['id']}")
                return customer["id"]
            else:
                print(f"   ⚠️  Cliente não encontrado no Shopify: {email}")
                return None
        else:
            print(f"   ❌ Erro ao buscar cliente no Shopify: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro na busca do cliente no Shopify: {str(e)}")
        return None

def create_shopify_price_rule(voucher_info):
    """Cria uma price rule no Shopify para o voucher de cashback"""
    if not SHOPIFY_ENABLED:
        return None
    
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    url = f"https://{SHOPIFY_SHOP_DOMAIN}/admin/api/2024-07/price_rules.json"
    
    # Converte valor para o formato correto do Shopify
    # Para Real (BRL): Shopify espera o valor em centavos como string
    # Ex: R$ 10.63 = "10.63" (não "1063")
    value_formatted = f"{voucher_info['balance']:.2f}"
    
    # Busca o cliente no Shopify pelo email
    shopify_customer_id = voucher_info.get('shopify_customer_id')
    
    # Configuração da Price Rule baseada na existência do cliente
    if shopify_customer_id:
        # Cliente encontrado - cupom restrito a ele
        customer_selection = "prerequisite"
        prerequisite_customer_ids = [shopify_customer_id]
        print(f"   🔒 Cupom restrito ao cliente Shopify ID: {shopify_customer_id}")
    else:
        # Cliente não encontrado - cupom disponível para todos
        customer_selection = "all"
        prerequisite_customer_ids = []
        print(f"   🌍 Cupom disponível para qualquer cliente (cliente não encontrado no Shopify)")
    
    price_rule_data = {
        "price_rule": {
            "title": f"Cashback {voucher_info['customer_name']} - R$ {voucher_info['balance']:.2f}",
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "value_type": "fixed_amount",
            "value": f"-{value_formatted}",  # Valor negativo em formato decimal
            "customer_selection": customer_selection,
            "starts_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ends_at": voucher_info["expiration_date"],
            "once_per_customer": True,
            "usage_limit": 1,
            "prerequisite_subtotal_range": {
                "greater_than_or_equal_to": value_formatted  # Pedido mínimo = valor do cashback
            }
        }
    }
    
    # Adiciona IDs dos clientes apenas se houver
    if prerequisite_customer_ids:
        price_rule_data["price_rule"]["prerequisite_customer_ids"] = prerequisite_customer_ids
    
    try:
        response = requests.post(url, headers=headers, json=price_rule_data)
        
        if response.status_code == 201:
            price_rule = response.json()["price_rule"]
            print(f"   ✅ Price Rule criada: ID {price_rule['id']}")
            return price_rule
        elif response.status_code == 403:
            error_response = response.json()
            if "write_price_rules scope" in str(error_response):
                print(f"   🔒 Erro de permissão: Token precisa de aprovação para criar price rules")
                return "permission_error"
            else:
                print(f"   ❌ Erro de autorização: {response.status_code}")
                print(f"      Resposta: {response.text}")
                return None
        else:
            print(f"   ❌ Erro ao criar Price Rule: {response.status_code}")
            print(f"      Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro na criação da Price Rule: {str(e)}")
        return None

def create_shopify_discount_code(price_rule_id, voucher_code):
    """Cria um código de desconto no Shopify associado à price rule"""
    if not SHOPIFY_ENABLED:
        return None
    
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    url = f"https://{SHOPIFY_SHOP_DOMAIN}/admin/api/2024-07/price_rules/{price_rule_id}/discount_codes.json"
    
    discount_code_data = {
        "discount_code": {
            "code": voucher_code
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=discount_code_data)
        
        if response.status_code == 201:
            discount_code = response.json()["discount_code"]
            print(f"   ✅ Código de desconto criado: {voucher_code}")
            return discount_code
        else:
            print(f"   ❌ Erro ao criar código de desconto: {response.status_code}")
            print(f"      Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro na criação do código de desconto: {str(e)}")
        return None

def create_shopify_voucher(voucher_info):
    """Cria um voucher completo no Shopify (Price Rule + Discount Code)"""
    if not SHOPIFY_ENABLED:
        print(f"   🧪 MODO TESTE - Voucher seria criado: {voucher_info['voucher_code']}")
        return {
            "price_rule_id": "TEST_MODE",
            "discount_code": voucher_info['voucher_code'],
            "status": "test_mode"
        }
    
    # Passo 1: Criar Price Rule
    print(f"   🔄 Criando Price Rule...")
    price_rule = create_shopify_price_rule(voucher_info)
    
    if not price_rule:
        return None
    
    # Passo 2: Criar Discount Code
    print(f"   🔄 Criando Código de Desconto...")
    discount_code = create_shopify_discount_code(price_rule["id"], voucher_info["voucher_code"])
    
    if not discount_code:
        return None
    
    return {
        "price_rule_id": price_rule["id"],
        "discount_code": discount_code["code"],
        "status": "created"
    }

def filter_positive_balances(balances, limit=10):
    """Filtra apenas os saldos positivos e aplica limite para teste"""
    positive_balances = [balance for balance in balances if balance.get("balance", 0) > 0]
    
    if limit and limit > 0:
        return positive_balances[:limit]
    
    return positive_balances

def process_cashback_vouchers(balances):
    """Processa os saldos de cashback e cria vouchers no Shopify"""
    print("\n🎟️ PROCESSANDO VOUCHERS DE CASHBACK")
    print("=" * 60)
    
    if SHOPIFY_ENABLED:
        print("🔗 Integração com Shopify: ATIVADA")
        print("🏪 Loja Shopify:", SHOPIFY_SHOP_DOMAIN)
    else:
        print("🧪 MODO TESTE - Shopify não configurado")
    
    vouchers_created = []
    total_value = 0
    
    for i, balance in enumerate(balances, 1):
        customer_id = balance.get("customer_id")
        balance_amount = float(balance.get("balance", 0))
        next_expiration = balance.get("next_expiration", "Sem data de expiração")
        
        print(f"\n📋 Processando {i}/{len(balances)} - Cliente ID: {customer_id}")
        print(f"   💰 Saldo: R$ {balance_amount:.2f}")
        
        # Busca dados do cliente
        email, name = get_customer_email(customer_id)
        
        if not email or not name:
            print(f"   ❌ Não foi possível obter dados do cliente {customer_id}")
            continue
        
        print(f"   👤 Cliente: {name} ({email})")
        
        # Busca o cliente no Shopify pelo email
        print(f"   🔍 Buscando cliente no Shopify...")
        shopify_customer_id = find_shopify_customer_by_email(email)
        
        # Gera código do voucher
        voucher_code = generate_voucher_code(name, customer_id)
        
        # Converte data de expiração
        expiration_date = parse_expiration_date(next_expiration)
        
        # Prepara informações do voucher
        voucher_info = {
            "customer_id": customer_id,
            "customer_name": name,
            "customer_email": email,
            "shopify_customer_id": shopify_customer_id,  # Novo campo
            "balance": balance_amount,
            "expiration": next_expiration,
            "expiration_date": expiration_date,
            "voucher_code": voucher_code
        }
        
        print(f"   🎫 Código do voucher: {voucher_code}")
        print(f"   � Expira em: {expiration_date}")
        
        # Cria voucher no Shopify
        shopify_result = create_shopify_voucher(voucher_info)
        
        if shopify_result:
            voucher_info.update(shopify_result)
            vouchers_created.append(voucher_info)
            total_value += balance_amount
            print(f"   ✅ Voucher processado com sucesso!")
        else:
            print(f"   ❌ Falha ao processar voucher")
        
        # Pequena pausa para não sobrecarregar as APIs
        import time
        time.sleep(0.5)
    
    return vouchers_created, total_value

def generate_summary_report(vouchers, total_value):
    """Gera um relatório resumido dos vouchers"""
    if not vouchers:
        print("\n❌ Nenhum voucher foi processado com sucesso")
        return
    
    total_vouchers = len(vouchers)
    avg_value = total_value / total_vouchers if total_vouchers > 0 else 0
    
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL - VOUCHERS PROCESSADOS")
    print("=" * 70)
    print(f"🎟️  Total de vouchers: {total_vouchers}")
    print(f"💰 Valor total: R$ {total_value:.2f}")
    print(f"📊 Valor médio: R$ {avg_value:.2f}")
    
    if SHOPIFY_ENABLED:
        created_count = len([v for v in vouchers if v.get("status") == "created"])
        restricted_count = len([v for v in vouchers if v.get("shopify_customer_id")])
        general_count = len(vouchers) - restricted_count
        
        print(f"✅ Criados no Shopify: {created_count}")
        print(f"🔒 Restritos ao cliente: {restricted_count}")
        print(f"🌍 Uso geral: {general_count}")
        print(f"🏪 Loja: {SHOPIFY_SHOP_DOMAIN}")
    else:
        print(f"🧪 Modo teste: Vouchers não criados no Shopify")
    
    print("\n📋 LISTA DETALHADA:")
    print("-" * 70)
    for i, voucher in enumerate(vouchers, 1):
        status_icon = "✅" if voucher.get("status") == "created" else "🧪"
        restriction_icon = "🔒" if voucher.get("shopify_customer_id") else "🌍"
        restriction_text = "Restrito ao cliente" if voucher.get("shopify_customer_id") else "Uso geral"
        
        print(f"{i:2d}. {status_icon} {voucher['voucher_code']} {restriction_icon}")
        print(f"    👤 {voucher['customer_name'][:35]:<35} | 📧 {voucher['customer_email']}")
        print(f"    💰 R$ {voucher['balance']:>7.2f} | 📅 {voucher.get('expiration', 'N/A')}")
        print(f"    🎯 {restriction_text}")
        if voucher.get("price_rule_id"):
            print(f"    🆔 Price Rule ID: {voucher['price_rule_id']}")
        if voucher.get("shopify_customer_id"):
            print(f"    👥 Shopify Customer ID: {voucher['shopify_customer_id']}")
        print()

def export_vouchers_to_excel(vouchers):
    """Exporta a lista de vouchers para um arquivo Excel"""
    if not vouchers:
        print("⚠️  Nenhum voucher para exportar")
        return None
    
    # Prepara os dados para o Excel
    excel_data = []
    for voucher in vouchers:
        # Formata a data de expiração de forma mais legível
        expiration_formatted = voucher.get('expiration', 'Sem data')
        if expiration_formatted and expiration_formatted != 'Sem data de expiração':
            try:
                # Converte de "2025-08-15 08:14:22" para "15/08/2025"
                dt = datetime.strptime(expiration_formatted, "%Y-%m-%d %H:%M:%S")
                expiration_formatted = dt.strftime("%d/%m/%Y")
            except:
                pass
        
        row = {
            'Código do Voucher': voucher['voucher_code'],
            'Email do Cliente': voucher['customer_email'],
            'Nome do Cliente': voucher['customer_name'],
            'Valor (R$)': voucher['balance'],
            'Validade': expiration_formatted,
            'Status': 'Criado no Shopify' if voucher.get('status') == 'created' else 'Teste',
            'Restrição': 'Restrito ao cliente' if voucher.get('shopify_customer_id') else 'Uso geral',
            'Price Rule ID': voucher.get('price_rule_id', ''),
            'Shopify Customer ID': voucher.get('shopify_customer_id', ''),
            'Data de Criação': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        excel_data.append(row)
    
    # Cria o DataFrame
    df = pd.DataFrame(excel_data)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"converted/vouchers_shopify_{timestamp}.xlsx"
    
    # Garante que o diretório existe
    os.makedirs("converted", exist_ok=True)
    
    try:
        # Exporta para Excel com formatação
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Vouchers', index=False)
            
            # Obtém a planilha para formatação
            worksheet = writer.sheets['Vouchers']
            
            # Ajusta largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"\n📊 ARQUIVO EXCEL EXPORTADO")
        print(f"📁 Arquivo: {filename}")
        print(f"📈 {len(vouchers)} vouchers exportados")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {str(e)}")
        return None

def main():
    """Função principal - Criação de vouchers Shopify"""
    print("🎟️ GERADOR DE VOUCHERS SHOPIFY")
    print("=" * 60)
    print("📋 Objetivo: Converter saldos de cashback em vouchers Shopify")
    
    if SHOPIFY_ENABLED:
        print("� Integração com Shopify: ATIVADA")
        print("🏪 Loja:", SHOPIFY_SHOP_DOMAIN)
    else:
        print("🧪 MODO TESTE: Vouchers serão simulados")
    
    print()
    
    try:
        # 1. Carrega os saldos de cashback
        print("📥 Carregando saldos de cashback...")
        all_balances = load_cashback_balances()
        
        if not all_balances:
            print("❌ Nenhum dado de cashback encontrado")
            return
        
        # 2. Filtra apenas saldos positivos (10 primeiros para teste)
        print("🔍 Filtrando saldos positivos...")
        positive_balances = filter_positive_balances(all_balances, limit=10)
        
        if not positive_balances:
            print("❌ Nenhum saldo positivo encontrado")
            return
        
        print(f"✅ Encontrados {len(positive_balances)} saldos positivos para processar")
        
        # 3. Processa os vouchers e cria no Shopify
        vouchers, total_value = process_cashback_vouchers(positive_balances)
        
        # Verifica se houve erro de permissão
        permission_error_detected = False
        if SHOPIFY_ENABLED and not vouchers:
            # Testa se é problema de permissão
            print("\n🔍 Verificando se é problema de permissão...")
            test_voucher = {
                "customer_name": "Teste",
                "balance": 1.0,
                "expiration_date": datetime.now().strftime("%Y-%m-%dT23:59:59Z")
            }
            result = create_shopify_price_rule(test_voucher)
            if result == "permission_error":
                permission_error_detected = True
        
        # 4. Gera relatório final
        generate_summary_report(vouchers, total_value)
        
        # 5. Exporta para Excel
        if vouchers:
            excel_file = export_vouchers_to_excel(vouchers)
            if excel_file:
                print(f"📄 Lista de vouchers salva em: {excel_file}")
        
        if permission_error_detected:
            print("\n" + "!" * 70)
            print("🔒 PROBLEMA DE PERMISSÃO DETECTADO")
            print("!" * 70)
            print("❌ O token de acesso do Shopify precisa de aprovação para criar Price Rules")
            print()
            print("📋 COMO RESOLVER:")
            print("1. Acesse o admin do Shopify")
            print("2. Vá em Apps > Apps privadas")
            print("3. Edite o app que está sendo usado")
            print("4. Solicite aprovação para o escopo 'write_price_rules'")
            print("5. Aguarde aprovação do proprietário da loja")
            print()
            print("🔗 Ou crie um novo app privado com as permissões corretas:")
            print("   - read_customers (para buscar dados dos clientes)")
            print("   - write_price_rules (para criar regras de desconto)")
            print("   - write_discounts (para criar códigos de desconto)")
            print()
        elif SHOPIFY_ENABLED and vouchers:
            print("\n🎉 Vouchers criados com sucesso no Shopify!")
            print("� Os clientes podem usar os códigos no checkout da loja")
        elif vouchers:
            print("\n✅ Processamento concluído em modo teste!")
            print("🔄 Configure as credenciais do Shopify para criar os vouchers reais")
        else:
            print("\n⚠️  Nenhum voucher foi processado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro durante o processamento: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
