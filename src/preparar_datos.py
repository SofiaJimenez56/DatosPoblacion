"""
preparar_datos.py
-----------------
Pipeline de preparación de datos del INEGI (ENTI 2022) para el análisis
de la relación entre trabajo infantil en el hogar y las condiciones de
la vivienda y la escolaridad del jefe.

Integra las bases de Hogar y Vivienda, selecciona las variables relevantes,
las renombra con nombres legibles, limpia códigos especiales y valores
faltantes, y genera la variable objetivo binaria `tiene_trabajo_infantil`.

Uso:
    python src/preparar_datos.py
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

RUTA_HOG = os.path.join(RAW_DIR, 'conjunto_de_datos_hog_enti_2022.csv')
RUTA_VIV = os.path.join(RAW_DIR, 'conjunto_de_datos_viv_enti_2022.csv')
RUTA_SALIDA = os.path.join(PROCESSED_DIR, 'inegi_procesado.csv')


# Constantes del proyecto
LLAVES = ['ent', 'con', 'upm', 'n_pro_viv', 'v_sel', 'per']

COLUMNAS_RELEVANTES = [
    # Llaves compartidas
    'ent', 'con', 'upm', 'n_pro_viv', 'v_sel', 'per',
    # De Hogar
    'tcti', 'tonp', 'tocup', 'tqdna', 'con5a17',
    'escol_jefe', 'cs_p13_2', 'sex_jef', 'clase_hog',
    'tam_hog', 'p_tot', 'clase2_jef',
    # De Vivienda
    'p21', 'p22', 'p23', 'p24', 'p25', 'p26', 'p28', 'p31',
    'p32_1', 'p32_2', 'p32_9', 'p32_12',
    'tot_hog', 'pobviv', 'ur2',
]

MAPA_COLUMNAS = {
    # Llaves
    'ent': 'entidad',
    'con': 'control',
    'upm': 'upm',
    'n_pro_viv': 'num_vivienda',
    'v_sel': 'vivienda_sel',
    'per': 'periodo',
    # Hogar
    'tcti': 'trabajo_infantil_total',
    'tonp': 'menores_ocupacion_no_permitida',
    'tocup': 'menores_ocupados_5a17',
    'tqdna': 'menores_quehaceres_no_adecuados',
    'con5a17': 'poblacion_5a17',
    'escol_jefe': 'escolaridad_jefe',
    'cs_p13_2': 'anios_aprobados_jefe',
    'sex_jef': 'sexo_jefe',
    'clase_hog': 'clase_hogar',
    'tam_hog': 'tamano_hogar',
    'p_tot': 'total_residentes',
    'clase2_jef': 'actividad_jefe',
    # Vivienda
    'p21': 'material_piso',
    'p22': 'cuartos_dormir',
    'p23': 'cuartos_totales',
    'p24': 'luz_electrica',
    'p25': 'agua_entubada',
    'p26': 'origen_agua',
    'p28': 'sanitario',
    'p31': 'drenaje',
    'p32_1': 'refrigerador',
    'p32_2': 'lavadora',
    'p32_9': 'computadora',
    'p32_12': 'internet',
    'tot_hog': 'hogares_en_vivienda',
    'pobviv': 'poblacion_vivienda',
    'ur2': 'ambito',
}

COLUMNAS_LLAVE_TEXTO = [
    'entidad', 'control', 'upm', 'num_vivienda', 'vivienda_sel', 'periodo'
]

COLUMNAS_NUMERICAS = [c for c in MAPA_COLUMNAS.values() if c not in COLUMNAS_LLAVE_TEXTO]

VARS_VIVIENDA_CLAVE = [
    'material_piso', 'cuartos_dormir', 'cuartos_totales',
    'luz_electrica', 'agua_entubada', 'sanitario', 'drenaje',
]

MAPA_ENTIDADES = {
    '01': 'Aguascalientes', '02': 'Baja California', '03': 'Baja California Sur',
    '04': 'Campeche', '05': 'Coahuila', '06': 'Colima', '07': 'Chiapas',
    '08': 'Chihuahua', '09': 'Ciudad de México', '10': 'Durango',
    '11': 'Guanajuato', '12': 'Guerrero', '13': 'Hidalgo', '14': 'Jalisco',
    '15': 'Estado de México', '16': 'Michoacán', '17': 'Morelos',
    '18': 'Nayarit', '19': 'Nuevo León', '20': 'Oaxaca', '21': 'Puebla',
    '22': 'Querétaro', '23': 'Quintana Roo', '24': 'San Luis Potosí',
    '25': 'Sinaloa', '26': 'Sonora', '27': 'Tabasco', '28': 'Tamaulipas',
    '29': 'Tlaxcala', '30': 'Veracruz', '31': 'Yucatán', '32': 'Zacatecas',
}

CODIGO_NO_ESPECIFICADO = 9
VALOR_NO_APLICA = -1


# Funciones del pipeline
def cargar_crudos():
    """Carga las bases crudas de Hogar y Vivienda como texto."""
    df_hog = pd.read_csv(RUTA_HOG, dtype=str, encoding='utf-8')
    df_viv = pd.read_csv(RUTA_VIV, dtype=str, encoding='utf-8')
    print(f"  Hogar: {df_hog.shape}")
    print(f"  Vivienda: {df_viv.shape}")
    return df_hog, df_viv


def integrar(df_hog, df_viv):
    """Hace el merge por las llaves compartidas."""
    df = pd.merge(df_hog, df_viv, on=LLAVES, how='inner', suffixes=('_hog', '_viv'))
    print(f"  Integrado: {df.shape}")
    return df


def seleccionar_columnas(df):
    """Selecciona solo las columnas relevantes para el análisis."""
    faltantes = [c for c in COLUMNAS_RELEVANTES if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes en el merge: {faltantes}")
    return df[COLUMNAS_RELEVANTES].copy()


def renombrar_columnas(df):
    """Renombra los nemónicos por nombres descriptivos."""
    return df.rename(columns=MAPA_COLUMNAS)


def convertir_tipos(df):
    """Convierte variables a sus tipos correctos."""
    # Llaves como texto
    for col in COLUMNAS_LLAVE_TEXTO:
        df[col] = df[col].astype(str).str.zfill(len(df[col].iloc[0]))
    
    # Numéricas: primero vacío -> NaN, luego a número
    for col in COLUMNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def tratar_codigos_especiales(df):
    """Reemplaza el código 9 (No especificado) por NaN."""
    columnas_binarias = [
        'luz_electrica', 'agua_entubada', 'sanitario', 'drenaje',
        'refrigerador', 'lavadora', 'computadora', 'internet',
    ]
    for col in columnas_binarias:
        df[col] = df[col].replace(CODIGO_NO_ESPECIFICADO, pd.NA)
    
    df['material_piso'] = df['material_piso'].replace(CODIGO_NO_ESPECIFICADO, pd.NA)
    df['escolaridad_jefe'] = df['escolaridad_jefe'].replace(CODIGO_NO_ESPECIFICADO, pd.NA)
    df['origen_agua'] = df['origen_agua'].replace(CODIGO_NO_ESPECIFICADO, pd.NA)
    return df


def eliminar_viviendas_incompletas(df):
    """Elimina hogares sin datos de vivienda (cuestionario no aplicado)."""
    antes = len(df)
    df = df.dropna(subset=VARS_VIVIENDA_CLAVE).reset_index(drop=True)
    eliminadas = antes - len(df)
    print(f"  Hogares eliminados por vivienda incompleta: {eliminadas}")
    return df


def imputar_origen_agua(df):
    """Marca los casos de origen_agua no aplicables (sin agua entubada)."""
    df['origen_agua'] = df['origen_agua'].fillna(VALOR_NO_APLICA).astype(int)
    return df


def crear_variable_objetivo(df):
    """Crea la variable binaria de trabajo infantil."""
    df['tiene_trabajo_infantil'] = (df['trabajo_infantil_total'] > 0).astype(int)
    return df


def agregar_nombre_entidad(df):
    """Agrega la columna con el nombre de la entidad federativa."""
    df['entidad_nombre'] = df['entidad'].map(MAPA_ENTIDADES)
    return df


def guardar(df):
    """Guarda el dataset procesado."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False)
    print(f"  Guardado: {RUTA_SALIDA}")
    print(f"  Shape final: {df.shape}")



def main():
    print("=== Pipeline de preparación de datos ENTI 2022 ===")

    print("\n[1/9] Cargando datos crudos...")
    df_hog, df_viv = cargar_crudos()

    print("\n[2/9] Integrando bases...")
    df = integrar(df_hog, df_viv)

    print("\n[3/9] Seleccionando columnas relevantes...")
    df = seleccionar_columnas(df)

    print("\n[4/9] Renombrando columnas...")
    df = renombrar_columnas(df)

    print("\n[5/9] Convirtiendo tipos...")
    df = convertir_tipos(df)

    print("\n[6/9] Tratando códigos especiales...")
    df = tratar_codigos_especiales(df)

    print("\n[7/9] Eliminando viviendas incompletas...")
    df = eliminar_viviendas_incompletas(df)

    print("\n[8/9] Imputando origen_agua y creando variable objetivo...")
    df = imputar_origen_agua(df)
    df = crear_variable_objetivo(df)
    df = agregar_nombre_entidad(df)

    print("\n[9/9] Guardando dataset procesado...")
    guardar(df)

    print("\n=== Pipeline completado ===")


if __name__ == '__main__':
    main()