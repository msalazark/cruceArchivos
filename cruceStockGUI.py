# This is a sample Python script.
import pandas as pd
from datetime import datetime
from pandasql import sqldf
import os
import argparse
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

fecha = datetime.now().strftime('%Y-%m-%d')
fechaStock = datetime.now().strftime('%Y%m%d')


def buscar_archivo(directorio, fecha):
    listado = os.listdir(directorio)
    for archivo in listado:
        if fecha in archivo and 'csv' in archivo:
            print(directorio + archivo)
            df = pd.read_csv(directorio + archivo, sep=',', error_bad_lines = False, low_memory=False)
        else:
            df = pd.DataFrame()
        return df


def cargaArchivoStock(archivo1):
    dtypes = {"source_code": str,
              "sku": str,
              "status": str,
              "quantity": int
              }
    stock = pd.read_csv(archivo1, sep=",", dtype=dtypes)
    return stock


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


def select_file_nuevo():
    filetypes = (
        ('text files', '*.txt'),
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )

    archivoStockNuevo = fd.askopenfilename(
        title='Abrir archivo de stock a cargar',
        initialdir='/',
        filetypes=filetypes)

    print(archivoStockNuevo)
    label_file_explorer_nuevo.configure(text=archivoStockNuevo)

def select_file_actual():
    filetypes = (
        ('text files', '*.txt'),
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    )
    archivoStockActual = fd.askopenfilename(
        title='Abrir archivo de stock a actual',
        initialdir='/',
        filetypes=filetypes)
    print(archivoStockActual)
    label_file_explorer_actual.configure(text=archivoStockActual)

def open_text_file():
    # file type
    filetypes = (
        ('text files', '*.txt'),
        ('csv files', '*.csv'),
        ('All files', '*.*')
    )
    # show the open file dialog
    f = fd.askopenfile(filetypes=filetypes)
    text.insert('1.0', f.readlines())


def ejecutar_cruce():
    # print(fecha)
    # print(fechaStock)
    # print(label_file_explorer_actual['text'])
    # print(label_file_explorer_nuevo['text'])
    log = ""
    varchivoStockActual = label_file_explorer_actual['text']
    varchivoStockNuevo = label_file_explorer_nuevo['text']
    # print(varchivoStockActual)
    # print(varchivoStockNuevo)

    log = log + "Cargando stock actual" + "\n"
    label_file_explorer_proceso.configure(text=log)
    stockActual = cargaArchivoStock(varchivoStockActual)
    log = log + str(stockActual.shape[0]) + " registros " + "\n"
    label_file_explorer_proceso.configure(text=log)
    # print(stockActual.shape)
    log = log + "Cargando nuevo stock" + "\n"
    label_file_explorer_proceso.configure(text=log)
    stockNuevo = cargaArchivoStock(varchivoStockNuevo)
    log = log + str(stockNuevo.shape[0]) + " registros " + "\n"
    label_file_explorer_proceso.configure(text=log)

    # print(stockNuevo.shape)
    query = "SELECT stockNuevo.* \
            FROM stockNuevo \
            INNER JOIN stockActual \
            ON stockActual.sku = stockNuevo.sku \
            WHERE stockActual.source_code = stockNuevo.source_code \
            AND stockActual.quantity <> stockNuevo.quantity \
            "
    # print(query)
    log = log + "Realizando cruce" + "\n"
    label_file_explorer_proceso.configure(text=log)
    pre_final = sqldf(query)
    log = log + str(pre_final.shape[0]) + " registros a exportar" + "\n"
    label_file_explorer_proceso.configure(text=log)
    # print(pre_final.shape)

    exportar(pre_final)
    log = log + "Archivos exportados" + "\n"
    label_file_explorer_proceso.configure(text=log)


if __name__ == '__main__':
    # create the root window
    root = Tk()
    root.title('Seleccionar archivos de stock')
    root.resizable(False, False)
    root.minsize(500, 250)  # width, height
    root.maxsize(800, 400)
    root.geometry('500x250+50+50')

    # Create a File Explorer label
    label_file_explorer_actual = Label(root,
                                text="Archivo actual",
                                fg="blue")

    label_file_explorer_nuevo = Label(root,
                               text="Archivo Nuevo",
                               fg="blue")

    label_file_explorer_proceso = Label(root,
                               text="",
                               fg="blue")

    # open button
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
        text='Realizar Cruce',
        command=ejecutar_cruce
    )

    open_button1.grid(column=0, row=1, padx=5, pady=5)
    label_file_explorer_actual.grid(column=1, row=1, padx=5, pady=5)
    open_button2.grid(column=0, row=2, padx=5, pady=5)
    label_file_explorer_nuevo.grid(column=1, row=2, padx=5, pady=5)
    open_button3.grid(column=0, row=3, padx=5, pady=5)
    label_file_explorer_proceso.grid(column=0, row=4, columnspan=4)

    # run the application
    root.mainloop()

