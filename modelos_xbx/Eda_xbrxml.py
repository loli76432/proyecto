import pandas as pd
import glob
import os

import re
import numpy as np
from difflib import SequenceMatcher
from collections import Counter
import json


# # Ruta a la carpeta
# carpeta = r"C:\Users\usuario\Documents\Python\00_xvxml_SMano\Datos"

# # Buscar todos los archivos que terminan en _procesado_limpio.csv
# archivos_csv = glob.glob(os.path.join(carpeta, "*.csv"))

# # Leer y concatenar todos los archivos
# df_unico = pd.concat([pd.read_csv(f) for f in archivos_csv], ignore_index=True)

# # Verificamos el resultado
#  print(f"Archivos combinados: {len(archivos_csv)}")
# # print(df_unico.head())

# # Guardar el DataFrame como archivo CSV
# df.to_csv("archivo_combinado.csv", index=False, encoding="utf-8")

#  df = df_unico.copy()

helb = (r'F:\00Proyecto_final\Datos\archivo_combinado.csv')
df = pd.read_csv(helb)
df.head(2)

# Prezio-kate guztietatik ikurrak eta hutsuneak kentzen ditu
df['Precio'] = df['Precio'].str.replace(r'[^\d.,]', '', regex=True)

# Komak puntu bihurtzen ditu eta float bihurtzen du
df['Precio'] = df['Precio'].str.replace(',', '.').astype(float)

# Maximoa kalkulatzen du
precio_maximo = df['Precio'].max()

print(f"💰 Precio máximo encontrado: {precio_maximo:.2f} EUR")



