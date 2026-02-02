from flask import Flask, render_template, request, jsonify
import folium
import json
import os
import glob
import webbrowser
import threading
import geopandas as gpd
import pandas as pd
import re
from unicodedata import normalize

app = Flask(__name__)

# Carrega as cidades do arquivo JSON
def carregar_cidades():
    json_path = os.path.join(os.path.dirname(__file__), 'cidades_brasil.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

CIDADES_BRASIL = carregar_cidades()

# Diretórios
SHAPEFILE_PATH = os.path.join(os.path.dirname(__file__), 'GO_Municipios_2023', 'GO_Municipios_2023.shp')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache_municipios')

# Cria o diretório de cache se não existir
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Carrega o shapefile de Goiás
print("📍 Carregando shapefile de Goiás...")
try:
    # Força a leitura sem usar fiona.path
    import warnings
    warnings.filterwarnings('ignore')
    gdf_goias = gpd.read_file(SHAPEFILE_PATH, encoding='utf-8')
    print(f"✅ Shapefile carregado com {len(gdf_goias)} municípios")
    print(f"📋 Colunas disponíveis: {list(gdf_goias.columns)}")
except Exception as e:
    print(f"❌ Erro ao carregar shapefile: {e}")
    # Tenta novamente sem especificar encoding
    try:
        gdf_goias = gpd.read_file(SHAPEFILE_PATH)
        print(f"✅ Shapefile carregado com {len(gdf_goias)} municípios")
        print(f"📋 Colunas disponíveis: {list(gdf_goias.columns)}")
    except Exception as e2:
        print(f"❌ Erro crítico ao carregar shapefile: {e2}")
        gdf_goias = None

# Gera lista de municípios do shapefile
def gerar_lista_municipios():
    """
    Gera uma lista de municípios a partir do shapefile e do JSON.
    Combina dados do shapefile (todos os 246 municípios) com dados do JSON (população).
    """
    municipios = {}
    
    if gdf_goias is not None:
        # Adiciona todos os municípios do shapefile
        for idx, row in gdf_goias.iterrows():
            nome = row['NM_MUN']
            codigo = row['CD_MUN']
            
            # Busca dados adicionais do JSON se existir
            if nome in CIDADES_BRASIL:
                municipios[nome] = {
                    'codigo_ibge': str(codigo),
                    'lat': CIDADES_BRASIL[nome].get('lat', 0),
                    'lon': CIDADES_BRASIL[nome].get('lon', 0),
                    'populacao': CIDADES_BRASIL[nome].get('populacao', 0),
                    'estado': 'GO'
                }
            else:
                # Município não está no JSON, adiciona sem população
                municipios[nome] = {
                    'codigo_ibge': str(codigo),
                    'lat': 0,
                    'lon': 0,
                    'populacao': 0,
                    'estado': 'GO'
                }
        
        print(f"✅ Lista de municípios gerada: {len(municipios)} municípios")
    else:
        # Fallback para o JSON se o shapefile não carregar
        print(f"⚠️ Usando apenas dados do JSON")
        municipios = CIDADES_BRASIL
    
    return municipios

# Gera a lista completa de municípios
MUNICIPIOS_GOIAS = gerar_lista_municipios()

# Cache para armazenar polígonos dos municípios
cache_poligonos = {}

def normalizar_nome(nome):
    """
    Normaliza o nome do município para comparação.
    """
    nome_normalizado = nome.lower()
    nome_normalizado = nome_normalizado.replace('á', 'a').replace('â', 'a').replace('ã', 'a')
    nome_normalizado = nome_normalizado.replace('é', 'e').replace('ê', 'e')
    nome_normalizado = nome_normalizado.replace('í', 'i')
    nome_normalizado = nome_normalizado.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
    nome_normalizado = nome_normalizado.replace('ú', 'u').replace('ü', 'u')
    nome_normalizado = nome_normalizado.replace('ç', 'c')
    return nome_normalizado

def obter_poligono_municipio(codigo_ibge, nome_municipio):
    """
    Obtém o polígono geográfico do município a partir do shapefile.
    Os dados são armazenados em cache para melhor performance.
    """
    if not nome_municipio:
        print(f"❌ ERRO: Nome do município não fornecido!")
        return None
    
    if gdf_goias is None:
        print(f"❌ ERRO: Shapefile não carregado!")
        return None
    
    # Verifica se já está no cache em memória
    if nome_municipio in cache_poligonos:
        print(f"✅ Cache (memória): {nome_municipio}")
        return cache_poligonos[nome_municipio]
    
    # Busca o município no shapefile
    print(f"🔍 Buscando no shapefile: {nome_municipio}...")
    
    # Normaliza o nome para busca
    nome_normalizado = normalizar_nome(nome_municipio)
    
    # Busca na coluna NM_MUN (nome do município)
    municipio_encontrado = None
    for idx, row in gdf_goias.iterrows():
        nome_shp = normalizar_nome(str(row['NM_MUN']))
        if nome_normalizado == nome_shp:
            municipio_encontrado = row
            print(f"✅ Município encontrado: {row['NM_MUN']}")
            break
    
    if municipio_encontrado is None:
        print(f"❌ ERRO: Município não encontrado no shapefile: {nome_municipio}")
        print(f"   Tentando busca parcial...")
        # Tenta busca parcial
        for idx, row in gdf_goias.iterrows():
            nome_shp = normalizar_nome(str(row['NM_MUN']))
            if nome_normalizado in nome_shp or nome_shp in nome_normalizado:
                municipio_encontrado = row
                print(f"✅ Município encontrado (parcial): {row['NM_MUN']}")
                break
        
        if municipio_encontrado is None:
            return None
    
    # Converte geometria para GeoJSON
    try:
        geometry = municipio_encontrado['geometry']
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": geometry.__geo_interface__,
                "properties": {}
            }]
        }
        
        # Salva no cache em memória
        cache_poligonos[nome_municipio] = geojson
        print(f"✅ Polígono convertido: {nome_municipio}")
        return geojson
        
    except Exception as e:
        print(f"❌ ERRO ao converter geometria: {str(e)}")
        return None

