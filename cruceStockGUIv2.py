# This is a sample Python script.
import tkinter
import pandas as pd
from datetime import datetime
from pandasql import sqldf
import os
import argparse
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter.messagebox import showinfo

sepGeneral = ","
sepGeneralStock = "\t" # Archivo de Chapa
fecha = datetime.now().strftime('%Y-%m-%d')
fechaStock = datetime.now().strftime('%Y%m%d')

# Recojo de catalogo
def buscar_archivo(directorio, fecha):
    listado = os.listdir(directorio)
    for archivo in listado:
        if fecha in archivo and 'csv' in archivo:
            print(directorio + archivo)
            df = pd.read_csv(directorio + archivo, sep=sepGeneral, error_bad_lines = False, low_memory=False)
        else:
            df = pd.DataFrame()
        return df

# Recojo de stock Actual
def cargaArchivoStockActual(archivo1):
    dtypes = {"source_code": str,
              "sku": str,
              "status": str,
              "StockAlm": int
              }
    stock = pd.read_csv(archivo1, sep=sepGeneral, dtype=dtypes)
    stock.rename(columns={"StockAlm": "quantity"}, inplace=True)
    return stock

# Stock nuevo
def cargaArchivoStockNuevo(archivo1):
    dtypes = {"source_code": str,
              "sku": str,
              "status": str,
              "StockAlm": int
              }
    stockNuevo = pd.read_csv(archivo1, sep=sepGeneralStock, dtype=dtypes)
    stockNuevo.rename(columns={"StockAlm": "quantity"}, inplace=True)
    return stockNuevo

# Stock nuevo EC
def cargaArchivoStockNuevoEC(archivo1):
    dtypes = {"source_code": str,
              "sku": str,
              "status": str,
              "StockAlm": int
              }
    stockNuevoEC = pd.read_csv(archivo1, sep=sepGeneral, dtype=dtypes)
    stockNuevoEC.rename(columns={"StockAlm": "quantity"}, inplace=True)
    return stockNuevoEC

def exportar(pre_final, prefijo, largoLote):
    archivo = prefijo + fecha +  ".csv"
    pre_final.to_csv(archivo, index=False)
    totalRegExport = pre_final.shape[0]
    rango_inferior = 0
    lotes = int((totalRegExport / largoLote) + 1) + 1
    print("lotes: ", str(lotes))
    for i in range(1, lotes):
        rango_inferior = rango_inferior + 1
        rango_superior = rango_inferior + (largoLote - 1)
        print("Desde ", rango_inferior, " Hasta ", rango_superior)
        carga = pre_final[rango_inferior:rango_superior]
        archivo = prefijo + fecha + "_" + str(i) + ".csv"
        print(archivo)
        carga[["source_code", "sku", "status", "quantity"]].to_csv(archivo, index=False)
        rango_inferior = rango_superior
    print("Proceso terminado")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stockActual', '-sa', help="Stock Actual", type=str)
    parser.add_argument('--stockNuevo', '-sn', help="Stock Nuevo", type=str)
    return parser.parse_args()