class DetectorMarcasTecnologicas:
    """
    Clase para detectar marcas y franquicias de aparatos tecnológicos en datos CSV.
    """
    
    def __init__(self):
        # Lista completa de marcas tecnológicas por categoría
        self.marcas_tecnologicas = {
            'smartphones': [
                'Apple', 'Samsung', 'Huawei', 'Xiaomi', 'OnePlus', 'Google', 'Sony',
                'LG', 'Motorola', 'Nokia', 'Oppo', 'Vivo', 'Realme', 'Honor',
                'Asus', 'HTC', 'BlackBerry', 'ZTE', 'Lenovo', 'Meizu', 'Alcatel',
                'TCL', 'Fairphone', 'Nothing', 'RedMi', 'Poco', 'iPhone', 'Galaxy',
                'Pixel', 'Xperia', 'Mi', 'Nord', 'Mate', 'P Series', 'Note'
            ],
            'laptops': [
                'Apple', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI', 'Toshiba',
                'Sony', 'Samsung', 'Microsoft', 'Razer', 'Alienware', 'ThinkPad',
                'MacBook', 'Surface', 'Pavilion', 'Inspiron', 'Latitude', 'XPS',
                'Yoga', 'IdeaPad', 'Legion', 'ROG', 'ZenBook', 'VivoBook',
                'Aspire', 'Predator', 'Nitro', 'Swift', 'Spin', 'TravelMate',
                'Vaio', 'Chromebook', 'EliteBook', 'ProBook', 'Spectre', 'Envy'
            ],
            'tablets': [
                'Apple', 'Samsung', 'Huawei', 'Lenovo', 'Microsoft', 'Amazon',
                'Google', 'Asus', 'Acer', 'Sony', 'LG', 'Xiaomi', 'OnePlus',
                'iPad', 'Galaxy Tab', 'Surface', 'Kindle', 'Fire', 'Nexus',
                'MediaPad', 'Tab', 'Yoga Tab', 'ZenPad', 'Iconia', 'Xperia Tablet'
            ],
            'televisores': [
                'Samsung', 'LG', 'Sony', 'Panasonic', 'Philips', 'TCL', 'Hisense',
                'Sharp', 'Toshiba', 'Vizio', 'Roku', 'Xiaomi', 'OnePlus',
                'OLED', 'QLED', 'LED', 'Smart TV', 'Android TV', 'webOS',
                'Bravia', 'Aquos', 'Viera', 'Ambilight', 'Neo QLED', 'NanoCell'
            ],
            'audio': [
                'Sony', 'Bose', 'Sennheiser', 'Audio-Technica', 'Beats', 'JBL',
                'Harman Kardon', 'Marshall', 'Klipsch', 'Yamaha', 'Pioneer',
                'Technics', 'Shure', 'AKG', 'Beyerdynamic', 'Focal', 'Grado',
                'Plantronics', 'Jabra', 'Skullcandy', 'Anker', 'Soundcore',
                'Bang & Olufsen', 'B&O', 'Ultimate Ears', 'UE', 'Logitech',
                'Razer', 'SteelSeries', 'HyperX', 'Corsair', 'Astro'
            ],
            'gaming': [
                'Sony', 'Microsoft', 'Nintendo', 'Valve', 'Razer', 'Logitech',
                'Corsair', 'SteelSeries', 'HyperX', 'Asus', 'MSI', 'Alienware',
                'PlayStation', 'Xbox', 'Switch', 'Steam Deck', 'ROG', 'Predator',
                'Legion', 'Omen', 'Pavilion Gaming', 'TUF', 'Strix', 'Nitro'
            ],
            'componentes': [
                'Intel', 'AMD', 'Nvidia', 'Qualcomm', 'Samsung', 'SK Hynix',
                'Micron', 'Western Digital', 'Seagate', 'Toshiba', 'Kingston',
                'Corsair', 'G.Skill', 'Crucial', 'EVGA', 'Asus', 'MSI',
                'Gigabyte', 'ASRock', 'Sapphire', 'PowerColor', 'XFX',
                'Core i3', 'Core i5', 'Core i7', 'Core i9', 'Ryzen', 'Threadripper',
                'GeForce', 'Radeon', 'RTX', 'GTX', 'RX', 'Vega', 'RDNA'
            ],
            'accesorios': [
                'Apple', 'Samsung', 'Anker', 'Belkin', 'Logitech', 'Razer',
                'Corsair', 'SteelSeries', 'HyperX', 'Jabra', 'Plantronics',
                'Mophie', 'Spigen', 'OtterBox', 'UAG', 'Peak Design',
                'Moment', 'DJI', 'GoPro', 'Insta360', 'Osmo', 'Action',
                'MagSafe', 'Qi', 'USB-C', 'Lightning', 'Thunderbolt'
            ],
            'impresoras_3d': [
                # Marcas principales de impresoras 3D
                'Prusa', 'Ultimaker', 'Creality', 'Bambu Lab', 'Formlabs', 'Stratasys',
                'Raise3D', 'Markforged', 'Zortrax', 'Flashforge', 'Anycubic',
                'Artillery', 'Qidi Tech', 'Elegoo', 'Monoprice', 'Dremel',
                'XYZprinting', 'LulzBot', 'Sindoh', 'Peopoly', 'Phrozen',
                'Cubify', 'Makerbot', 'Tiertime', 'Solidoodle', 'Robo 3D',
                'Printrbot', 'SeeMeCNC', 'Afinia', 'Type A Machines', 'Fusion3',
                'Modix', 'BigRep', 'Massivit', 'Desktop Metal', 'HP',
                'Canon', 'Epson', 'Brother', 'Ricoh', 'Konica Minolta',
                
                # Modelos específicos populares
                'Prusa i3', 'Prusa MK3', 'Prusa MK4', 'Prusa MINI', 'Prusa XL',
                'Ultimaker 2', 'Ultimaker 3', 'Ultimaker S3', 'Ultimaker S5',
                'Ender 3', 'Ender 5', 'Ender 7', 'CR-10', 'CR-6', 'CR-30',
                'Kobra', 'Vyper', 'Chiron', 'Mega', 'Photon', 'Mars',
                'Saturn', 'Jupiter', 'Neptune', 'Sidewinder', 'Genius',
                'A1 mini', 'A1', 'P1P', 'P1S', 'X1', 'X1 Carbon',
                'Form 2', 'Form 3', 'Form 4', 'Fuse 1', 'Fuse 2',
                'Replicator', 'Method', 'Sketch', 'Z18', 'F123',
                'M200', 'M300', 'Inventor', 'Adventurer', 'da Vinci',
                'Taz', 'Mini', 'Sidekick', 'Workhorse', 'Pro2',
                'Voxel8', 'Moment', 'Sonic', 'Magna', 'Liquid Crystal',
                
                # Tecnologías de impresión 3D
                'FDM', 'FFF', 'SLA', 'SLS', 'DLP', 'LCD', 'MSLA',
                'PolyJet', 'MultiJet', 'Binder Jetting', 'EBM', 'DMLS',
                'SLM', 'LOM', 'CJP', 'MJF', 'CLIP', 'Carbon M1',
                
                # Franquicias y distribuidores
                'Prusa Research', 'Bambu Lab', 'Creality 3D', 'Flashforge Corp',
                'Anycubic Technology', 'Artillery', 'Qidi Technology',
                'Elegoo Inc', 'Monoprice Inc', 'Dremel DigiLab',
                'XYZprinting Inc', 'Aleph Objects', 'Sindoh Co',
                'Peopoly Inc', 'Phrozen Technology', '3D Systems',
                'Cubify Inc', 'MakerBot Industries', 'Tiertime Corp',
                'Solidoodle Inc', 'Robo 3D Inc', 'Printrbot Inc',
                'SeeMeCNC Corp', 'Afinia 3D', 'Type A Machines',
                'Fusion3 Design', 'Modix 3D', 'BigRep GmbH'
            ]
        }
        
        # Crear lista unificada de todas las marcas
        self.todas_las_marcas = set()
        for categoria in self.marcas_tecnologicas.values():
            self.todas_las_marcas.update([marca.lower() for marca in categoria])
        
        # Patrones regex para detectar modelos y características
        self.patrones_modelo = {
            'numeros_modelo': r'[A-Z]{1,4}[-\s]?\d{2,4}[A-Z]?',
            'series_letra_numero': r'[A-Z]\d{1,3}',
            'android_version': r'Android\s+\d{1,2}\.?\d?',
            'ios_version': r'iOS\s+\d{1,2}\.?\d?',
            'memoria_ram': r'(\d+)\s*(GB|MB)\s*(RAM|Memory)',
            'almacenamiento': r'(\d+)\s*(GB|TB)\s*(Storage|SSD|HDD)',
            'procesador': r'(Intel|AMD|Snapdragon|Exynos|A\d+|M\d+)',
            'pantalla': r'(\d+\.?\d*)\s*(inch|"|pulgadas|″)',
            'resolucion': r'(\d+)x(\d+)|([48]K|HD|FHD|UHD|QHD)',
            'color': r'(Black|White|Blue|Red|Green|Gold|Silver|Rose|Gray|Grey|Space|Midnight|Pink|Purple|Yellow|Orange)',
            # Patrones específicos para impresoras 3D
            'volumen_impresion': r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)\s*(mm|cm)',
            'precision_capa': r'(\d+\.?\d*)\s*(mm|micron|μm)\s*(layer|capa)',
            'velocidad_impresion': r'(\d+)\s*(mm/s|mm/min)\s*(speed|velocidad)',
            'temperatura_extrusor': r'(\d+)\s*°?C\s*(extrusor|extruder|hotend)',
            'temperatura_cama': r'(\d+)\s*°?C\s*(cama|bed|heatbed)',
            'diametro_filamento': r'(\d+\.?\d*)\s*(mm)\s*(filament|filamento)',
            'tecnologia_impresion': r'(FDM|FFF|SLA|SLS|DLP|LCD|MSLA|PolyJet|MultiJet)',
            'conectividad_3d': r'(USB|SD|WiFi|Ethernet|Bluetooth)\s*(card|conexion|connectivity)?'
        }
        
        # Palabras clave adicionales para mejorar detección
        self.palabras_clave = {
            'dispositivos': ['phone', 'smartphone', 'tablet', 'laptop', 'notebook', 'computer', 'pc', 'tv', 'television', 'monitor', 'watch', 'smartwatch', 'headphones', 'earbuds', 'speaker', 'console', 'gaming', 'camera', 'drone', 'printer', 'impresora', '3d printer', 'impresora 3d'],
            'caracteristicas': ['pro', 'max', 'plus', 'mini', 'air', 'ultra', 'lite', 'se', 'edge', 'note', 'fold', 'flip', 'prime', 'elite', 'gaming', 'studio', 'book', 'go', 'surface'],
            'conectividad': ['wifi', 'bluetooth', 'cellular', '5g', '4g', 'lte', 'usb', 'type-c', 'lightning', 'wireless', 'nfc', 'ethernet', 'sd card'],
            'impresion_3d': ['fdm', 'fff', 'sla', 'sls', 'dlp', 'lcd', 'msla', 'resin', 'resina', 'filament', 'filamento', 'pla', 'abs', 'petg', 'tpu', 'wood', 'metal', 'carbon', 'nylon', 'support', 'soporte', 'infill', 'relleno', 'layer', 'capa', 'nozzle', 'boquilla', 'extruder', 'extrusor', 'heatbed', 'cama caliente', 'auto leveling', 'nivelacion automatica', 'dual extruder', 'doble extrusor', 'enclosed', 'cerrada', 'heated chamber', 'camara caliente']
        }
    
    def limpiar_texto(self, texto):
        """
        Limpia y normaliza el texto para mejor detección.
        """
        if pd.isna(texto):
            return ""
        
        # Convertir a string y minúsculas
        texto = str(texto).lower()
        
        # Eliminar caracteres especiales pero mantener espacios y guiones
        texto = re.sub(r'[^\w\s\-\.]', ' ', texto)
        
        # Normalizar espacios
        texto = ' '.join(texto.split())
        
        return texto
    
    def calcular_similaridad(self, texto1, texto2):
        """
        Calcula la similaridad entre dos textos.
        """
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def detectar_marca_exacta(self, texto):
        """
        Detecta marcas con coincidencia exacta.
        """
        texto_limpio = self.limpiar_texto(texto)
        palabras = texto_limpio.split()
        
        marcas_encontradas = []
        
        # Buscar coincidencias exactas
        for marca in self.todas_las_marcas:
            if marca in texto_limpio:
                marcas_encontradas.append(marca)
        
        # Buscar coincidencias por palabras
        for palabra in palabras:
            if palabra in self.todas_las_marcas:
                marcas_encontradas.append(palabra)
        
        return list(set(marcas_encontradas))
    
    def detectar_marca_fuzzy(self, texto, umbral=0.8):
        """
        Detecta marcas con búsqueda difusa.
        """
        texto_limpio = self.limpiar_texto(texto)
        palabras = texto_limpio.split()
        
        marcas_encontradas = []
        
        for palabra in palabras:
            if len(palabra) >= 3:  # Solo palabras de 3+ caracteres
                for marca in self.todas_las_marcas:
                    if len(marca) >= 3:
                        similitud = self.calcular_similaridad(palabra, marca)
                        if similitud >= umbral:
                            marcas_encontradas.append((marca, similitud))
        
        # Ordenar por similitud y devolver las mejores
        marcas_encontradas.sort(key=lambda x: x[1], reverse=True)
        return [marca for marca, _ in marcas_encontradas[:3]]
    
    def extraer_caracteristicas(self, texto):
        """
        Extrae características técnicas del texto.
        """
        texto_limpio = self.limpiar_texto(texto)
        caracteristicas = {}
        
        # Aplicar patrones regex
        for nombre_patron, patron in self.patrones_modelo.items():
            matches = re.findall(patron, texto_limpio, re.IGNORECASE)
            if matches:
                caracteristicas[nombre_patron] = matches
        
        # Buscar palabras clave
        for categoria, palabras in self.palabras_clave.items():
            palabras_encontradas = [palabra for palabra in palabras if palabra in texto_limpio]
            if palabras_encontradas:
                caracteristicas[categoria] = palabras_encontradas
        
        return caracteristicas
    
    def determinar_categoria(self, texto, marcas_detectadas):
        """
        Determina la categoría del dispositivo basándose en el texto y marcas.
        """
        texto_limpio = self.limpiar_texto(texto)
        
        puntuaciones = {categoria: 0 for categoria in self.marcas_tecnologicas.keys()}
        
        # Puntuación por marcas detectadas
        for marca in marcas_detectadas:
            for categoria, marcas_categoria in self.marcas_tecnologicas.items():
                if marca.title() in marcas_categoria or marca.lower() in [m.lower() for m in marcas_categoria]:
                    puntuaciones[categoria] += 2
        
        # Puntuación por marcas en texto
        for categoria, marcas_categoria in self.marcas_tecnologicas.items():
            for marca in marcas_categoria:
                if marca.lower() in texto_limpio:
                    puntuaciones[categoria] += 1
        
        # Puntuación por palabras clave de dispositivos
        palabras_dispositivos = {
            'smartphones': ['phone', 'smartphone', 'móvil', 'celular', 'iphone', 'android'],
            'laptops': ['laptop', 'notebook', 'computer', 'pc', 'macbook', 'ultrabook'],
            'tablets': ['tablet', 'ipad', 'tab'],
            'televisores': ['tv', 'television', 'televisor', 'smart tv', 'oled', 'qled'],
            'audio': ['headphones', 'auriculares', 'speaker', 'altavoz', 'earbuds', 'cascos'],
            'gaming': ['gaming', 'console', 'playstation', 'xbox', 'nintendo', 'switch'],
            'componentes': ['processor', 'gpu', 'cpu', 'ram', 'ssd', 'hdd', 'motherboard'],
            'accesorios': ['case', 'funda', 'protector', 'cable', 'cargador', 'soporte'],
            'impresoras_3d': ['3d printer', 'impresora 3d', 'printer', 'impresora', 'fdm', 'sla', 'resin', 'filament', 'filamento', 'extruder', 'extrusor', 'nozzle', 'boquilla', 'layer', 'capa', 'print', 'imprimir', 'printing', 'impresion']
        }
        
        for categoria, palabras in palabras_dispositivos.items():
            for palabra in palabras:
                if palabra in texto_limpio:
                    puntuaciones[categoria] += 1
        
        # Devolver la categoría con mayor puntuación
        categoria_detectada = max(puntuaciones.items(), key=lambda x: x[1])
        return categoria_detectada[0] if categoria_detectada[1] > 0 else 'desconocido'
    
    def procesar_campo(self, texto):
        """
        Procesa un campo de texto y extrae toda la información relevante.
        """
        if pd.isna(texto):
            return {
                'marca_detectada': None,
                'categoria': 'desconocido',
                'caracteristicas': {},
                'confianza': 0,
                'marcas_alternativas': [],
                'texto_original': texto
            }
        
        # Detectar marcas
        marcas_exactas = self.detectar_marca_exacta(texto)
        marcas_fuzzy = self.detectar_marca_fuzzy(texto)
        
        # Combinar resultados
        todas_marcas = list(set(marcas_exactas + marcas_fuzzy))
        
        # Determinar marca principal
        marca_principal = todas_marcas[0] if todas_marcas else None
        
        # Extraer características
        caracteristicas = self.extraer_caracteristicas(texto)
        
        # Determinar categoría
        categoria = self.determinar_categoria(texto, todas_marcas)
        
        # Calcular confianza
        confianza = self.calcular_confianza(texto, marca_principal, caracteristicas)
        
        return {
            'marca_detectada': marca_principal,
            'categoria': categoria,
            'caracteristicas': caracteristicas,
            'confianza': confianza,
            'marcas_alternativas': todas_marcas[1:] if len(todas_marcas) > 1 else [],
            'texto_original': texto
        }
    
    def calcular_confianza(self, texto, marca, caracteristicas):
        """
        Calcula un índice de confianza para la detección.
        """
        if not marca:
            return 0
        
        puntuacion = 0
        
        # Puntuación base por marca detectada
        puntuacion += 30
        
        # Puntuación por características detectadas
        puntuacion += len(caracteristicas) * 10
        
        # Puntuación por longitud del texto (más texto = más contexto)
        puntuacion += min(len(str(texto)), 100) * 0.2
        
        # Puntuación por coincidencia exacta de marca
        if marca.lower() in self.limpiar_texto(texto):
            puntuacion += 20
        
        # Normalizar a 0-100
        return min(puntuacion, 100)
    
    def añadir_campo_marca(self, df, campo_origen, nuevo_campo='marca_detectada', 
                          incluir_caracteristicas=True, incluir_categoria=True):
        """
        Añade campos de marca al DataFrame.
        """
        if campo_origen not in df.columns:
            raise ValueError(f"El campo '{campo_origen}' no existe en el DataFrame")
        
        print(f"🔍 Procesando {len(df)} registros...")
        
        # Procesar cada registro
        resultados = []
        for idx, valor in enumerate(df[campo_origen]):
            if idx % 100 == 0:
                print(f"   Procesando registro {idx+1}/{len(df)}")
            
            resultado = self.procesar_campo(valor)
            resultados.append(resultado)
        
        # Añadir campos al DataFrame
        df[nuevo_campo] = [r['marca_detectada'] for r in resultados]
        
        if incluir_categoria:
            df[f'{nuevo_campo}_categoria'] = [r['categoria'] for r in resultados]
        
        if incluir_caracteristicas:
            df[f'{nuevo_campo}_caracteristicas'] = [json.dumps(r['caracteristicas']) for r in resultados]
            df[f'{nuevo_campo}_confianza'] = [r['confianza'] for r in resultados]
            df[f'{nuevo_campo}_alternativas'] = [','.join(r['marcas_alternativas']) for r in resultados]
        
        return df
    
    def generar_reporte(self, df, campo_marca='marca_detectada'):
        """
        Genera un reporte del análisis de marcas.
        """
        print("\n" + "="*60)
        print("📊 REPORTE DE ANÁLISIS DE MARCAS")
        print("="*60)
        
        # Estadísticas generales
        total_registros = len(df)
        registros_con_marca = df[campo_marca].notna().sum()
        porcentaje_deteccion = (registros_con_marca / total_registros) * 100
        
        print(f"📈 Registros totales: {total_registros}")
        print(f"🎯 Registros con marca detectada: {registros_con_marca}")
        print(f"📊 Porcentaje de detección: {porcentaje_deteccion:.1f}%")
        
        # Top marcas detectadas
        if registros_con_marca > 0:
            top_marcas = df[campo_marca].value_counts().head(10)
            print(f"\n🏆 Top 10 marcas detectadas:")
            for marca, count in top_marcas.items():
                porcentaje = (count / registros_con_marca) * 100
                print(f"   • {marca}: {count} registros ({porcentaje:.1f}%)")
        
        # Análisis por categoría si existe
        if f'{campo_marca}_categoria' in df.columns:
            categorias = df[f'{campo_marca}_categoria'].value_counts()
            print(f"\n📱 Distribución por categoría:")
            for categoria, count in categorias.items():
                porcentaje = (count / total_registros) * 100
                print(f"   • {categoria}: {count} registros ({porcentaje:.1f}%)")
        
        # Análisis de confianza si existe
        if f'{campo_marca}_confianza' in df.columns:
            confianza_media = df[f'{campo_marca}_confianza'].mean()
            print(f"\n🎯 Confianza media: {confianza_media:.1f}")
            
            # Distribución de confianza
            rangos_confianza = pd.cut(df[f'{campo_marca}_confianza'], 
                                    bins=[0, 25, 50, 75, 100], 
                                    labels=['Baja (0-25)', 'Media (25-50)', 'Alta (50-75)', 'Muy Alta (75-100)'])
            distribucion = rangos_confianza.value_counts()
            print(f"📊 Distribución de confianza:")
            for rango, count in distribucion.items():
                porcentaje = (count / total_registros) * 100
                print(f"   • {rango}: {count} registros ({porcentaje:.1f}%)")