def calcular_centroide(geojson):
    """
    Calcula o centroide (ponto central) de um polígono GeoJSON.
    """
    try:
        if not geojson or 'features' not in geojson or not geojson['features']:
            return None
        
        # Pega a geometria
        geometry = geojson['features'][0]['geometry']
        
        # Se for MultiPolygon, pega o primeiro polígono
        if geometry['type'] == 'MultiPolygon':
            coords = geometry['coordinates'][0][0]
        else:  # Polygon
            coords = geometry['coordinates'][0]
        
        # Calcula a média das coordenadas
        lons = [p[0] for p in coords]
        lats = [p[1] for p in coords]
        
        lon_centro = sum(lons) / len(lons)
        lat_centro = sum(lats) / len(lats)
        
        return [lat_centro, lon_centro]
    except Exception as e:
        print(f"⚠️ Erro ao calcular centroide: {str(e)}")
        return None

# Armazena as cidades selecionadas e suas cores
cidades_selecionadas = {}

@app.route('/')
def index():
    return render_template('index.html', cidades=sorted(MUNICIPIOS_GOIAS.keys()))

@app.route('/adicionar_cidade', methods=['POST'])
def adicionar_cidade():
    data = request.json
    cidade = data.get('cidade')
    cor = data.get('cor', '#FF0000')
    
    if cidade in MUNICIPIOS_GOIAS:
        cidades_selecionadas[cidade] = cor
        return jsonify({"success": True, "message": f"{cidade} adicionada com sucesso!"})
    return jsonify({"success": False, "message": "Cidade não encontrada!"})

@app.route('/remover_cidade', methods=['POST'])
def remover_cidade():
    data = request.json
    cidade = data.get('cidade')
    
    if cidade in cidades_selecionadas:
        del cidades_selecionadas[cidade]
        return jsonify({"success": True, "message": f"{cidade} removida com sucesso!"})
    return jsonify({"success": False, "message": "Cidade não está na seleção!"})

@app.route('/limpar_todas', methods=['POST'])
def limpar_todas():
    cidades_selecionadas.clear()
    return jsonify({"success": True, "message": "Todas as cidades foram removidas!"})