def select_file_nuevo():
    filetypes = (
        ('TXT files', '*.txt'),
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    archivoStockNuevo = fd.askopenfilename(
        title='Abrir archivo de stock a cargar',
        initialdir='/',
        filetypes=filetypes)

    print(archivoStockNuevo)
    label_file_explorer_nuevo.configure(text=archivoStockNuevo)


def select_file_nuevo_ec():
    filetypes = (
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    archivoStockNuevoEC = fd.askopenfilename(
        title='Abrir archivo de stock EC a cargar',
        initialdir='/',
        filetypes=filetypes )
    print(archivoStockNuevoEC)
    label_file_explorer_nuevo_ec.configure(text=archivoStockNuevoEC)


def select_file_actual():
    filetypes = (
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    archivoStockActual = fd.askopenfilename(
        title='Abrir archivo de stock a actual',
        initialdir='/',
        filetypes=filetypes)
    print(archivoStockActual)
    label_file_explorer_actual.configure(text=archivoStockActual)


def select_file_catalogo():
    filetypes = (
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    archivoCatalogo = fd.askopenfilename(
        title='Abrir archivo de stock de stock',
        initialdir='/',
        filetypes=filetypes)
    print(archivoCatalogo)
    label_file_explorer_catalogo.configure(text=archivoCatalogo)


def ejecutar_cruce_ec():
    log = ""
    varchivoStockActual = label_file_explorer_actual['text']
    varchivoStockNuevoEC = label_file_explorer_nuevo_ec['text']
    varchivoCatalogo = label_file_explorer_catalogo['text']
    text_area.insert( tkinter.INSERT, log)
    # Cargar catalago
    catalogo = pd.read_csv(varchivoCatalogo, sep=',', low_memory=False,
                           on_bad_lines="skip",
                           skip_blank_lines=True,
                           encoding='utf-8',
                           encoding_errors='ignore')
    print("Catalogo: ", catalogo.shape)
    bar["value"] = 5

    stockActual = cargaArchivoStockActual(varchivoStockActual)
    print("Stock Actual: ", stockActual.shape)
    bar["value"] = 10

    stock = cargaArchivoStockNuevoEC(varchivoStockNuevoEC)
    print("Stock a cargar EC:", stock.shape)
    bar["value"] = 20

    # Los que están en la tienda EC
    query = """
            SELECT stock.* \
            FROM stock \
            INNER JOIN catalogo \
            ON stock.sku = catalogo.sku  \
            WHERE stock.sku NOT LIKE 'D%'
            """
    stockEC = sqldf(query)
    print("Stock EC Nuevo en Catálogo: ", stockEC.shape)
    bar["value"] = 30

    # Stock Demanda
    query = """
            SELECT stock.* \
            FROM stock  \
            INNER JOIN catalogo \
            ON stock.sku = catalogo.sku \
            WHERE catalogo.categories LIKE '%Default Category/LIBROS A PEDIDO%' \
            AND stock.sku LIKE 'D%' 
            """
    stockECDemanda = sqldf(query)
    print("Stock Demanda Actual :",  stockECDemanda.shape)
    bar["value"] = 40


    query = """
            SELECT stockEC.*  \
            FROM stockEC \
            LEFT OUTER JOIN stockECDemanda \
            ON stockEC.sku = stockECDemanda.sku \
            WHERE stockECDemanda.sku IS NULL \
            AND stockEC.sku NOT LIKE 'D%'
            """
    stockECFinal = sqldf(query)
    print("Stock EC Sin demanda ", stockECFinal.shape)  # Stock sin demanda

    # Stock Actual
    stockActual601 = stockActual[ (stockActual["source_code"] == "601" ) & ( stockActual["sku"].str[0] != "D" )]
    print("Stock Actual EC :", stockActual601.shape)
    bar["value"] = 50

    print("********  Cruce Cargar ********")

    # Los que están en Stock Actual y están en Stock -
    query = """
            SELECT stockECFinal.* \
            FROM stockECFinal \
            INNER JOIN stockActual601 \
            ON ( stockActual601.sku = stockECFinal.sku AND stockActual601.source_code = stockECFinal.source_code ) \
            WHERE stockActual601.quantity <> stockECFinal.quantity 
            """
    stockECActualizar = sqldf(query)
    print("Stock a actualizar: ", stockECActualizar.shape)
    #stockECActualizar.drop(columns={"level_0", "index"}, inplace=True)
    bar["value"] = 60

    # Los que están en Stock Nuevo y no están en Stock Actual -
    query = """
            SELECT stockECFinal.* \
            FROM stockECFinal \
            LEFT OUTER JOIN stockActual601 \
            ON ( stockActual601.sku = stockECFinal.sku AND stockActual601.source_code = stockECFinal.source_code ) \
            WHERE stockActual601.sku IS NULL \
            """
    stockECNuevo = sqldf(query)
    print("Stock nuevo a cargar ", stockECNuevo.shape)
    # stockECActualizar.drop(columns={"level_0", "index"}, inplace=True)
    bar["value"] = 70

    # Los que están en Stock Actual con stock y no están en Stock EC - APAGAR
    query = """
            SELECT stockActual601.*  \
            FROM stockActual601 \
            LEFT OUTER JOIN stockECFinal \
            ON ( stockActual601.sku = stockECFinal.sku AND stockActual601.source_code = stockECFinal.source_code ) \
            WHERE stockECFinal.sku IS NULL  \
            AND stockActual601.quantity > 0 \
            """
    stockECApagar = sqldf(query)
    print("Stock a apagar: ", stockECApagar.shape)
    bar["value"] = 80

    stockECApagar["status"] = 0
    stockECApagar["quantity"] = 0

    print("********  Merge  ********")
    finalEC = pd.concat( [ stockECActualizar, stockECNuevo, stockECApagar] ).drop_duplicates()
    print("Registros a cargar ", finalEC.shape)
    bar["value"] = 90

    print("********  Exportar  ********")
    exportar(finalEC, "ActualizarApagarStockTienda601_", 5000)
    bar["value"] = 100

def ejecutar_cruce():
    log = ""
    varchivoStockActual = label_file_explorer_actual['text']
    varchivoStockNuevo = label_file_explorer_nuevo['text']
    varchivoCatalogo = label_file_explorer_catalogo['text']
    bar["value"] = 20
    print(varchivoStockActual)
    print(varchivoStockNuevo)

    # Cargar catalago
    catalogo = pd.read_csv(varchivoCatalogo, sep=',', low_memory=False,
                           on_bad_lines="skip",
                           skip_blank_lines=True,
                           encoding='utf-8',
                           encoding_errors='ignore')
    print(catalogo.shape)

    log = log + "Cargando stock actual" + "\n"
    label_file_explorer_proceso.configure(text=log)
    stockActual = cargaArchivoStockActual(varchivoStockActual)
    print(stockActual.shape)
    bar["value"] = 30

    stockNuevo = cargaArchivoStockNuevo(varchivoStockNuevo)
    log = log + str(stockNuevo.shape[0]) + " registros " + "\n"
    text_area.insert( tkinter.INSERT, log)
    print(stockNuevo.shape)
    bar["value"] = 40

    # print(stockNuevo.head())
    # Los que están en tiendas selecionadas y en catálogo
    query = """
    SELECT stockNuevo.* \
    FROM stockNuevo \
    INNER JOIN catalogo \
    ON stockNuevo.sku = catalogo.sku  
    """
    stockNuevoSel = sqldf(query)
    print(stockNuevoSel.shape)
    # Stock de seguridad
    '''
    for i, fila in stockNuevoSel.iterrows():
        if fila.quantity > 3:
            stockNuevoSel['status'][i] = '1'
            stockNuevoSel['quantity'][i] = fila["quantity"] - 3
        else:
            stockNuevoSel['status'][i] = '0'
            stockNuevoSel['quantity'][i] = 0
    print(str(i) + " stock de seguridad actualizado")
    '''
    # PASO 1
    print("1. Cruce Stock nuevo a cargar vs stock actual - Actualizar Stock")
    query = """
            SELECT stockNuevoSel.* \
            FROM stockNuevoSel \
            INNER JOIN stockActual \
            ON (stockActual.sku = stockNuevoSel.sku AND stockActual.source_code = stockNuevoSel.source_code) \
            WHERE stockNuevoSel.quantity <> stockActual.quantity
            """
    stockNuevoUpdate = sqldf(query)
    #stockNuevoUpdate.drop(columns={"level_0", "index"}, inplace=True)
    print("Total de coincidencias : ", stockNuevoUpdate.shape)
    bar["value"] = 60

    # PASO 2
    print("2. Los que están en stock actual y no están en el nuevo > Apagar")
    query = """
    SELECT stockActual.* \
    FROM stockActual  \
    LEFT OUTER JOIN stockNuevoSel \
    ON (stockActual.sku = stockNuevoSel.sku AND stockActual.source_code = stockNuevoSel.source_code) \
    WHERE stockNuevoSel.sku IS NULL \
    AND stockActual.quantity > 0 
    """
    stockApagar = sqldf(query)
    stockApagar["status"] = 0
    stockApagar["quantity"] = 0
    bar["value"] = 75
    print(stockApagar.shape)

    # PASO 3 - NUEVOS A CARGAR
    # Los que no están en stock, pero existen en catálogo y registros por cargar
    print("3. Nuevos a cargar")
    query = """
    SELECT stockNuevoSel.* \
    FROM stockNuevoSel  \
    LEFT OUTER JOIN stockActual \
    ON (stockActual.sku = stockNuevoSel.sku AND stockActual.source_code = stockNuevoSel.source_code) \
    WHERE stockActual.sku IS NULL
    """
    stockNuevoCargar = sqldf(query)
    #stockNuevoCargar.drop(columns={"level_0", "index"}, inplace=True)
    bar["value"] = 85
    print(stockNuevoCargar.shape)

    # 4. MIX
    print("4. Cruce")
    stockFinalSel = pd.concat([stockNuevoUpdate, stockApagar, stockNuevoCargar]).drop_duplicates()
    #stockFinalSel = stockFinalSel[stockFinalSel['source_code'] == "209"]  ## Linea temporal para solo quedarse con una tienda
    print(stockFinalSel.shape)
    bar["value"] = 95
    #stockFinalSel.drop(columns={"index"}, inplace=True)

    # 5. EXPORTAR TIENDAS
    print("5. Exportar")
    exportar(stockFinalSel, "ActualizarApagarStockTienda_", 5000)
    bar["value"] = 100

if __name__ == '__main__':
    # create the root window
    root = Tk()
    root.title('Seleccionar archivos de stock')
    root.resizable(False, False)
    #root.minsize(700, 400)  # width, height
    #root.maxsize(800, 500)
    root.geometry('810x270+50+50')

    bar = ttk.Progressbar(root, orient=HORIZONTAL, length=800)

    # Create a File Explorer label
    label_file_explorer_actual = Label(root,
                                text="Archivo actual",
                                fg="blue")

    label_file_explorer_nuevo = Label(root,
                               text="Archivo Nuevo",
                               fg="blue")

    label_file_explorer_nuevo_ec = Label(root,
                               text="Archivo Nuevo Stock EC",
                               fg="blue")

    label_file_explorer_proceso = Label(root,
                               text="",
                               fg="blue")

    label_file_explorer_catalogo = Label(root,
                               text="Archivo de Catálogo",
                               fg="blue")

    label_file_explorer_stock_ec = Label(root,
                               text="",
                               fg="blue")


    # open button
    open_buttonCat = ttk.Button(
        root,
        text='Catalogo',
        command=select_file_catalogo
    )

    open_button1 = ttk.Button(
        root,
        text='Stock Actual',
        command=select_file_actual
    )

    open_button2 = ttk.Button(
        root,
        text='Stock Nuevo',
        command=select_file_nuevo
    )

    open_button3 = ttk.Button(
        root,
        text='Stock EC',
        command=select_file_nuevo_ec
    )

    open_button4 = ttk.Button(
        root,
        text='Realizar Cruce Tiendas',
        command=ejecutar_cruce
    )

    open_button5 = ttk.Button(
        root,
        text='Realizar Cruce Ecommerce',
        command=ejecutar_cruce_ec
    )

    open_buttonCat.grid(column=0, row=2, sticky="nsew", padx=5, pady=5, columnspan=1)
    label_file_explorer_catalogo.grid(column=1, row=2, sticky="w",columnspan=4)

    open_button1.grid(column=0, row=3, sticky="nsew", padx=5, pady=5, columnspan=1)
    label_file_explorer_actual.grid(column=1, row=3, sticky="w", columnspan=4)

    open_button2.grid(column=0, row=4, sticky="nsew", padx=5, pady=5, columnspan=1)
    label_file_explorer_nuevo.grid(column=1, row=4, sticky="w", columnspan=4)

    open_button3.grid(column=0, row=5, sticky="nsew", padx=5, pady=5, columnspan=1)
    label_file_explorer_nuevo_ec.grid(column=1, row=5, sticky="w", columnspan=4)

    open_button4.grid(column=0, row=6, sticky="nsew",  padx=5, pady=5, columnspan=1)
    open_button5.grid(column=0, row=7, sticky="nsew", padx=5, pady=5, columnspan=1)
    #label_file_explorer_stock_ec.grid(column=1, row=8, sticky="w", rowspan=2, columnspan=5)

    text_area = scrolledtext.ScrolledText(root, wrap= tkinter.WORD,
                                          width=780, height=8,
                                          font=("Times New Roman", 12))


    bar.grid(column=0, row=1, sticky="nsew", padx=5, pady=5,  columnspan=5)
    # run the application
    root.mainloop()
