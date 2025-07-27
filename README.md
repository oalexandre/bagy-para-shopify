# 🛒 Conversor Bagy → Shopify

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)

*Scripts para apoio na migração de dados da plataforma Bagy (Dooca Commerce) para Shopify*

</div>

## 📋 Descriçã## 📈 Histórico de Versões

### v2.1 (Atual) 
- ✅ **NOVO**: Script de geração de redirects 301 automáticos
- ✅ Mapeamento SKU → Handle para preservar SEO
- ✅ Relatórios detalhados de redirects criados
- ✅ Integração completa com fluxo de migração

### v2.0 
- ✅ Uso de variáveis de ambiente (`.env`)
- ✅ Organização automática de pastas
- ✅ Regras aprimoradas de variação (Cor + Tamanho)
- ✅ Tratamento completo de imagens
- ✅ Compatibilidade total com template Shopify

### v1.0 (Inicial)
- ✅ Scripts básicos de exportação
- ✅ Conversão simples para CSV
- ✅ Estrutura de projeto básica
Este projeto automatiza a migração de dados da plataforma **Bagy (Dooca Commerce)** para o **Shopify**, convertendo os formatos de dados para serem compatíveis com a importação. O sistema processa quatro tipos principais de dados:

- 📦 **Produtos** - Converte produtos com variações, preços, imagens e estoque
- 👥 **Clientes** - Exporta dados de clientes com endereços completos
- 🎟️ **Cupons** - Exporta códigos de desconto e promoções
- 🔗 **Redirects 301** - Gera redirecionamentos para preservar SEO

### 🎯 Objetivo

Facilitar a migração completa de lojas virtuais da plataforma Bagy para o Shopify, garantindo que todos os dados sejam convertidos corretamente e estejam prontos para importação, seguindo as melhores práticas e padrões do Shopify. Inclui a criação automática de redirects 301 para preservar o SEO e evitar páginas 404.

## 📁 Estrutura do Projeto

```
bagy-para-shopify/
├── 📄 importProductsFromBagy.py        # Exporta produtos da API Bagy
├── 👥 importCustomersFromBagy.py       # Exporta clientes da API Bagy  
├── 🎟️ importDiscountCodeFromBagy.py    # Exporta cupons da API Bagy
├── 🔄 convert_bagy_to_shopify_final.py # Converte JSON para CSV Shopify
├── � generateRedirects301.py          # Gera redirects 301 para SEO
├── �📋 requirements.txt                 # Dependências Python
├── 🔐 .env                            # Configurações (API_KEY)
├── 📖 README.md                       # Documentação do projeto
├── 📂 imported/                       # Arquivos brutos da Bagy
│   ├── produtos.json
│   ├── produtos_dooca.xlsx
│   ├── clientes_dooca.xlsx
│   ├── cupons_dooca.xlsx
│   └── products_export_1.csv          # Exportação dos produtos do Shopify
└── 📂 converted/                      # Arquivos prontos para Shopify
    ├── produtos_shopify_completo.csv
    ├── redirects_301.csv              # Redirects prontos para importação
    └── redirects_detailed_report.csv  # Relatório detalhado dos redirects
```


## 🚀 Instalação e Configuração

### 📋 Pré-requisitos

- 🐍 **Python 3.8** ou superior
- 🌐 **Conexão com internet** (para acessar API da Bagy)
- 🔑 **API_KEY** válida da Bagy

