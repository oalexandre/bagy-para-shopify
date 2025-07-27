import json
import pandas as pd
import os
from urllib.parse import urlparse

def load_bagy_products():
    """Carrega os produtos da Bagy do arquivo JSON"""
    try:
        with open("imported/produtos.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        print(f"✅ Carregados {len(products)} produtos da Bagy")
        return products
    except FileNotFoundError:
        print("❌ Arquivo produtos.json não encontrado na pasta imported/")
        return []

def load_shopify_products():
    """Carrega os produtos do Shopify do arquivo CSV exportado"""
    try:
        df = pd.read_csv("imported/products_export_1.csv")
        print(f"✅ Carregados {len(df)} produtos do Shopify")
        return df
    except FileNotFoundError:
        print("❌ Arquivo products_export_1.csv não encontrado na pasta imported/")
        return pd.DataFrame()

def extract_path_from_url(url, base_url="https://www.asmanhas.com.br"):
    """Extrai o path da URL da Bagy para usar no redirect"""
    if url.startswith(base_url):
        return url.replace(base_url, "")
    else:
        # Se não começar com a base, extrai apenas o path
        parsed = urlparse(url)
        return parsed.path
    return url

def create_sku_to_handle_mapping(shopify_df):
    """Cria um mapeamento SKU -> Handle do Shopify"""
    mapping = {}
    
    if shopify_df.empty:
        return mapping
    
    # Remove linhas sem SKU ou Handle
    valid_rows = shopify_df[
        shopify_df['Variant SKU'].notna() & 
        shopify_df['Handle'].notna() &
        (shopify_df['Variant SKU'] != '') &
        (shopify_df['Handle'] != '')
    ]
    
    for _, row in valid_rows.iterrows():
        sku = str(row['Variant SKU']).strip()
        handle = str(row['Handle']).strip()
        
        if sku and handle:
            mapping[sku] = handle
    
    print(f"🔗 Criado mapeamento SKU -> Handle para {len(mapping)} SKUs")
    return mapping

def process_bagy_products(bagy_products, sku_to_handle):
    """Processa produtos da Bagy e cria lista de redirects"""
    redirects = []
    processed_urls = set()  # Para evitar duplicatas
    
    for product in bagy_products:
        product_url = product.get("url", "")
        variations = product.get("variations", [])
        
        if not product_url:
            continue
            
        # Extrai o path da URL principal do produto
        product_path = extract_path_from_url(product_url)
        
        # Se o produto tem variações, processa cada uma
        if variations:
            for variation in variations:
                sku = variation.get("sku", "")
                variation_url = variation.get("url", "")
                
                if sku and sku in sku_to_handle:
                    handle = sku_to_handle[sku]
                    redirect_to = f"/products/{handle}"
                    
                    # Processa URL da variação se existir
                    if variation_url and variation_url not in processed_urls:
                        variation_path = extract_path_from_url(variation_url)
                        redirects.append({
                            "redirect_from": variation_path,
                            "redirect_to": redirect_to,
                            "sku": sku,
                            "product_name": product.get("name", ""),
                            "source": "variation_url"
                        })
                        processed_urls.add(variation_url)
                    
                    # Processa URL principal do produto se ainda não foi processada
                    elif product_url not in processed_urls:
                        redirects.append({
                            "redirect_from": product_path,
                            "redirect_to": redirect_to,
                            "sku": sku,
                            "product_name": product.get("name", ""),
                            "source": "product_url"
                        })
                        processed_urls.add(product_url)
                        break  # Só adiciona a URL principal uma vez por produto
        
        # Se não tem variações, tenta usar algum SKU do produto (se houver)
        else:
            # Tenta encontrar SKU em outros campos do produto
            product_sku = product.get("sku") or product.get("reference")
            if product_sku and product_sku in sku_to_handle and product_url not in processed_urls:
                handle = sku_to_handle[product_sku]
                redirect_to = f"/products/{handle}"
                
                redirects.append({
                    "redirect_from": product_path,
                    "redirect_to": redirect_to,
                    "sku": product_sku,
                    "product_name": product.get("name", ""),
                    "source": "product_direct"
                })
                processed_urls.add(product_url)
    
    return redirects

def save_redirects_csv(redirects, filename="redirects_301.csv"):
    """Salva os redirects no formato CSV para importação"""
    if not redirects:
        print("❌ Nenhum redirect encontrado para salvar")
        return
    
    # Cria a pasta converted se não existir
    os.makedirs("converted", exist_ok=True)
    
    # Caminho completo do arquivo
    filepath = os.path.join("converted", filename)
    
    # Cria DataFrame com as colunas necessárias
    df_redirects = pd.DataFrame(redirects)
    
    # Cria CSV no formato do modelo (Redirect from, Redirect to)
    csv_data = pd.DataFrame({
        "Redirect from": df_redirects["redirect_from"],
        "Redirect to": df_redirects["redirect_to"]
    })
    
    # Remove duplicatas baseado no "Redirect from"
    csv_data = csv_data.drop_duplicates(subset=["Redirect from"], keep="first")
    
    # Salva o CSV
    csv_data.to_csv(filepath, index=False, encoding="utf-8")
    
    print(f"✅ Arquivo CSV salvo como {filepath}")
    print(f"📊 Total de redirects: {len(csv_data)}")
    
    # Salva também um relatório detalhado
    detailed_filepath = os.path.join("converted", "redirects_detailed_report.csv")
    df_redirects_detailed = pd.DataFrame(redirects)
    df_redirects_detailed.to_csv(detailed_filepath, index=False, encoding="utf-8")
    print(f"📄 Relatório detalhado salvo em: {detailed_filepath}")
    
    return filepath

def generate_summary_report(redirects, sku_to_handle, bagy_products):
    """Gera um relatório resumido dos resultados"""
    total_bagy_products = len(bagy_products)
    total_shopify_skus = len(sku_to_handle)
    total_redirects = len(redirects)
    
    # Conta por tipo de fonte
    sources_count = {}
    for redirect in redirects:
        source = redirect.get("source", "unknown")
        sources_count[source] = sources_count.get(source, 0) + 1
    
    # Cria o relatório
    report_lines = [
        "🔗 RELATÓRIO DE CRIAÇÃO DE REDIRECTS",
        "=" * 50,
        "",
        f"📦 Total de produtos da Bagy: {total_bagy_products}",
        f"🏪 Total de SKUs do Shopify: {total_shopify_skus}",
        f"✅ Total de redirects criados: {total_redirects}",
        "",
        "📊 Redirects por fonte:",
    ]
    
    for source, count in sources_count.items():
        source_name = {
            "variation_url": "URLs de variações",
            "product_url": "URLs principais de produto",
            "product_direct": "Produtos sem variações"
        }.get(source, source)
        report_lines.append(f"   - {source_name}: {count}")
    
    report_lines.extend([
        "",
        "📁 Arquivos gerados:",
        "   - converted/redirects_301.csv (para importação)",
        "   - converted/redirects_detailed_report.csv (relatório completo)",
        "",
        "🎯 Próximos passos:",
        "   1. Revisar o arquivo redirects_301.csv",
        "   2. Fazer upload no admin do Shopify",
        "   3. Verificar se os redirects foram criados corretamente"
    ])
    
    # Salva o relatório
    summary_file = "converted/redirects_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    # Exibe o relatório
    print("\n" + "\n".join(report_lines))
    print(f"\n📝 Resumo salvo em: {summary_file}")

def main():
    """Função principal"""
    print("🔗 GERADOR DE REDIRECTS 301 BAGY → SHOPIFY")
    print("=" * 50)
    
    # Carrega os dados
    print("\n📥 Carregando dados...")
    bagy_products = load_bagy_products()
    shopify_df = load_shopify_products()
    
    if not bagy_products:
        print("❌ Nenhum produto da Bagy encontrado")
        return
    
    if shopify_df.empty:
        print("❌ Nenhum produto do Shopify encontrado")
        return
    
    # Cria mapeamento SKU -> Handle
    print("\n🗺️  Criando mapeamento SKU -> Handle...")
    sku_to_handle = create_sku_to_handle_mapping(shopify_df)
    
    if not sku_to_handle:
        print("❌ Nenhum mapeamento SKU -> Handle criado")
        return
    
    # Processa produtos da Bagy
    print("\n🔄 Processando produtos da Bagy...")
    redirects = process_bagy_products(bagy_products, sku_to_handle)
    
    if not redirects:
        print("❌ Nenhum redirect foi criado. Verifique se os SKUs coincidem entre Bagy e Shopify")
        return
    
    # Salva os redirects
    print("\n💾 Salvando redirects...")
    csv_file = save_redirects_csv(redirects)
    
    # Gera relatório resumido
    print("\n📊 Gerando relatório...")
    generate_summary_report(redirects, sku_to_handle, bagy_products)
    
    print(f"\n🎉 Processo concluído! Arquivo pronto: {csv_file}")

if __name__ == "__main__":
    main()
