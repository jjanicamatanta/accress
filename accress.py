import pandas as pd
from flask import Flask, jsonify, request
import mysql.connector
import os
import time
import json
# db03
import requests
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.support.ui import Select

import functions as helper

app = Flask(__name__)

# DB1
@app.route('/db1')
def pea():
    conexion = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='',
        database='ubigeo'
    )
    departamento = request.args.get('departamento', default=None, type=str)
    if departamento is None:
        return jsonify({
            "message":"Ingrese departamento"
        })
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM db01 where code = '"+departamento+"'")

    resultados = cursor.fetchall()
    
    if len(resultados) == 0:
        return jsonify({
            "message":"Ese departamento no tiene resulados"
        })
    else:
        return jsonify({
            "departamento":resultados[0]["departamento"],
            "pea_ocupada": resultados[0]["pea_ocupada"], 
            "pea_desocupada": resultados[0]["pea_desocupada"],
            "no_pea":resultados[0]["no_pea"]
        })

@app.route('/db1/upload', methods=['POST'])
def pea_upload():
    conexion = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='',
        database='ubigeo'
    )
    if request.method == 'POST':
        cursor = conexion.cursor()
        f = request.files['file']
        filepath = os.path.join(f.filename)
        f.save(filepath)
        df = pd.read_excel(filepath)
        # pea = df.iloc[8,1]
        # title = df.columns[0]
        departamento = df.iloc[3,0]
        codigo = departamento.split()[-1]
        pea_ocupada = df.iloc[13,1]
        pea_desocupada = df.iloc[18,1]
        no_pea = df.iloc[23,1]

        query = "INSERT INTO db01 (code, departamento, pea_ocupada, pea_desocupada, no_pea) VALUES (%s, %s, %s, %s, %s)"
        valores = (codigo, departamento, pea_ocupada, pea_desocupada, no_pea)
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        data = {
            "message":"Archivo subido exitosamente",
            "data": {
                "departamento":departamento,
                "pea_ocupada": pea_ocupada, 
                "pea_desocupada": pea_desocupada,
                "no_pea":no_pea
            }
        }
        return jsonify(data)
    
    return 'Método no permitido'
# END DB1

# DB2 (TODO: accesso a google drive) 
# END DB2

# DB3 (TODO: Problemas golpeando al endpoint, retorna error 500)
@app.route('/db3')
def db3():
    distrito = request.args.get('distrito', default="Huancavelica, Huancavelica, distrito: Pilchaca", type=int)
    if distrito is None:
        return jsonify({
            "message":"Ingrese distrito"
        })
    
    driver = webdriver.Chrome()

    driver.get('https://censos2017.inei.gob.pe/bininei2/RpWebStats.exe/CrossTab?BASE=CPV2017&ITEM=CRUZCOMBI&lang=esp')

    # Quitar seleccion
    helper.getElementByPath(driver, '/html/body/div[2]/div[4]/form/div[2]/div[1]/div[1]/span').click()
    helper.getElementByPath(driver, "//li[contains(text(), 'P5a+: La semana pasada, según fué su seccion, ¿A que actividad se dedicó el nego')]").click()

    # Desplegar Nivel de Manzana
    helper.getElementByPath(driver, "/html/body/div[2]/div[4]/form/div[2]/div[3]/div[1]/span").click()
    helper.getElementByPath(driver, "//li[contains(text(), 'Distrito')]").click()
    
    # Desplegar distrito
    helper.getElementByPath(driver, "/html/body/div[2]/div[4]/form/div[3]/div[1]/div[1]/div[1]/span").click()
    helper.getElementByPath(driver, "//li[contains(text(), '"+distrito+"')]").click()
    
    # Submit
    helper.getElementByPath(driver, "/html/body/div[2]/div[4]/form/div[4]/input[1]").click()

    filas = helper.getElementByPath(driver, "/html/body/div[2]/div[3]/div/div[1]/div/div/div[1]/table").find_elements(By.TAG_NAME, "tr")[10:20]

    datos_filas = []
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        datos_fila = [
            helper.convert_to_slug(celda.text) if index == 1 else celda.text 
            for index, celda in enumerate(celdas)
        ]
        datos_filas.append(datos_fila)

    return jsonify(datos_filas)
  
# END DB3

# DB4 (TODO: Error al leer <canvas>: la imagen no se puede leer)
@app.route('/db4')
def db4():
    distrito = request.args.get('distrito', default="0305010003-CHAHUARQUI", type=int)
    if distrito is None:
        return jsonify({
            "message":"Ingrese distrito"
        })
    # print(distrito)
    # return ""
    driver = webdriver.Chrome()

    driver.get('https://public.tableau.com/views/ReporteCCPPBC/ReporteCCPP?:showVizHome=n')

    # ================== FIND DATA ============================

    # Open district select (Click)
    # helper.getElementByPath(driver,'/html/body/div[2]/div[4]/form/div[2]/div[1]/div/span/span[1]/span/ul/li[1]/span').click()
    helper.getElementByPath(driver,'/html/body/div[2]/div[2]/div[1]/div[1]/div/div[2]/div[25]/div/div/div/div/div/div/div[3]/span').click()

    # Click in district
    helper.getElementByPath(driver,f"//*[@title='{distrito}']").click()

    # ================== GET DATA ============================

    # Find text in div (container)
    container_elements = helper.getElementByPath(driver,f"/html/body/div[2]/div[2]/div[1]/div[1]/div/div[2]/div[33]/div/div/div/div[1]/div[5]/div[3]/div/div").text.splitlines()

    # Find numbers: Screenshot to <canvas>
    helper.getElementByPath(driver,f"/html/body/div[2]/div[2]/div[1]/div[1]/div/div[2]/div[33]/div/div/div/div[1]/div[11]/div[1]/div[2]/canvas[2]").screenshot("image.png")

    # ================== FORMAT DATA ============================

    data_formatted = []
    
    lines = helper.imageToStringArray("./image.png")
    for index, element in enumerate(container_elements):

        data_formatted.append([
            helper.convert_to_slug(element), 
            lines[index][1]  if 0 <= index < len(lines) else ""
        ])
    
    driver.close()

    return jsonify(data_formatted)
# END DB4

# DB5
@app.route('/db5')
def db5():
    departamento = request.args.get('departamento', default="01")
    provincia = request.args.get('provincia', default="02")
    distrito = request.args.get('distrito', default="02")
    if distrito is None:
        return jsonify({
            "message":"Ingrese distrito"
        })
    
    url = 'http://app20.susalud.gob.pe:8080/registro-renipress-webapp/listadoEstablecimientosRegistrados.htm?action=cargarEstablecimientos&txt_filtrar=&cmb_estado=1&cmb_departamento='+departamento+'&cmb_provincia='+provincia+'&cmb_distrito='+distrito+'&cmb_institucion=0&cmb_tipo_establecimiento=0&cmb_clasificacion=0&cmb_categoria=0&cmb_unidadEjecutora=0&cmb_servicio=0&cmb_autoridadSanitaria=0&cmb_red=0&cmb_microRed=0&cmb_clas=0&cmb_colegio=0&cmb_especialidad=0&cmb_quintil=0&cmb_telesalud=0&dat_fd_quintil=&ra_reg=on&dat_fd_desde=&dat_fd_hasta='
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.text.replace("\"draw\":,", "\"draw\":\"\",")
        data = json.loads(data)
        return jsonify(data)
    else:
        print("Error en la solicitud:", response.status_code)
 
# END DB5

if __name__ == '__main__':
    app.run(debug=True)


   