### ⚡ Instalação Rápida

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd bagy-para-shopify
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o arquivo `.env`**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   API_KEY=sua_chave_api_da_bagy_aqui
   ```
   
   > 💡 **Como obter a API_KEY:** Entre em contato com o suporte da Bagy para obter sua chave de API

### 📦 Dependências

O projeto utiliza as seguintes bibliotecas Python:

- `requests` - Comunicação com API
- `openpyxl` - Manipulação de arquivos Excel  
- `pandas` - Processamento de dados
- `numpy` - Operações matemáticas
- `python-dotenv` - Carregamento de variáveis de ambiente


## 🔧 Como Usar

O processo de migração segue um fluxo sequencial simples:

### 📥 Passo 1: Exportar Dados da Bagy

#### 1.1 Exportar Produtos
```bash
python importProductsFromBagy.py
```
- ✅ Baixa todos os produtos da API Bagy
- 📄 Gera: `imported/produtos.json` e `imported/produtos_dooca.xlsx`
- 📋 Inclui: variações, preços, estoque, imagens, categorias

#### 1.2 Exportar Clientes  
```bash
python importCustomersFromBagy.py
```
- ✅ Baixa todos os clientes da API Bagy
- 📄 Gera: `imported/clientes_dooca.xlsx`
- 📋 Inclui: dados pessoais, endereços, telefones

#### 1.3 Exportar Cupons
```bash
python importDiscountCodeFromBagy.py
```
- ✅ Baixa todos os cupons de desconto da API Bagy
- 📄 Gera: `imported/cupons_dooca.xlsx`
- 📋 Inclui: códigos, valores, regras, validades

### 🔄 Passo 2: Converter para Shopify

#### 2.1 Converter Produtos
```bash
python convert_bagy_to_shopify_final.py
```
- ✅ Lê o arquivo `imported/produtos.json`
- 🔄 Converte para o formato CSV do Shopify
- 📄 Gera: `converted/produtos_shopify_completo.csv`
- ⚙️ Aplica regras específicas do Shopify

### 🔗 Passo 3: Gerar Redirects 301 (Opcional)

#### 3.1 Exportar Produtos do Shopify
Antes de gerar os redirects, você precisa exportar os produtos já importados no Shopify:

1. **No admin do Shopify**, vá em **Produtos**
2. Clique em **Exportar** (botão no canto superior direito)
3. Selecione:
   - **Formato**: CSV for Excel, Numbers, or other spreadsheet programs
   - **Exportar**: Todos os produtos
4. Baixe o arquivo e renomeie para `products_export_1.csv`
5. Coloque o arquivo na pasta `imported/`

#### 3.2 Gerar Arquivo de Redirects
```bash
python generateRedirects301.py
```
- ✅ Lê `imported/produtos.json` (URLs da Bagy)
- 🔍 Mapeia SKUs com `imported/products_export_1.csv` (Handles do Shopify)
- 📄 Gera: `converted/redirects_301.csv` (pronto para importação)
- 📊 Cria relatório detalhado em `converted/redirects_detailed_report.csv`

#### 3.3 Importar Redirects no Shopify
1. **No admin do Shopify**, vá em **Navegação** → **Redirecionamentos de URL**
2. Clique em **Importar redirecionamentos**
3. Faça upload do arquivo `converted/redirects_301.csv`
4. Confirme a importação

> 🎯 **Objetivo**: Preservar SEO mantendo as URLs antigas da Bagy redirecionando para as novas URLs do Shopify


## ⚙️ Regras de Conversão para Shopify

### 🎨 Variações de Produtos
- 🎨 **Option1**: Cor (sempre primeiro)
- 📏 **Option2**: Tamanho (sempre segundo)  
- 📊 **Ordenação**: Azul-P, Azul-M, Azul-G → Verde-P, Verde-M, Verde-G

### 📄 Estrutura do CSV
- **Primeira linha**: Dados completos do produto + primeira variação
- **Linhas seguintes**: Apenas Handle + dados das variações adicionais
- **Linhas de imagem**: Apenas Handle + dados da imagem

### 🖼️ Tratamento de Imagens
- ✅ Primeira imagem do produto na primeira linha
- ✅ Imagens de variação específicas quando disponíveis
- ✅ Imagens adicionais em linhas separadas

### 📋 Dados Obrigatórios
- **Handle** - Gerado automaticamente do nome
- **Title** - Nome do produto
- **Vendor** - Marca ou "Marca" como padrão
- **Price** - Preço da variação ou produto
- **Inventory Qty** - Estoque disponível

## 🛍️ Importação no Shopify

### Para Produtos

1. 🔐 Acesse seu painel administrativo do Shopify
2. 📋 Vá em **"Produtos"** > **"Importar"**
3. 📁 Selecione o arquivo: `converted/produtos_shopify_completo.csv`
4. 🗺️ Mapeie os campos conforme necessário
5. ▶️ Execute a importação

### Para Clientes e Cupons

- 📄 Use os arquivos Excel gerados na pasta `imported/`
- 🔧 Importe manualmente ou use ferramentas de migração do Shopify

## 🔗 Benefícios dos Redirects 301

Os redirects automáticos garantem uma migração sem perda de SEO:

### ✅ Vantagens
- 🎯 **Preserva ranking Google**: Mantém autoridade das páginas
- 👥 **Melhora experiência do usuário**: Evita páginas 404
- 📊 **Transfere link juice**: Preserva valor dos backlinks externos  
- 🤖 **Facilita reindexação**: Google entende a mudança de domínio
- ⚡ **Automático**: Processa centenas de produtos rapidamente

### 📋 Como funciona
1. **Mapeia por SKU**: Conecta produtos Bagy ↔ Shopify pelo mesmo SKU
2. **URLs de origem**: `https://www.asmanhas.com.br/produto-exemplo`
3. **URLs de destino**: `/products/produto-exemplo-shopify`
4. **Importação fácil**: Arquivo CSV pronto para o Shopify

> 💡 **Dica**: Execute os redirects após importar todos os produtos no Shopify para garantir que os handles estejam corretos.


## 🛠️ Solução de Problemas

### ❌ Erros Comuns

<details>
<summary><strong>🔑 "API_KEY não encontrada"</strong></summary>

**Soluções:**
- ✅ Verifique se o arquivo `.env` existe na pasta correta
- ✅ Confirme se a `API_KEY` está correta no arquivo `.env`
- ✅ Certifique-se de não haver espaços extras na chave

</details>

<details>
<summary><strong>📄 "Arquivo produtos.json não encontrado"</strong></summary>

