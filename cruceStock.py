# This is a sample Python script.
import pandas as pd
from datetime import datetime
import sqldf
import os
import argparse

# Press ⇧F10 to execute it or replace it with your code.
fecha = datetime.now().strftime('%Y-%m-%d')
fechaStock = datetime.now().strftime('%Y%m%d')
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def buscar_archivo(directorio, fecha):
    listado = os.listdir(directorio)
    for archivo in listado:
        if fecha in archivo and 'csv' in archivo:
            print(directorio + archivo)
            df = pd.read_csv(directorio + archivo, sep=',' , error_bad_lines = False, low_memory=False)
        else:
            df = pd.DataFrame()
        return df


def buscar_archivo_excel(directorio, fecha):
    listado = os.listdir(directorio)
    df = pd.DataFrame()
    for archivo in listado:
        if fecha in archivo and 'xlsx' in archivo:
            print(directorio + archivo)
            df = pd.read_excel(directorio + archivo)
            break
    return df


def cargaArchivoStock(archivo1):
    dtypes = {"source_code": str,
              "sku": str,
              "status": str,
              "quantity": int
              }
    stockActual = pd.read_csv(archivo1, sep=",", dtype=dtypes)
    return stockActual


def cruce(stockActual, stockNuevo):
    # Los que están
    query = """
    SELECT stockNuevo.*
    FROM stockNuevo 
    INNER JOIN stockActual
    ON stockActual.sku = stockNuevo.sku 
    WHERE stockActual.source_code = stockNuevo.source_code
    AND stockActual.quantity <> stockNuevo.quantity
    """
    pre_final = sqldf.run(query)
    return pre_final


def exportar(pre_final):
    totalRegExport = pre_final.shape[0]
    largoLote = 1000
    rango_inferior = 0
    lotes = int((totalRegExport / largoLote) + 1) + 1
    print("lotes: ", str(lotes))
    for i in range(1, lotes):
        rango_inferior = rango_inferior + 1
        rango_superior = rango_inferior + (largoLote - 1)
        print("Desde ", rango_inferior, " Hasta ", rango_superior)
        carga = pre_final[rango_inferior:rango_superior]
        archivo = "ActualizarStockTienda_" + fecha + "_" + str(i) + ".csv"
        print(archivo)
        carga.to_csv(archivo, index=False)
        rango_inferior = rango_superior
    print("Proceso terminado")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stockActual', '-sa', help="Stock Actual", type=str)
    parser.add_argument('--stockNuevo', '-sn', help="Stock Nuevo", type=str)
    return parser.parse_args()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    args = parse_args()
    archivoStockActual = args.stockActual
    if archivoStockActual is None:
        archivoStockActual = input("Nombre de Archivo Stock actual : ")

    archivoStockNuevo = args.stockNuevo
    if archivoStockNuevo is None:
        archivoStockNuevo = input("Nombre de Archivo Stock Nuevo : ")

    print(fecha)
    print(fechaStock)

    stockActual = cargaArchivoStock(archivoStockActual)
    stockNuevo = cargaArchivoStock(archivoStockNuevo)
    pre_final = cruce(stockActual,stockNuevo)
    print(pre_final.shape)
    exportar(pre_final)




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