@app.route('/gerar_mapa')
def gerar_mapa():
    # Obtém parâmetro de exibição de pins
    mostrar_pins = request.args.get('mostrar_pins', 'true').lower() == 'true'
    
    # Cria o mapa centrado em Goiás
    mapa = folium.Map(
        location=[-16.0, -49.5],  # Centro de Goiás
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Adiciona polígonos para cada cidade selecionada
    for cidade, cor in cidades_selecionadas.items():
        print(f"\n🎨 Processando: {cidade} (cor: {cor})")
        
        if cidade not in MUNICIPIOS_GOIAS:
            print(f"⚠️ {cidade} não encontrada no banco de dados")
            continue
        
        info = MUNICIPIOS_GOIAS[cidade]
        populacao = info.get('populacao', 0)
        codigo_ibge = info.get('codigo_ibge', '')
        
        print(f"   Código IBGE: {codigo_ibge}")
        print(f"   População: {populacao:,}")
        
        # Obtém o polígono do município
        geojson = obter_poligono_municipio(codigo_ibge, cidade)
        
        if geojson:
            print(f"   ✅ GeoJSON obtido - Features: {len(geojson.get('features', []))}")
            
            # Calcula o centroide do polígono para posicionar o marcador
            centroide = calcular_centroide(geojson)
            if centroide:
                lat_marcador, lon_marcador = centroide
                print(f"   📍 Centroide calculado: Lat {lat_marcador:.4f}, Lon {lon_marcador:.4f}")
            else:
                # Fallback para coordenadas do JSON se não conseguir calcular centroide
                lat_marcador = info['lat']
                lon_marcador = info['lon']
                print(f"   ⚠️ Usando coordenadas do JSON")
            
            # Adiciona o polígono ao mapa com a cor selecionada
            folium.GeoJson(
                geojson,
                name=cidade,
                style_function=lambda feature, cor=cor: {
                    'fillColor': cor,
                    'color': cor,
                    'weight': 3,
                    'fillOpacity': 0.5,
                    'opacity': 0.9
                },
                tooltip=f"{cidade} - {info['estado']}",
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4 style="margin: 0 0 10px 0; color: {cor};">{cidade}</h4>
                        <p style="margin: 5px 0;"><b>Estado:</b> {info['estado']}</p>
                        <p style="margin: 5px 0;"><b>População:</b> {populacao:,}</p>
                        <p style="margin: 5px 0;"><b>Código IBGE:</b> {codigo_ibge}</p>
                    </div>
                    """,
                    max_width=250
                )
            ).add_to(mapa)
            
            print(f"   ✅ Polígono adicionado ao mapa")
            
            # Adiciona um marcador no centro do município (usando centroide do polígono) se a opção estiver ativada
            if mostrar_pins:
                folium.Marker(
                    location=[lat_marcador, lon_marcador],
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: Arial; text-align: center;">
                            <h4 style="margin: 0 0 10px 0; color: {cor};">{cidade}</h4>
                            <p style="margin: 5px 0;">População: {populacao:,}</p>
                        </div>
                        """,
                        max_width=200
                    ),
                    tooltip=cidade,
                    icon=folium.Icon(
                        color='red' if cor in ['#FF0000', '#DC143C', '#8B0000', '#FF6B6B'] else 
                              'blue' if cor in ['#0000FF', '#1E90FF', '#4169E1', '#4A90E2'] else 
                              'green' if cor in ['#008000', '#00FF00', '#32CD32', '#50C878'] else 
                              'orange' if cor in ['#FFA500', '#FF8C00', '#FF4500', '#FFB347'] else
                              'purple' if cor in ['#800080', '#9370DB', '#BA55D3'] else
                              'darkblue',
                        icon='info-sign'
                    )
                ).add_to(mapa)
                
                print(f"   ✅ Marcador adicionado ao mapa")
            else:
                print(f"   ⏭️ Marcador desabilitado (opção desmarcada)")
        else:
            print(f"   ❌ GeoJSON não disponível, usando círculo")
            # Fallback: se não conseguir o polígono, usa um círculo
            print(f"Usando círculo para {cidade} (polígono não disponível)")
            folium.Circle(
                location=[info['lat'], info['lon']],
                radius=5000,
                popup=f"<b>{cidade}</b><br>Estado: {info['estado']}<br>População: {populacao:,}<br><i>Polígono não disponível</i>",
                tooltip=f"{cidade} (aproximado)",
                color=cor,
                fill=True,
                fillColor=cor,
                fillOpacity=0.4,
                weight=3
            ).add_to(mapa)
    
    # Adiciona controle de camadas
    folium.LayerControl().add_to(mapa)
    
    # Salva o mapa em HTML
    mapa_html = mapa._repr_html_()
    return mapa_html

@app.route('/get_cidades_selecionadas')
def get_cidades_selecionadas():
    return jsonify(cidades_selecionadas)

