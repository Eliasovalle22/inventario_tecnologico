import os

def buscar_url_incorrecta():
    templates_dir = 'templates'
    archivos_encontrados = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        content = f.read()
                        # Buscar URLs sin namespace
                        if "url 'lista'" in content or 'url "lista"' in content:
                            archivos_encontrados.append(file_path)
                            print(f"❌ Encontrado en: {file_path}")
                            # Mostrar las líneas alrededor
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if "url 'lista'" in line or 'url "lista"' in line:
                                    print(f"  Línea {i+1}: {line.strip()}")
                    except:
                        pass
    
    if not archivos_encontrados:
        print("✅ No se encontraron URLs incorrectas")
    
    return archivos_encontrados

if __name__ == "__main__":
    print("Buscando URLs incorrectas 'lista' sin namespace...")
    buscar_url_incorrecta()