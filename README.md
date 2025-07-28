# 🛒 Conversor Bagy → Shopify├── 📄 importProductsFromBagy.py        # Exporta produtos da API Bagy
├── 👥 importCustomersFromBagy.py       # Exporta clientes da API Bagy  
├── 🎟️ importDiscountCodeFromBagy.py    # Exporta cupons da API Bagy
├── 💰 importCashbackFromBagy.py        # Exporta saldos de cashback da API Bagy
├── 🎫 generateVouchersFromCashback.py  # Gera vouchers Shopify baseados em cashback
├── 🔄 convert_bagy_to_shopify_final.py # Converte JSON para CSV Shopify
├── 🔗 generateRedirects301.py          # Gera redirects 301 para SEO
├── 📋 requirements.txt                 # Dependências Python
├── 🔐 .env                            # Configurações (API_KEY)
├── 📖 README.md                       # Documentação do projeto
├── 📂 imported/                       # Arquivos brutos da Bagy
└── 📂 converted/                      # Arquivos prontos para Shopifygn="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)

*Scripts para apoio na migração de dados da plataforma Bagy (Dooca Commerce) para Shopify*

</div>


Este projeto automatiza a migração de dados da plataforma **Bagy (Dooca Commerce)** para o **Shopify**, convertendo os formatos de dados para serem compatíveis com a importação. O sistema processa seis tipos principais de dados:

- 📦 **Produtos** - Converte produtos com variações, preços, imagens e estoque
- 👥 **Clientes** - Exporta dados de clientes com endereços completos
- 🎟️ **Cupons** - Exporta códigos de desconto e promoções
- 💰 **Saldos de Cashback** - Exporta saldos atuais de cashback por customer_id (com tratamento robusto de erros da API)
- 🎫 **Vouchers de Cashback** - Converte saldos de cashback em cupons do Shopify (prova de conceito)
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
└── 📂 converted/                      # Arquivos prontos para Shopify
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

#### 1.5 📊 Como usar o generateVouchersFromCashback.py

### 🎯 Objetivo
Converte saldos de cashback da Bagy em cupons de desconto funcionais no Shopify, criando automaticamente as Price Rules e Discount Codes necessários.

### 📋 Pré-requisitos
1. **Arquivo de saldos:** Execute primeiro `importCashbackFromBagy.py` para gerar `cashback_saldos.json`
2. **APIs configuradas:** Configure as variáveis de ambiente para Bagy e Shopify
3. **Permissões Shopify:** Token deve ter os escopos: `read_customers`, `write_price_rules`, `write_discounts`

### ⚙️ Configuração do Shopify

#### 1. Criar App Privado no Shopify
```bash
# No admin do Shopify:
# 1. Vá em Apps > Apps privadas 
# 2. Clique em "Criar app privado"
# 3. Configure os escopos necessários:
#    - read_customers (buscar dados dos clientes)
#    - write_price_rules (criar regras de desconto)  
#    - write_discounts (criar códigos de desconto)
# 4. Copie o token de acesso gerado
```

#### 2. Configurar Variáveis de Ambiente
```bash
# No arquivo .env, adicione:
SHOPIFY_SHOP_DOMAIN=sua-loja.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_seu_token_aqui
```

### 🚀 Como executar
```bash
# 1. Certifique-se que o arquivo de cashback existe
python importCashbackFromBagy.py

# 2. Execute a criação de vouchers
python generateVouchersFromCashback.py
```

### 📊 O que o script faz

#### Processamento automático:
1. **Carrega dados:** Lê `imported/cashback_saldos.json`
2. **Filtra saldos:** Processa apenas saldos positivos (limite de 10 para teste)
3. **Busca clientes:** Obtém email via API da Bagy
4. **Encontra no Shopify:** Localiza cliente pelo email
5. **Cria Price Rule:** Regra de desconto restrita ao cliente
6. **Cria Discount Code:** Código único no formato `CASHBACK-NOME-ID`
7. **Exporta Excel:** Lista completa de vouchers criados

#### Segurança implementada:
- ✅ **Cupom restrito:** Apenas o cliente específico pode usar
- ✅ **Uso único:** Cada cupom só pode ser usado uma vez
- ✅ **Valor mínimo:** Pedido deve ser >= valor do cashback
- ✅ **Data de expiração:** Baseada na validade original do cashback

### 📈 Resultado
```
🎟️ Total de vouchers: 10
💰 Valor total: R$ 77.90
🔒 Restritos ao cliente: 10
🌍 Uso geral: 0
📄 Excel exportado: converted/vouchers_shopify_20250728_115524.xlsx
```

