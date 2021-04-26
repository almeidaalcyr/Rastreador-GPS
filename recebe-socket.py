#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 14:50:10 2021

@author: alcyr
"""


import socket
import sys
import time
from datetime import datetime
import re

host = ''
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8",80))
host = s.getsockname()[0]
s.close()

porta = 9000
tamanhoDaString = 100
servidor = (host, porta)

def formata_dados(byte):
    '''
    

    Parameters
    ----------
    byte : BYTE
        Dados NMEA em formato BYTE.

    Returns
    -------
    NMEA : DICT
        Dados NMEA.
    '''
    
    NMEA = str(byte.decode('utf-8'))
    valido = checksum(NMEA)
    
    if valido:
        NMEA = NMEA.split(",")
        NMEA = {
                "formato": NMEA[0],
                "tempo": NMEA[1], # HHMMSS (UTC)
                "status": NMEA[2], # A = OK, V = warning
                "latitude": NMEA[3],
                "latitude_NS": NMEA[4],
                "longitude": NMEA[5],
                "longitude_EW": NMEA[6],
                "velocidade_solo": NMEA[7], #SMG: Velocidade "à proa" - em knots
                "velocidade_curso": NMEA[8], #CMG: Velocidade (com o drift) - em knots
                "data": NMEA[9], #DDMMAA
                "mag_delta": NMEA[10],
                "mag_delta_NSEW": NMEA[11][0],
                "checksum": valido
                }
        return NMEA
    
    else:
        return None

def checksum(nmea):
    if re.search("$", nmea):
        nmea = nmea.split('$')[-1]

    nmea, checksum = nmea.split('*')

    calc_checksum = 0
    for i in nmea:
        calc_checksum ^= ord(i)

    checksum = "0x"+checksum
    calc_checksum = str(hex(calc_checksum))

    if checksum == calc_checksum:
        return True
    else:
        return False
    
def calcula_latitude(NMEA):
    '''
    Calcula a latitude a partir dos dados no NMEA

    Parameters
    ----------
    NMEA : DICT
        Dados NMEA organizados em um dicionário.

    Returns
    -------
    resultado : FLOAT
        Latitude em graus.
    '''
    
    inicial = int(NMEA["latitude"][:2])
    final = float(NMEA["latitude_NS"][2:])/60
    resultado = inicial + final
    if latitude_NS == 'S':
        resultado = -resultado
    return resultado

def calcula_longitude(NMEA):
    '''
    Calcula a longitude a partir dos dados no NMEA

    Parameters
    ----------
    NMEA : DICT
        Dados NMEA organizados em um dicionário.

    Returns
    -------
    resultado : FLOAT
        Longitude em graus.
    '''
    
    inicial = int(NMEA["longitude"][:3])
    final = float(NMEA["longitude_EW"][3:])/60
    resultado = inicial + final
    if longitude_EW == 'S':
        resultado = -resultado
    return resultado
    
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('servidor {} iniciado na porta {}'.format(*servidor))
tcp.bind(servidor)

while(True):
    tcp.listen(1)
    print('Aguardando o cliente')
    conexao, cliente = tcp.accept()
    
    try:
        print('Conectado com', cliente[0])
        byte = conexao.recv(tamanhoDaString)
        NMEA = formata_dados(byte)
        
        #dado = str.encode(dado)
            
        print('Enviando resposta ao cliente... ')
        if byte:
            conexao.sendall(byte)
        else:
            print('Fim da resposta', cliente)
            break
    
    finally:
        conexao.close()
        del conexao
        print('Finalizado')
