# 🎯 Guia de Criação do Executável

Este guia explica como transformar a aplicação Flask em um executável standalone (.exe) que pode ser distribuído para qualquer máquina Windows sem necessidade de instalar Python.

## 📦 O que é PyInstaller?

**PyInstaller** empacota aplicações Python em executáveis standalone que incluem:
- ✅ Interpretador Python
- ✅ Todas as bibliotecas necessárias (Flask, Folium, Requests)
- ✅ Seus arquivos (templates, JSON, cache)
- ✅ Tudo em uma única pasta distribuível

## 🚀 Passo a Passo para Gerar o Executável

### 1. Instalar PyInstaller

Com a venv ativada, instale o PyInstaller:

```bash
pip install pyinstaller
```

### 2. Gerar o Executável

Execute o script de build:

```bash
build_exe.bat
```

**OU** manualmente:

```bash
pyinstaller --clean app.spec
```

### 3. Aguarde a Compilação

O processo pode levar alguns minutos. Você verá:
- Análise de dependências
- Compilação dos módulos
- Empacotamento dos arquivos

### 4. Resultado

Após concluir, você terá:

```
dist/
  └── MapaMunicipiosGoias/
      ├── MapaMunicipiosGoias.exe  ← EXECUTÁVEL PRINCIPAL
      ├── _internal/                ← Bibliotecas Python
      ├── templates/                ← Templates HTML
      ├── cache_municipios/         ← Cache de polígonos
      └── cidades_brasil.json       ← Dados das cidades
```

## 📂 Como Distribuir

### Para Distribuir para Outras Máquinas:

1. **Copie a pasta completa** `dist\MapaMunicipiosGoias\`
2. **Não copie apenas o .exe** - ele precisa da pasta `_internal` e dos arquivos de dados
3. Envie via:
   - ZIP/RAR compactado
   - Pen drive
   - Compartilhamento de rede
   - OneDrive/Google Drive

### Exemplo de estrutura para distribuição:

```
MapaMunicipiosGoias.zip
  └── MapaMunicipiosGoias/
      ├── MapaMunicipiosGoias.exe
      ├── _internal/
      ├── templates/
      ├── cache_municipios/
      └── cidades_brasil.json
```

## 🖥️ Como Executar

Na máquina de destino (sem Python instalado):

1. Extraia a pasta `MapaMunicipiosGoias`
2. Clique duas vezes em `MapaMunicipiosGoias.exe`
3. Uma janela de console aparecerá (mostrando logs do servidor)
4. **O navegador abrirá automaticamente** em `http://127.0.0.1:5000`
5. Use a aplicação normalmente!

### Para Fechar:

- Feche a janela do console (preta)
- Ou pressione `Ctrl+C` no console

## ⚙️ Configurações Avançadas

### Arquivo `app.spec`

O arquivo `app.spec` controla como o executável é gerado:

```python
# Ocultar console (janela preta)
console=False  # Mude para False para modo "sem console"

# Adicionar ícone personalizado
icon='icone.ico'  # Adicione um arquivo .ico

# Criar executável único (mais lento)
a = Analysis(...
    onefile=True,  # Gera um único .exe (maior e mais lento)
)
```

### Modificações Comuns:

**1. Sem Console (Modo Silencioso)**

Em `app.spec`, altere:
```python
console=False
```

**2. Adicionar Ícone**

Crie um arquivo `icone.ico` e em `app.spec`:
```python
icon='icone.ico'
```

**3. Executável Único (One-File)**

Para um único .exe (mais lento ao iniciar):
```bash
pyinstaller --onefile --windowed app.py
```

## 🔧 Resolução de Problemas

### Problema: "Módulo não encontrado"

**Solução**: Adicione ao `hiddenimports` em `app.spec`:
```python
hiddenimports=['nome_do_modulo'],
```

### Problema: "Arquivos não encontrados"

**Solução**: Adicione aos `datas` em `app.spec`:
```python
datas=[
    ('arquivo_ou_pasta', 'destino'),
],
```

### Problema: Executável muito grande

**Soluções**:
- Use `--exclude-module` para excluir módulos não usados
- Ative UPX compression (já ativado por padrão)
- Remova bibliotecas não essenciais

### Problema: Antivírus bloqueando

Executáveis gerados por PyInstaller podem ser marcados como falsos positivos:
- **Solução**: Adicione exceção no antivírus
- **Ou**: Assine digitalmente o executável (requer certificado)

## 📊 Tamanho do Executável

- **Pasta completa**: ~100-150 MB
- **Tempo de inicialização**: 3-5 segundos
- **Navegador abre**: automaticamente após 1.5 segundos

## 🎁 Recursos Incluídos no Executável

✅ Python 3.x (embarcado)
✅ Flask + dependências
✅ Folium (mapas)
✅ Requests (API IBGE)
✅ Templates HTML
✅ Dados de 50+ municípios de Goiás
✅ Cache de polígonos
✅ Abertura automática do navegador

## 📝 Notas Importantes

1. **Sem Internet**: A aplicação funciona offline após baixar os polígonos (eles ficam em cache)
2. **Primeira execução**: Mais lenta (baixa polígonos do IBGE)
3. **Execuções seguintes**: Rápidas (usa cache local)
4. **Navegador**: Abre automaticamente o navegador padrão do usuário
5. **Porta 5000**: Certifique-se que a porta está livre

## 🔄 Atualizações

Para atualizar o executável após modificar o código:

1. Modifique os arquivos Python
2. Execute novamente `build_exe.bat`
3. Distribua a nova pasta `dist\MapaMunicipiosGoias\`

## 📱 Alternativas

Se PyInstaller não funcionar bem:

- **cx_Freeze**: Similar ao PyInstaller
- **Nuitka**: Compila para C++ (mais rápido)
- **py2exe**: Específico para Windows

## 🌐 Executável vs Servidor Web

**Executável (PyInstaller)**:
- ✅ Fácil de distribuir
- ✅ Não requer Python
- ✅ Executa localmente
- ❌ ~150 MB por instalação
- ❌ Um usuário por vez

**Servidor Web**:
- ✅ Múltiplos usuários simultâneos
- ✅ Acesso remoto
- ✅ Atualizações centralizadas
- ❌ Requer servidor
- ❌ Requer Python instalado

---

**Criado com ❤️ para facilitar a distribuição da aplicação!**