def normalizar_nome_municipio(nome):
    """
    Normaliza o nome do município para comparação com o shapefile.
    Remove acentos, converte para maiúsculas e remove espaços extras.
    """
    # Remove acentos
    nome = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    # Converte para maiúsculas e remove espaços extras
    nome = nome.upper().strip()
    # Remove caracteres especiais exceto espaços
    nome = re.sub(r'[^A-Z\s]', '', nome)
    # Remove espaços duplos
    nome = ' '.join(nome.split())
    return nome

def converter_cor_para_hex(cor):
    """
    Converte cor de diferentes formatos para hexadecimal.
    Aceita: #RRGGBB, rgb(r;g;b), rgb(r,g,b), r;g;b
    """
    cor = cor.strip()
    
    # Já está em formato hex
    if cor.startswith('#'):
        if len(cor) == 7 and all(c in '0123456789ABCDEFabcdef' for c in cor[1:]):
            return cor.upper()
        else:
            return None
    
    # Formato rgb(r;g;b) ou rgb(r,g,b)
    if cor.startswith('rgb(') and cor.endswith(')'):
        cor = cor[4:-1]
    
    # Tenta separar por ponto e vírgula primeiro, depois por vírgula
    separador = ';' if ';' in cor else ','
    partes = [p.strip() for p in cor.split(separador)]
    
    if len(partes) == 3:
        try:
            r, g, b = [int(p) for p in partes]
            if all(0 <= v <= 255 for v in [r, g, b]):
                return f'#{r:02X}{g:02X}{b:02X}'
        except ValueError:
            return None
    
    return None

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """
    Processa upload de CSV com municípios e cores.
    Formato esperado: cidade,cor
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'message': 'Arquivo deve ser .csv'}), 400
        
        # Lê o CSV
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(file, encoding='latin-1')
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro ao ler CSV: {str(e)}'}), 400
        
        # Verifica se tem pelo menos 2 colunas
        if len(df.columns) < 2:
            return jsonify({'success': False, 'message': 'CSV deve ter pelo menos 2 colunas (cidade e cor)'}), 400
        
        # Pega as duas primeiras colunas
        coluna_cidade = df.columns[0]
        coluna_cor = df.columns[1]
        
        print(f"📁 Processando CSV: {len(df)} linhas")
        print(f"   Colunas: {coluna_cidade} | {coluna_cor}")
        
        adicionados = 0
        erros = []
        
        for idx, row in df.iterrows():
            try:
                cidade_original = str(row[coluna_cidade]).strip()
                cor_original = str(row[coluna_cor]).strip()
                
                # Normaliza o nome do município
                cidade_normalizada = normalizar_nome_municipio(cidade_original)
                
                # Busca o município no shapefile
                municipio_encontrado = None
                for nome_shp in MUNICIPIOS_GOIAS.keys():
                    if normalizar_nome_municipio(nome_shp) == cidade_normalizada:
                        municipio_encontrado = nome_shp
                        break
                
                if not municipio_encontrado:
                    erros.append({
                        'linha': idx + 2,  # +2 porque +1 do índice 0 e +1 do header
                        'cidade': cidade_original,
                        'erro': 'Município não encontrado no shapefile'
                    })
                    continue
                
                # Converte a cor para hexadecimal
                cor_hex = converter_cor_para_hex(cor_original)
                
                if not cor_hex:
                    erros.append({
                        'linha': idx + 2,
                        'cidade': cidade_original,
                        'erro': f'Cor inválida: {cor_original}'
                    })
                    continue
                
                # Adiciona à lista de cidades selecionadas
                cidades_selecionadas[municipio_encontrado] = cor_hex
                adicionados += 1
                
                print(f"   ✅ {cidade_original} → {municipio_encontrado} ({cor_hex})")
                
            except Exception as e:
                erros.append({
                    'linha': idx + 2,
                    'cidade': str(row[coluna_cidade]) if coluna_cidade in row else 'N/A',
                    'erro': str(e)
                })
        
        mensagem = f'{adicionados} municípios importados com sucesso'
        if erros:
            mensagem += f' ({len(erros)} erros)'
        
        return jsonify({
            'success': True,
            'message': mensagem,
            'adicionados': adicionados,
            'erros': erros
        })
        
    except Exception as e:
        print(f"❌ Erro no upload: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao processar arquivo: {str(e)}'}), 500

def abrir_navegador():
    """Abre o navegador automaticamente após iniciar o servidor"""
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Abre o navegador automaticamente em uma thread separada
    threading.Timer(1.5, abrir_navegador).start()
    
    # Inicia o servidor Flask
    app.run(debug=False, port=5000, use_reloader=False)