**Soluções:**
- ✅ Execute primeiro `python importProductsFromBagy.py`
- ✅ Verifique se a pasta `imported/` foi criada
- ✅ Confirme se o arquivo foi gerado com sucesso

</details>

<details>
<summary><strong>🌐 "Erro de conexão com API"</strong></summary>

**Soluções:**
- ✅ Verifique sua conexão com internet
- ✅ Confirme se a API_KEY está válida e ativa
- ✅ Tente novamente após alguns minutos
- ✅ Verifique se não há firewall bloqueando

</details>

<details>
<summary><strong>🖼️ "Imagens não estão aparecendo"</strong></summary>

**Soluções:**
- ✅ Verifique se as URLs das imagens estão acessíveis publicamente
- ✅ Confirme se as imagens não foram removidas do servidor original
- ✅ Teste as URLs das imagens em um navegador

</details>

<details>
<summary><strong>🔗 "Nenhum redirect foi criado"</strong></summary>

**Soluções:**
- ✅ Verifique se o arquivo `products_export_1.csv` está na pasta `imported/`
- ✅ Confirme se você exportou os produtos do Shopify **após** importá-los
- ✅ Verifique se os SKUs coincidem entre Bagy e Shopify
- ✅ Execute primeiro `python importProductsFromBagy.py` e `python convert_bagy_to_shopify_final.py`

</details>

<details>
<summary><strong>📊 "Poucos redirects gerados"</strong></summary>

**Soluções:**
- ✅ Confirme que todos os produtos foram importados no Shopify
- ✅ Verifique se os SKUs não foram alterados durante a importação
- ✅ Confira o relatório `redirects_detailed_report.csv` para mais detalhes
- ✅ Produtos sem variações podem não ter SKUs mapeados

</details>

### 📊 Logs e Monitoramento

Todos os scripts mostram:
- ⏱️ Progresso da execução em tempo real
- 📈 Contadores de itens processados  
- ❌ Mensagens de erro detalhadas
- ✅ Confirmação dos arquivos gerados
- 📁 Localização dos arquivos salvos

## 📚 Informações Técnicas

### ⚡ Performance
- **API Bagy**: Delay de 350ms entre requests (evita rate limit)
- **Processamento**: Local, sem limites específicos
- **Arquivos grandes**: Processamento otimizado em lotes

### 🔧 Compatibilidade
- **Shopify**: Formato CSV oficial para importação
- **Excel**: Compatível com versões 2010+  
- **Python**: Testado em versões 3.8, 3.9, 3.10, 3.11, 3.12

### 🔒 Segurança
- **API_KEY**: Armazenada em arquivo `.env` (não versionado)
- **Dados**: Processados localmente
- **Privacidade**: Sem envio de dados para terceiros

## 📞 Suporte

### 🤝 Canais de Suporte

- **API da Bagy**: suporte@bagy.com.br
- **Importação Shopify**: [Documentação oficial do Shopify](https://help.shopify.com)
- **Este projeto**: Verifique os logs de erro e soluções acima

## � Exemplos Práticos

### 🔗 Exemplo de Redirect Gerado

```csv
Redirect from,Redirect to
/bandana-pet-calma-caraio-asmanhas,/products/bandana-pet-calma-caraio-asmanhas
/bandana-pet-calma-caraio-asmanhas/azul,/products/bandana-pet-calma-caraio-asmanhas
/camiseta-mestre-gambiarra-asmanhas,/products/camiseta-mestre-da-gambiarra-asmanhas
```

### 📊 Fluxo Completo de Migração

```
1. 📥 Exportar da Bagy
   ├── python importProductsFromBagy.py
   ├── python importCustomersFromBagy.py
   └── python importDiscountCodeFromBagy.py

2. 🔄 Converter para Shopify
   └── python convert_bagy_to_shopify_final.py

3. 📦 Importar no Shopify
   ├── Produtos: produtos_shopify_completo.csv
   ├── Clientes: clientes_dooca.xlsx
   └── Cupons: cupons_dooca.xlsx

4. 🔗 Gerar Redirects
   ├── Exportar produtos do Shopify → products_export_1.csv
   ├── python generateRedirects301.py
   └── Importar redirects_301.csv no Shopify
```

### 🎯 Resultado Final
- ✅ Todos os produtos migrados com variações corretas
- ✅ Clientes e cupons prontos para importação
- ✅ SEO preservado com redirects 301 automáticos
- ✅ URLs antigas redirecionam para as novas

## �📈 Histórico de Versões

### v2.0 (Atual) 
- ✅ Uso de variáveis de ambiente (`.env`)
- ✅ Organização automática de pastas
- ✅ Regras aprimoradas de variação (Cor + Tamanho)
- ✅ Tratamento completo de imagens
- ✅ Compatibilidade total com template Shopify

### v1.0 (Inicial)
- ✅ Scripts básicos de exportação
- ✅ Conversão simples para CSV
- ✅ Estrutura de projeto básica

---

<div align="center">

**📅 Julho 2025** | **🐍 Python 3.8+** | **📝 MIT License**

*Desenvolvido para facilitar a migração Bagy → Shopify*

</div>=