# Función de conveniencia para uso rápido
def detectar_marcas_csv(archivo_csv, campo_origen, nuevo_campo='marca_detectada', 
                       guardar_resultado=True, archivo_salida=None):
    """
    Función conveniente para detectar marcas en un archivo CSV.
    """
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    
    # Crear detector
    detector = DetectorMarcasTecnologicas()
    
    # Procesar
    df_resultado = detector.añadir_campo_marca(df, campo_origen, nuevo_campo)
    
    # Generar reporte
    detector.generar_reporte(df_resultado, nuevo_campo)
    
    # Guardar resultado
    if guardar_resultado:
        if archivo_salida is None:
            archivo_salida = archivo_csv.replace('.csv', '_con_marcas.csv')
        df_resultado.to_csv(archivo_salida, index=False)
        print(f"\n💾 Resultado guardado en: {archivo_salida}")
    
    return df_resultado

# Ejemplo de uso

# Crear detector
detector = DetectorMarcasTecnologicas()


# Procesar DataFrame
df_resultado = detector.añadir_campo_marca(df, 'Título', 'marca')


df_resultado.info()
df_resultado.head(8)
###         ====  Valores únicos por columna  =====
df_resultado.nunique()

### ✅ Paso 3: Conteo de valores únicos por variable (como desglose)

