from flask import Flask, render_template, request, jsonify
import folium
import json
import os
import glob
import webbrowser
import threading

app = Flask(__name__)

# Carrega as cidades do arquivo JSON
def carregar_cidades():
    json_path = os.path.join(os.path.dirname(__file__), 'cidades_brasil.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

CIDADES_BRASIL = carregar_cidades()

# Diretórios
KML_DIR = os.path.join(os.path.dirname(__file__), 'goias_kml')
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache_municipios')

# Cria o diretório de cache se não existir
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Cache para armazenar polígonos dos municípios
cache_poligonos = {}

def encontrar_kml_municipio(nome_municipio):
    """
    Encontra o arquivo KML correspondente ao município.
    """
    # Normaliza o nome do município para busca
    nome_normalizado = nome_municipio.lower()
    nome_normalizado = nome_normalizado.replace('á', 'a').replace('â', 'a').replace('ã', 'a')
    nome_normalizado = nome_normalizado.replace('é', 'e').replace('ê', 'e')
    nome_normalizado = nome_normalizado.replace('í', 'i')
    nome_normalizado = nome_normalizado.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
    nome_normalizado = nome_normalizado.replace('ú', 'u').replace('ü', 'u')
    nome_normalizado = nome_normalizado.replace('ç', 'c')
    nome_normalizado = nome_normalizado.replace(' ', '_')
    nome_normalizado = nome_normalizado.replace('-', '_')
    
    # Busca por arquivos KML que contenham o nome
    pattern = os.path.join(KML_DIR, f"*{nome_normalizado}*.kml")
    arquivos = glob.glob(pattern)
    
    if arquivos:
        return arquivos[0]
    
    # Tenta busca mais flexível
    for arquivo in glob.glob(os.path.join(KML_DIR, "*.kml")):
        nome_arquivo = os.path.basename(arquivo).lower()
        if nome_normalizado in nome_arquivo:
            return arquivo
    
    return None

def kml_para_geojson(kml_path):
    """
    Converte arquivo KML para GeoJSON extraindo coordenadas dos polígonos.
    """
    try:
        with open(kml_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrai coordenadas usando parsing simples
        import re
        
        # Busca por tags <coordinates>
        coord_pattern = r'<coordinates>(.*?)</coordinates>'
        matches = re.findall(coord_pattern, conteudo, re.DOTALL)
        
        features = []
        for match in matches:
            coords_text = match.strip()
            coords_list = []
            
            # Parse das coordenadas (formato: lon,lat,alt lon,lat,alt ...)
            for linha in coords_text.split():
                linha = linha.strip()
                if not linha:
                    continue
                
                partes = linha.split(',')
                if len(partes) >= 2:
                    try:
                        lon = float(partes[0])
                        lat = float(partes[1])
                        coords_list.append([lon, lat])
                    except ValueError:
                        continue
            
            if coords_list and len(coords_list) > 2:  # Precisa de pelo menos 3 pontos para um polígono
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords_list]
                    },
                    "properties": {}
                }
                features.append(feature)
        
        if features:
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            return geojson
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao converter KML: {str(e)}")
        return None

def obter_poligono_municipio(codigo_ibge, nome_municipio):
    """
    Obtém o polígono geográfico do município a partir dos arquivos KML locais.
    Os dados são armazenados em cache para melhor performance.
    """
def obter_poligono_municipio(codigo_ibge, nome_municipio):
    """
    Obtém o polígono geográfico do município a partir dos arquivos KML locais.
    Os dados são armazenados em cache para melhor performance.
    """
    if not nome_municipio:
        print(f"❌ ERRO: Nome do município não fornecido!")
        return None
    
    # Verifica se já está no cache em memória
    if nome_municipio in cache_poligonos:
        print(f"✅ Cache (memória): {nome_municipio}")
        return cache_poligonos[nome_municipio]
    
    # Verifica se existe cache em disco (GeoJSON convertido)
    cache_file = os.path.join(CACHE_DIR, f"{nome_municipio.replace(' ', '_')}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                geojson = json.load(f)
                
                # Valida se o GeoJSON tem dados
                if geojson and 'features' in geojson and geojson['features']:
                    cache_poligonos[nome_municipio] = geojson
                    print(f"✅ Cache (disco): {nome_municipio}")
                    return geojson
                else:
                    print(f"⚠️ Cache inválido para {nome_municipio}, reprocessando...")
                    os.remove(cache_file)
        except Exception as e:
            print(f"⚠️ Erro ao ler cache de {nome_municipio}: {str(e)}")
            if os.path.exists(cache_file):
                os.remove(cache_file)
    
    # Busca o arquivo KML local
    print(f"🔍 Buscando KML local: {nome_municipio}...")
    kml_path = encontrar_kml_municipio(nome_municipio)
    
    if not kml_path:
        print(f"❌ ERRO: Arquivo KML não encontrado para {nome_municipio}")
        return None
    
    print(f"📂 KML encontrado: {os.path.basename(kml_path)}")
    
    # Converte KML para GeoJSON
    geojson = kml_para_geojson(kml_path)
    
    if geojson:
        # Salva no cache em disco
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, ensure_ascii=False)
            print(f"✅ Polígono convertido e salvo: {nome_municipio}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {str(e)}")
        
        # Salva no cache em memória
        cache_poligonos[nome_municipio] = geojson
        return geojson
    else:
        print(f"❌ ERRO: Não foi possível converter KML para GeoJSON: {nome_municipio}")
        return None

def calcular_centroide(geojson):
    """
    Calcula o centroide (ponto central) de um polígono GeoJSON.
    """
    try:
        if not geojson or 'features' not in geojson or not geojson['features']:
            return None
        
        # Pega o primeiro polígono
        coords = geojson['features'][0]['geometry']['coordinates'][0]
        
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
    return render_template('index.html', cidades=sorted(CIDADES_BRASIL.keys()))

@app.route('/adicionar_cidade', methods=['POST'])
def adicionar_cidade():
    data = request.json
    cidade = data.get('cidade')
    cor = data.get('cor', '#FF0000')
    
    if cidade in CIDADES_BRASIL:
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
    # Cria o mapa centrado em Goiás
    mapa = folium.Map(
        location=[-16.0, -49.5],  # Centro de Goiás
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Adiciona polígonos para cada cidade selecionada
    for cidade, cor in cidades_selecionadas.items():
        print(f"\n🎨 Processando: {cidade} (cor: {cor})")
        
        if cidade not in CIDADES_BRASIL:
            print(f"⚠️ {cidade} não encontrada no banco de dados")
            continue
        
        info = CIDADES_BRASIL[cidade]
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
            
            # Adiciona um marcador no centro do município (usando centroide do polígono)
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

def abrir_navegador():
    """Abre o navegador automaticamente após iniciar o servidor"""
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Abre o navegador automaticamente em uma thread separada
    threading.Timer(1.5, abrir_navegador).start()
    
    # Inicia o servidor Flask
    app.run(debug=False, port=5000, use_reloader=False)
