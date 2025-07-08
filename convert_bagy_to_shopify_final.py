#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter produtos da plataforma Bagy (formato JSON) 
para o formato CSV de importação do Shopify

Regras importantes:
1. Cor primeiro (Option1), depois Tamanho (Option2)
2. Ordenação: Cor Azul-P, Azul-M, Azul-G, depois Cor Verde-P, Verde-M, Verde-G
3. Primeira linha com dados completos do produto
4. Linhas subsequentes apenas com Handle + dados das variações
5. Imagens em linhas separadas com Handle + dados da imagem
"""

import json
import csv
import re
import os
from html import unescape

def clean_html(html_text):
    """Remove tags HTML e converte entidades HTML para texto limpo"""
    if not html_text:
        return ""
    
    try:
        # Remove estilos CSS inline
        html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove tags HTML
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_text)
        
        # Converte entidades HTML
        text = unescape(text)
        
        # Remove espaços extras e quebras de linha desnecessárias
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        print(f"Erro ao limpar HTML: {e}")
        return str(html_text) if html_text else ""

def create_handle(name):
    """Cria um handle válido para o Shopify baseado no nome do produto"""
    if not name:
        return "produto-sem-nome"
    
    try:
        handle = name.lower()
        # Remove acentos
        handle = handle.replace('ã', 'a').replace('á', 'a').replace('à', 'a').replace('â', 'a')
        handle = handle.replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o')
        handle = handle.replace('ô', 'o').replace('õ', 'o').replace('ú', 'u').replace('ç', 'c')
        
        # Remove caracteres especiais, mantém apenas letras, números, espaços e hífens
        handle = re.sub(r'[^a-z0-9\s-]', '', handle)
        # Substitui espaços por hífens
        handle = re.sub(r'\s+', '-', handle)
        # Remove hífens duplos
        handle = re.sub(r'-+', '-', handle)
        # Remove hífens no início e fim
        handle = handle.strip('-')
        
        return handle if handle else "produto-sem-nome"
    except Exception as e:
        print(f"Erro ao criar handle para '{name}': {e}")
        return "produto-erro"

def get_weight_in_grams(weight_str):
    """Converte peso para gramas (formato do Shopify)"""
    if not weight_str:
        return 0
    
    try:
        weight = float(weight_str)
        # Se o peso está em kg, converte para gramas
        return int(weight * 1000) if weight < 50 else int(weight)
    except:
        return 0

def safe_get(obj, key, default=''):
    """Obtém valor de forma segura"""
    try:
        return obj.get(key, default) if obj else default
    except:
        return default

def convert_bagy_to_shopify_csv(json_file_path, csv_file_path, max_products=None):
    """
    Converte produtos do JSON da Bagy para CSV do Shopify
    """
    
    try:
        print("Carregando arquivo JSON...")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"JSON carregado com {len(products)} produtos")
    except Exception as e:
        print(f"Erro ao ler arquivo JSON: {e}")
        return

    # Cabeçalhos do CSV do Shopify (baseado no template)
    headers = [
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags',
        'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
        'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams',
        'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy',
        'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price',
        'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src',
        'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description',
        'Google Shopping / Google Product Category', 'Google Shopping / Gender',
        'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition',
        'Google Shopping / Custom Product', 'Variant Image', 'Variant Weight Unit',
        'Variant Tax Code', 'Cost per item', 'Included / United States',
        'Price / United States', 'Compare At Price / United States',
        'Included / International', 'Price / International',
        'Compare At Price / International', 'Status'
    ]
    
    csv_rows = []
    processed_count = 0
    error_count = 0
    
    # Filtra produtos válidos
    valid_products = [p for p in products if p and p.get('name')]
    
    # Processa os produtos especificados ou todos se max_products for None
    if max_products is None:
        products_to_process = valid_products
    else:
        products_to_process = valid_products[:max_products]
    
    print(f"Processando {len(products_to_process)} produtos...")
    
    for i, product in enumerate(products_to_process):
        try:
            handle = create_handle(product['name'])
            title = safe_get(product, 'name', 'Produto sem nome')
            body_html = safe_get(product, 'description', '')
            vendor = 'Marca'
            
            # Tenta obter vendor do brand
            if product.get('brand') and product['brand'].get('name'):
                vendor = product['brand']['name']
            
            # Categoria do produto
            category = ''
            if product.get('category_default') and product['category_default'].get('name'):
                category = product['category_default']['name']
            
            # Tags - usando meta_keywords se disponível
            tags = safe_get(product, 'meta_keywords', '')
            
            # Status do produto
            status = 'active' if product.get('active', False) else 'draft'
            
            # SEO
            seo_title = safe_get(product, 'meta_title', '') or title
            seo_description = safe_get(product, 'meta_description', '') or clean_html(body_html)[:320]
            
            # Peso em gramas
            weight_grams = get_weight_in_grams(product.get('weight'))
            
            # Preço
            price = product.get('price', 0)
            compare_price = safe_get(product, 'price_compare', '')
            
            # Verifica se o produto tem variações
            variations = product.get('variations', [])
            images = product.get('images', [])
            
            if variations:
                # Produto com variações
                # ORDENAÇÃO IMPORTANTE: Cor primeiro, depois por tamanho
                def sort_variations(var):
                    try:
                        size_order = {'P': 1, 'M': 2, 'G': 3, 'GG': 4, 'XG': 5}
                        color = safe_get(var.get('color', {}), 'name', '') if var.get('color') else ''
                        size = safe_get(var.get('attribute', {}), 'name', 'P')
                        return (color, size_order.get(size, 6))
                    except:
                        return ('', 6)
                
                variations.sort(key=sort_variations)
                
                first_variation = True
                
                for variation in variations:
                    try:
                        row = [''] * len(headers)
                        
                        # Dados básicos do produto (apenas na primeira linha de variação)
                        if first_variation:
                            row[headers.index('Handle')] = handle
                            row[headers.index('Title')] = title
                            row[headers.index('Body (HTML)')] = body_html
                            row[headers.index('Vendor')] = vendor
                            row[headers.index('Type')] = category
                            row[headers.index('Tags')] = tags
                            row[headers.index('Published')] = 'TRUE' if status == 'active' else 'FALSE'
                            row[headers.index('SEO Title')] = seo_title
                            row[headers.index('SEO Description')] = seo_description[:320]
                            first_variation = False
                        else:
                            row[headers.index('Handle')] = handle
                        
                        # Opções de variação: COR PRIMEIRO (Option1), TAMANHO SEGUNDO (Option2)
                        if variation.get('color'):
                            row[headers.index('Option1 Name')] = 'Cor'
                            row[headers.index('Option1 Value')] = safe_get(variation['color'], 'name', '')
                        
                        if variation.get('attribute'):
                            row[headers.index('Option2 Name')] = safe_get(variation['attribute'], 'attribute_name', 'Tamanho')
                            row[headers.index('Option2 Value')] = safe_get(variation['attribute'], 'name', '')
                        
                        # Dados da variação
                        row[headers.index('Variant SKU')] = safe_get(variation, 'sku', '')
                        row[headers.index('Variant Grams')] = weight_grams
                        row[headers.index('Variant Inventory Tracker')] = 'shopify'
                        row[headers.index('Variant Inventory Qty')] = variation.get('balance', 0)
                        row[headers.index('Variant Inventory Policy')] = 'deny'
                        row[headers.index('Variant Fulfillment Service')] = 'manual'
                        row[headers.index('Variant Price')] = variation.get('price', price)
                        
                        if variation.get('price_compare'):
                            row[headers.index('Variant Compare At Price')] = variation['price_compare']
                        
                        # Adiciona imagem específica da variação se existir
                        if variation.get('images') and variation['images']:
                            variant_images = variation['images']
                            if isinstance(variant_images, list) and len(variant_images) > 0:
                                row[headers.index('Variant Image')] = safe_get(variant_images[0], 'src', '')
                            elif isinstance(variant_images, str):
                                row[headers.index('Variant Image')] = variant_images
                        
                        row[headers.index('Variant Requires Shipping')] = 'TRUE'
                        row[headers.index('Variant Taxable')] = 'TRUE'
                        row[headers.index('Gift Card')] = 'FALSE'
                        row[headers.index('Variant Weight Unit')] = 'g'
                        row[headers.index('Included / United States')] = 'TRUE'
                        row[headers.index('Included / International')] = 'TRUE'
                        row[headers.index('Status')] = status
                        
                        csv_rows.append(row)
                        
                    except Exception as e:
                        print(f"Erro ao processar variação do produto '{title}': {e}")
                        continue
            else:
                # Produto simples (sem variações)
                try:
                    row = [''] * len(headers)
                    
                    row[headers.index('Handle')] = handle
                    row[headers.index('Title')] = title
                    row[headers.index('Body (HTML)')] = body_html
                    row[headers.index('Vendor')] = vendor
                    row[headers.index('Type')] = category
                    row[headers.index('Tags')] = tags
                    row[headers.index('Published')] = 'TRUE' if status == 'active' else 'FALSE'
                    row[headers.index('Option1 Name')] = 'Title'
                    row[headers.index('Option1 Value')] = 'Default Title'
                    row[headers.index('Variant SKU')] = safe_get(product, 'sku', '')
                    row[headers.index('Variant Grams')] = weight_grams
                    row[headers.index('Variant Inventory Tracker')] = 'shopify'
                    row[headers.index('Variant Inventory Qty')] = 0
                    row[headers.index('Variant Inventory Policy')] = 'deny'
                    row[headers.index('Variant Fulfillment Service')] = 'manual'
                    row[headers.index('Variant Price')] = price
                    
                    if compare_price:
                        row[headers.index('Variant Compare At Price')] = compare_price
                    
                    row[headers.index('Variant Requires Shipping')] = 'TRUE'
                    row[headers.index('Variant Taxable')] = 'TRUE'
                    row[headers.index('Gift Card')] = 'FALSE'
                    row[headers.index('SEO Title')] = seo_title
                    row[headers.index('SEO Description')] = seo_description[:320]
                    row[headers.index('Variant Weight Unit')] = 'g'
                    row[headers.index('Included / United States')] = 'TRUE'
                    row[headers.index('Included / International')] = 'TRUE'
                    row[headers.index('Status')] = status
                    
                    # Adiciona primeira imagem se existir
                    if images and len(images) > 0:
                        row[headers.index('Image Src')] = safe_get(images[0], 'src', '')
                        row[headers.index('Image Position')] = str(safe_get(images[0], 'position', 1))
                        row[headers.index('Image Alt Text')] = safe_get(images[0], 'alt', '') or title
                    
                    csv_rows.append(row)
                    
                except Exception as e:
                    print(f"Erro ao processar produto simples '{title}': {e}")
                    continue
            
            # Adiciona linhas para imagens do produto
            try:
                if images and len(images) > 0:
                    # Para produtos com variações, adiciona a primeira imagem na primeira linha
                    if variations and csv_rows:
                        first_row_index = len(csv_rows) - len(variations)
                        if first_row_index >= 0 and not csv_rows[first_row_index][headers.index('Image Src')]:
                            csv_rows[first_row_index][headers.index('Image Src')] = safe_get(images[0], 'src', '')
                            csv_rows[first_row_index][headers.index('Image Position')] = str(safe_get(images[0], 'position', 1))
                            csv_rows[first_row_index][headers.index('Image Alt Text')] = safe_get(images[0], 'alt', '') or title
                    
                    # Adiciona imagens adicionais em linhas separadas
                    for j, image in enumerate(images[1:], start=2):
                        try:
                            image_row = [''] * len(headers)
                            image_row[headers.index('Handle')] = handle
                            image_row[headers.index('Image Src')] = safe_get(image, 'src', '')
                            image_row[headers.index('Image Position')] = str(safe_get(image, 'position', j))
                            image_row[headers.index('Image Alt Text')] = safe_get(image, 'alt', '') or title
                            csv_rows.append(image_row)
                        except Exception as e:
                            print(f"Erro ao processar imagem {j} do produto '{title}': {e}")
                            continue
            except Exception as e:
                print(f"Erro ao processar imagens do produto '{title}': {e}")
            
            processed_count += 1
            if processed_count % 50 == 0:
                print(f"Processados {processed_count} produtos...")
                
        except Exception as e:
            print(f"Erro ao processar produto {i+1} ('{product.get('name', 'SEM NOME')}'): {e}")
            error_count += 1
            continue
    
    # Escreve o arquivo CSV
    try:
        print("Escrevendo arquivo CSV...")
        
        # Cria a pasta converted se não existir
        converted_dir = "converted"
        os.makedirs(converted_dir, exist_ok=True)
        
        # Caminho completo do arquivo CSV
        csv_filepath = os.path.join(converted_dir, os.path.basename(csv_file_path))
        
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(csv_rows)
        
        print(f"\n✅ Conversão concluída!")
        print(f"📊 Produtos processados: {processed_count}")
        print(f"❌ Erros encontrados: {error_count}")
        print(f"📄 Linhas no CSV: {len(csv_rows) + 1}")  # +1 para o cabeçalho
        print(f"💾 Arquivo CSV gerado: {csv_filepath}")
        
    except Exception as e:
        print(f"❌ Erro ao escrever arquivo CSV: {e}")

if __name__ == "__main__":
    # Busca o produtos.json da pasta imported e salva CSV na pasta converted
    json_path = os.path.join("imported", "produtos.json")
    csv_path = "produtos_shopify_completo.csv"  # Nome do arquivo, pasta será definida pela função
    
    if not os.path.exists(json_path):
        print(f"❌ Arquivo não encontrado: {json_path}")
        print("Execute primeiro o script importProductsFromBagy.py para gerar o arquivo produtos.json")
    else:
        convert_bagy_to_shopify_csv(json_path, csv_path)