### columnas categóricas

for col in df_resultado.select_dtypes(include='object').columns:
    print(f"\n🧵 {col} - valores únicos:")
    print(df_resultado[col].value_counts())


### 🧪 Ejemplo: Subplots de análisis múltiple

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Crear figura con 2 filas y 2 columnas
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Distribución de Precio", "Boxplot por Categoría",
                    "Valoración por Marca", "Precio vs. Valoración"),
    vertical_spacing=0.2
)
# Histograma de Marcas
fig.add_trace(
    go.Histogram(x=df['marca'], nbinsx=30, name='Hist Precio'),
    row=1, col=1
)


# Boxplot Precio por Categoría
fig.add_trace(
    go.Box(x=df['marca'], y=df['Precio'], name='Boxplot'),
    row=1, col=2
)


# Gráfico de barras: Valoración media por Marca
media_valoracion = df.groupby('marca_confianza')['Precio'].mean().reset_index()
fig.add_trace(
    go.Bar(x=media_valoracion['marca_confianza'], y=media_valoracion['marca_confianza'], name='Precio'),
    row=2, col=1
)

# Scatter Precio vs Valoración
fig.add_trace(
    go.Scatter(
        x=df['marca'],
        y=df['Precio'],
        mode='markers',
        marker=dict(size=6, color='orange'),
        name='Scatter'
    ),
    row=2, col=2
)

# Layout general
fig.update_layout(
    height=800,
    width=1000,
    title_text="📊 Análisis gráfico del dataset",
    showlegend=False,
    template='plotly_dark'
)

fig.show()

import plotly.express as px

# Precio medio por categoría
df_grouped = df.groupby('marca_categoria')['Precio'].mean().reset_index()

# Gráfico de barras
fig = px.bar(df_grouped, x='marca_categoria', y='Precio',
             title='💸 Precio medio por categoría',
             labels={'Precio': 'Precio medio (EUR)', 'Categorías': 'Categoría'},
             color='Precio',
             template='plotly_white')

fig.update_layout(xaxis_tickangle=-45)
fig.show()

df.head(5)

df_resultado.to_csv(r"F:\00Proyecto_final\Datos\resultado.csv", index=False)