### 📁 Arquivo Excel gerado
O script cria automaticamente um arquivo Excel com:
- 📋 **Código do Voucher:** Ex: `CASHBACK-JOAOSILV-1234`
- 📧 **Email do Cliente:** Para identificação
- 👤 **Nome do Cliente:** Nome completo
- 💰 **Valor (R$):** Valor exato do desconto
- 📅 **Validade:** Data de expiração formatada
- 🎯 **Status:** Criado no Shopify ou Teste
- 🔒 **Restrição:** Restrito ao cliente ou Uso geral

### 🔧 Configurações avançadas

#### Processar todos os saldos (remover limite de teste):
```python
# Na linha ~429 do arquivo, altere:
positive_balances = filter_positive_balances(all_balances, limit=None)
```

#### Modo teste (sem Shopify):
```bash
# Remova as variáveis do Shopify do .env
# O script rodará em modo simulação
```

### 🚨 Problemas comuns

#### Erro de permissão:
```
🔒 Erro de permissão: Token precisa de aprovação para criar price rules
```
**Solução:** Solicite aprovação dos escopos `write_price_rules` no admin do Shopify

#### Cliente não encontrado:
```
⚠️ Cliente não encontrado no Shopify: email@cliente.com
```
**Resultado:** Cupom será criado para uso geral (qualquer cliente)

#### API da Bagy indisponível:
```
❌ Erro na requisição para cliente 12345: 500
```
**Resultado:** Cliente será pulado, processamento continua

---
```bash
# Execução completa
python importCashbackFromBagy.py

# Ver opções de ajuda
python importCashbackFromBagy.py --help
```

**📋 Funcionalidades:**
- ✅ **Busca Direta**: Usa endpoint `/cashbacks/customers/balances`
-  **Foco nos Saldos**: Exporta apenas customer_id e saldo atual (não histórico de transações)
- 🛡️ **Tratamento de Erros**: Detecta e trata erros da API automaticamente
- 📊 **Progresso Detalhado**: Mostra quantos clientes foram processados e quantos têm saldo

**📄 Arquivos Gerados:**
- `imported/cashback_saldos.xlsx` - Planilha Excel com saldos
- `imported/cashback_saldos.json` - Arquivo JSON com saldos  
- `imported/cashback_saldos_summary.txt` - Relatório com estatísticas

**🔧 Tratamento de Problemas da API:**
O script detecta automaticamente problemas na API Bagy (como o erro `Cannot read properties of undefined (reading 'startsWith')`) e tenta diferentes abordagens para garantir que os dados sejam coletados corretamente.

**📄 Arquivos Gerados:**
- `imported/cashback_saldos.xlsx` - Planilha Excel com saldos
- `imported/cashback_saldos.json` - Arquivo JSON com saldos  
- `imported/cashback_saldos_summary.txt` - Relatório com estatísticas

**🔧 Tratamento de Problemas da API:**
O script foi desenvolvido para contornar um bug conhecido da API Bagy no endpoint de saldos (`Cannot read properties of undefined (reading 'startsWith')`). Quando detecta este erro, automaticamente usa o método alternativo que:

1. Lista todos os clientes via `/customers` 
2. Para cada cliente, consulta o saldo individual via `/cashbacks/customers/{id}/balance`
3. Filtra apenas clientes com saldo > 0
4. Exporta os dados organizados

**� Estrutura dos Dados Exportados:**
```json
{
  "customer_id": 12345,
  "balance": 25.50,
  "next_expiration": "2024-12-31",
  "next_release": "2024-01-15"
}
```

**💡 Benefícios do Método Alternativo:**
- 🚀 Funciona mesmo com bugs na API Bagy
- 🎯 Filtra automaticamente apenas clientes com saldo
- 📈 Mostra progresso detalhado durante execução
- ⚡ Modo teste para validação rápida

#### 1.6 Gerar Vouchers de Cashback (Criação Automática no Shopify)
```bash
# Cria vouchers reais no Shopify - 10 primeiros casos
python generateVouchersFromCashback.py
```

**📋 Funcionalidades Completas:**
- ✅ **Lê Saldos de Cashback**: Usa arquivo `imported/cashback_saldos.json`
- 🔍 **Filtra Saldos Positivos**: Processa apenas clientes com saldo > 0
- 📧 **Busca Emails**: Consulta API da Bagy para obter email dos clientes
- 🏪 **Localiza no Shopify**: Encontra cliente pelo email
- 🎫 **Cria Price Rules**: Regras de desconto no Shopify
- 🎟️ **Cria Discount Codes**: Códigos únicos restritos ao cliente
- 📊 **Exporta Excel**: Lista completa de vouchers criados
- 📋 **Relatório Detalhado**: Status completo de cada voucher

