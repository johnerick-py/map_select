# Mapa de Municípios de Goiás - Limites Territoriais Exatos

Aplicação web que permite selecionar municípios de Goiás e visualizá-los em um mapa interativo com **limites territoriais exatos** e cores personalizadas.

## 📋 Funcionalidades

- ✅ Selecione municípios de Goiás de uma lista com 50+ municípios
- 🎨 Escolha cores personalizadas para cada município
- 🗺️ Visualize os **limites territoriais exatos** dos municípios (polígonos do IBGE)
- 📍 Marcadores coloridos e interativos
- 🗑️ Remova municípios individualmente ou todos de uma vez
- 💾 Interface intuitiva e responsiva
- 🔄 Cache local de polígonos para melhor performance

## 🚀 Como Usar

### 1. Instalação das Dependências

Com a venv ativada, instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
python app.py
```

### 3. Acessar no Navegador

Abra seu navegador e acesse:
```
http://localhost:5000
```

## 🎯 Como Funciona

1. **Selecione um Município**: Escolha um município de Goiás da lista suspensa
2. **Escolha uma Cor**: Use o seletor de cores para personalizar
3. **Adicione**: Clique em "Adicionar Município"
4. **Visualize**: Clique em "Atualizar Mapa" para ver os limites territoriais exatos
5. **Gerencie**: Remova municípios individualmente ou limpe todos

## 📦 Tecnologias Utilizadas

- **Flask**: Framework web Python
- **Folium**: Biblioteca para mapas interativos
- **API IBGE**: Dados geográficos oficiais dos municípios brasileiros
- **HTML/CSS/JavaScript**: Interface do usuário
- **GeoJSON**: Formato de dados geográficos para polígonos municipais
- **html2canvas**: Captura de tela do mapa para exportação
- **jsPDF**: Geração de arquivos PDF no navegador
- **Selenium + ChromeDriver**: Captura de screenshots do mapa renderizado
- **Pillow (PIL)**: Manipulação de imagens
- **ReportLab**: Geração de PDFs com layout profissional

## 🗺️ Municípios Disponíveis

A aplicação inclui mais de 50 municípios de Goiás, incluindo:
- Goiânia (capital)
- Aparecida de Goiânia
- Anápolis
- Rio Verde
- Luziânia
- E muitos outros...

## 🎨 Limites Territoriais Exatos

Os limites dos municípios são obtidos diretamente da **API de Malhas do IBGE**, garantindo:
- ✅ Precisão oficial dos territórios municipais
- ✅ Polígonos geográficos reais (não aproximações)
- ✅ Dados atualizados conforme malha municipal do IBGE
- ✅ Cache local para melhor performance

## � Exportação de Mapas

### Exportar como PNG
- Gera uma imagem de alta qualidade (1400x900px)
- **Processado no servidor** usando Selenium + Chrome headless
- Captura o mapa completo com todos os polígonos renderizados
- Formato ideal para apresentações e documentos
- Nome do arquivo: `mapa_municipios_goias_YYYY-MM-DD.png`

### Exportar como PDF
- Documento PDF profissional em formato A4 paisagem
- **Gerado no servidor** com ReportLab
- Inclui título, data de geração e número de municípios
- Rodapé com fonte dos dados (IBGE)
- Imagem do mapa em alta resolução
- Nome do arquivo: `mapa_municipios_goias_YYYY-MM-DD.pdf`

### Requisitos para Exportação
- **Google Chrome** instalado no sistema
- O ChromeDriver é instalado automaticamente pelo webdriver-manager
- Aguarde alguns segundos durante a geração (o mapa precisa renderizar)

## �🔧 Estrutura do Projeto

```
map_selectec_teste/
├── app.py                    # Aplicação Flask principal
├── cidades_brasil.json       # Dados dos municípios de Goiás
├── requirements.txt          # Dependências Python
├── templates/
│   └── index.html           # Interface web
├── cache_municipios/        # Cache de polígonos (criado automaticamente)
└── README.md
```

## 📝 Notas Técnicas

- Os polígonos são baixados da API do IBGE na primeira vez e armazenados em cache local
- O cache evita downloads repetidos e melhora a performance
- Cada município possui seu código IBGE para identificação única
- Em caso de falha no download, a aplicação usa um círculo como fallback

## 🔧 Possíveis Expansões

- Salvar configurações em arquivo
- Adicionar mais municípios de Goiás
- Calcular áreas e perímetros dos municípios
- Adicionar dados demográficos e socioeconômicos
- Exportar dados selecionados para Excel
- Adicionar filtros por região ou população
- Comparar múltiplos municípios com estatísticas
