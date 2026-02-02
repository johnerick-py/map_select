# Mapa de Municípios de Goiás - Shapefile Oficial IBGE 2023

Aplicação web que permite selecionar municípios de Goiás e visualizá-los em um mapa interativo com **limites territoriais oficiais do IBGE** usando shapefile e cores personalizadas.

## 📋 Funcionalidades

- ✅ **246 municípios** de Goiás carregados do shapefile oficial IBGE 2023
- 🎨 Escolha cores personalizadas para cada município
- 📤 **Upload de CSV em lote** para importar múltiplos municípios com cores
- 🗺️ Visualize os **limites territoriais exatos** usando dados vetoriais do IBGE
- 📍 Marcadores coloridos interativos (pode ativar/desativar)
- 🗑️ Remova municípios individualmente ou todos de uma vez
- 💾 Interface intuitiva e responsiva
- 🔄 GeoPandas para leitura eficiente do shapefile

## 🚀 Instalação e Execução (Windows)

### Pré-requisitos

- **Python 3.8 ou superior** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/download/win))

### Passo 1: Clone o Repositório

Abra o PowerShell ou CMD e execute:

```powershell
git clone https://github.com/johnerick-py/map_select.git
cd map_select
```

### Passo 2: Crie o Ambiente Virtual

```powershell
python -m venv venv
```

### Passo 3: Ative o Ambiente Virtual

```powershell
.\venv\Scripts\Activate
```

> **Nota**: Se aparecer erro de execução de scripts, execute este comando no PowerShell como Administrador:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Passo 4: Instale as Dependências

```powershell
pip install -r requirements.txt
```

> A instalação pode demorar alguns minutos pois inclui GeoPandas e suas dependências geoespaciais.

### Passo 5: Execute a Aplicação

```powershell
python app.py
```

A aplicação abrirá automaticamente no navegador em: **http://127.0.0.1:5000**

Para parar o servidor, pressione `Ctrl+C` no terminal.

## 🎯 Como Usar

### Modo Manual

1. **Selecione um Município**: Escolha da lista com 246 municípios de Goiás
2. **Escolha uma Cor**: Use o seletor de cores (#FF0000, etc)
3. **Adicione**: Clique em "✅ Adicionar Município"
4. **Visualize**: O mapa atualiza automaticamente com os polígonos

### Modo Upload CSV (Importação em Lote)

1. **Prepare seu CSV** com 2 colunas:
   ```csv
   cidade,cor
   GOIANIA,#FF0000
   anapolis,#00FF00
   Aparecida de Goiânia,#0000FF
   RIO VERDE,#FFFF00
   ```

2. **Formatos de Cor Suportados**:
   - Hexadecimal: `#FF0000`, `#00FF00`
   - RGB com ponto-e-vírgula: `rgb(255;0;0)`
   - RGB numérico: `255;165;0`

3. **Nomes de Municípios**:
   - ✅ Aceita com/sem acentos: `Goiânia` ou `GOIANIA`
   - ✅ Aceita maiúsculas/minúsculas: `goiania`, `GOIANIA`, `Goiânia`
   - ✅ Normalização automática para encontrar no shapefile

4. **Faça o Upload**:
   - Clique em "Selecione arquivo CSV" na seção **📤 Importar CSV**
   - Escolha seu arquivo .csv
   - Clique em "📥 Importar e Gerar Mapa"

5. **Resultado**:
   - ✅ Municípios válidos são adicionados automaticamente
   - ⚠️ Erros são reportados no console (município não encontrado, cor inválida)
   - 🗺️ Mapa atualiza automaticamente com todos os municípios
   - 📊 Contador mostra quantos municípios foram importados

### Controles de Visualização

- **📍 Mostrar marcadores**: Marque/desmarque para ativar/desativar pins no mapa
- **🗑️ Limpar Tudo**: Remove todos os municípios selecionados
- **✕ Remover**: Remove município individual da lista

## 📦 Tecnologias Utilizadas

- **Flask 3.0.0**: Framework web Python
- **Folium 0.15.1**: Biblioteca para mapas interativos Leaflet.js
- **GeoPandas 0.14.2**: Manipulação de dados geoespaciais e shapefile
- **Fiona 1.9.6**: Leitura de formatos geoespaciais
- **Pandas**: Processamento de arquivos CSV
- **Shapely**: Operações geométricas com polígonos
- **PyProj**: Projeções cartográficas
- **HTML/CSS/JavaScript**: Interface web responsiva

## 🗺️ Dados Geográficos

### Shapefile Oficial IBGE 2023

- **Fonte**: Instituto Brasileiro de Geografia e Estatística (IBGE)
- **Ano**: 2023 (malha municipal mais recente)
- **Municípios**: 246 municípios de Goiás
- **Formato**: Shapefile (.shp, .dbf, .shx, .prj, .cpg)
- **Pasta**: `GO_Municipios_2023/`

### Colunas do Shapefile

- `CD_MUN`: Código IBGE do município (7 dígitos)
- `NM_MUN`: Nome oficial do município
- `AREA_KM2`: Área territorial em quilômetros quadrados
- `geometry`: Polígono geográfico (MultiPolygon/Polygon)

## 🔧 Estrutura do Projeto

```
map_select/
├── app.py                      # Aplicação Flask principal
├── requirements.txt            # Dependências Python
├── cidades_brasil.json         # Dados complementares dos municípios
├── teste_municipios.csv        # Arquivo CSV de exemplo
├── GO_Municipios_2023/         # Shapefile oficial IBGE 2023
│   ├── GO_Municipios_2023.shp  # Arquivo principal do shapefile
│   ├── GO_Municipios_2023.dbf  # Tabela de atributos
│   ├── GO_Municipios_2023.shx  # Índice espacial
│   ├── GO_Municipios_2023.prj  # Sistema de coordenadas
│   └── GO_Municipios_2023.cpg  # Codificação de caracteres
├── templates/
│   └── index.html              # Interface web
├── cache_municipios/           # Cache (criado automaticamente)
└── README.md                   # Este arquivo
```

## 📝 Notas Técnicas

- Os polígonos são carregados do shapefile IBGE 2023 na inicialização
- GeoPandas processa os dados geoespaciais de forma eficiente
- Normalização de nomes remove acentos e padroniza para busca
- Suporta geometrias MultiPolygon e Polygon
- Cache em memória evita reprocessamento dos polígonos
- Conversão automática de cores RGB para hexadecimal

## ⚠️ Solução de Problemas

### Erro ao ativar ambiente virtual (Windows)

Se aparecer erro de política de execução:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro de instalação do GeoPandas

Se a instalação falhar, tente instalar as dependências geoespaciais separadamente:

```powershell
pip install fiona==1.9.6
pip install geopandas==0.14.2
```

### Shapefile não carrega

Verifique se a pasta `GO_Municipios_2023/` existe e contém todos os arquivos (.shp, .dbf, .shx, .prj, .cpg).

### CSV não importa

- Verifique se o arquivo tem extensão `.csv`
- Certifique-se de que tem pelo menos 2 colunas
- Use ponto-e-vírgula no formato RGB: `rgb(255;0;0)` ou `255;0;0`
- Nomes de municípios podem ter acentos, serão normalizados automaticamente

## 🔧 Executável Windows

Para gerar o executável standalone:

```powershell
pyinstaller app.spec
```

O executável será criado em `dist/MapaMunicipiosGoias/MapaMunicipiosGoias.exe`

## 📄 Licença

Dados geográficos fornecidos pelo IBGE (domínio público).

---

**Desenvolvido com ❤️ para visualização de dados geoespaciais do estado de Goiás**