**🔒 Segurança Implementada:**
- Cupons restritos especificamente ao cliente correto
- Uso único por cliente
- Valor mínimo do pedido = valor do cashback
- Data de expiração baseada no cashback original

**📄 Arquivo Excel Gerado:**
- Lista completa com códigos, emails, valores e validades
- Localizado em `converted/vouchers_shopify_[timestamp].xlsx`

#### 1.7 Gerar Vouchers de Cashback (Modo Conceito - Descontinuado)
```bash
# Prova de conceito - 10 primeiros casos
python generateVouchersFromCashback.py
```

**📋 Funcionalidades:**
- ✅ **Lê Saldos de Cashback**: Usa arquivo `imported/cashback_saldos.json`
- 🔍 **Filtra Saldos Positivos**: Processa apenas clientes com saldo > 0
- 📧 **Busca Emails**: Consulta API da Bagy para obter email dos clientes
- 🎫 **Prepara Vouchers**: Organiza dados para criação de cupons no Shopify
- 📊 **Relatório Detalhado**: Mostra valor, email e data de expiração

**📄 Dados Exibidos:**
- Customer ID e nome do cliente
- Email obtido via API da Bagy
- Valor do cashback (R$)
- Data de expiração do cashback
- Resumo total dos vouchers processados

**🔄 Próximos Passos:**
Este é um script de prova de conceito. A versão completa incluirá:
- Integração com API do Shopify para criação automática de cupons
- Processamento de todos os saldos (não apenas 10)
- Mapeamento de clientes Bagy → Shopify
- Criação de códigos únicos de desconto

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

### Para Clientes, Cupons e Cashback

- 📄 Use os arquivos Excel gerados na pasta `imported/`
- 🔧 Importe manualmente ou use ferramentas de migração do Shopify
- 💰 **Cashback**: Dados para referência e migração manual (Shopify não tem sistema nativo de cashback)

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
<summary><strong>� "Erro 500 no endpoint de cashback" (Cannot read properties of undefined)</strong></summary>

**Este é um erro conhecido da API Bagy relacionado ao endpoint `/cashbacks/customers/balances`.**

**Soluções automáticas do script:**
- ✅ O script detecta automaticamente este erro
- ✅ Usa método alternativo via endpoint `/customers`
- ✅ Consulta saldos individuais para cada cliente
- ✅ Filtra apenas clientes com saldo > 0

**Se o erro persistir:**
- ✅ Verifique se a API_KEY tem permissões para acessar cashback
- ✅ Aguarde alguns minutos e tente novamente
- ✅ Execute em horários de menor tráfego na API

</details>

<details>
<summary><strong>�📄 "Arquivo produtos.json não encontrado"</strong></summary>

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

<details>
<summary><strong>💰 "Nenhum dado de cashback encontrado"</strong></summary>

**Soluções:**
- ✅ Verifique se sua loja utiliza o sistema de cashback da Bagy
- ✅ Confirme se a API_KEY tem permissões para acessar dados de cashback
- ✅ Verifique se existem clientes com saldo ou lançamentos de cashback
- ✅ Consulte o suporte da Bagy sobre acesso aos endpoints de cashback

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
   ├── python importDiscountCodeFromBagy.py
   └── python importCashbackFromBagy.py

2. 🎫 Gerar Vouchers de Cashback (Opcional)
   └── python generateVouchersFromCashback.py

3. 🔄 Converter para Shopify
   └── python convert_bagy_to_shopify_final.py

4. 📦 Importar no Shopify
   ├── Produtos: produtos_shopify_completo.csv
   ├── Clientes: clientes_dooca.xlsx
   ├── Cupons: cupons_dooca.xlsx
   └── Cashback: cashback_saldos.xlsx (dados de referência)

5. 🔗 Gerar Redirects
   ├── Exportar produtos do Shopify → products_export_1.csv
   ├── python generateRedirects301.py
   └── Importar redirects_301.csv no Shopify
```

### 🎯 Resultado Final
- ✅ Todos os produtos migrados com variações corretas
- ✅ Clientes e cupons prontos para importação
- ✅ Dados de cashback exportados para análise e migração manual
- ✅ Vouchers de cashback preparados para criação no Shopify (prova de conceito)
- ✅ SEO preservado com redirects 301 automáticos
- ✅ URLs antigas redirecionam para as novas

---

<div align="center">

**📅 Julho 2025** | **🐍 Python 3.8+** | **📝 MIT License**

*Desenvolvido para facilitar a migração Bagy → Shopify*

</div>
