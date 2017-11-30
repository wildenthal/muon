﻿import visa
from time import strftime,sleep
import numpy as np
import time
import sys
import os
from interpol import threshold
from escalafunc import escalafunc

#El programa debe ser llamado de la siguiente manera:
# >>python3 barridolargo.py rateminimo ratemaximo nropuntos tiempoporpunto repeticiones (
#donde el tiempo esta medido en segundos
#rate debe ser mayor que 22

rm = visa.ResourceManager('@py')
osci = rm.open_resource(rm.list_resources()[0],read_termination='\n')

#Parametros de nuestra medicion
nropuntos = int(sys.argv[3])
ratelist = np.linspace(float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]))
tiempomedicion = float(sys.argv[4]) #Cuanto tiempo quiero barrer cada threshold
repeticiones = int(sys.argv[5])

#File management
os.chdir(os.path.dirname(os.path.abspath(__file__))) 
pathname = "../datos_temp/"+time.strftime("%d%b")+"/"
if not(os.path.isdir(pathname)):
    os.mkdir(pathname) 
nombrecarpeta = pathname + "coincidencias"+time.strftime("%y.%m.%d_%H.%M")+"/"
if not(os.path.isdir(nombrecarpeta)):
    os.mkdir(nombrecarpeta)
nombrearchivo = "coincidencias.pines_5_9.volt_850_852.seg_{}.".format(tiempomedicion)

#Imprime rates para chequear que esté todo bien
ratestring = ', '.join(map(str,ratelist.tolist()))
print('Rates a barrer: ' + ratestring)

#Crea csv para guardar
matrizdedatos = np.transpose([ratelist,np.zeros(nropuntos)])

#Hace el barrido
for j in range(repeticiones):
    for index,rate in enumerate(ratelist):
        threshold1, threshold2 = threshold(rate)
        escala1 = escalafunc(threshold1)
        escala2 = escalafunc(threshold2)
        osci.write('ch1:scale {}; :ch2:scale {}'.format(escala1,escala2))
        osci.write('TRIGger:A:SETHold:CLOCk:THReshold {}'.format(threshold1))
        osci.write('TRIGger:A:SETHold:DATa:THReshold {}'.format(threshold2))
        print('Estamos configurando la siguiente medición. Por favor espere...')
        sleep(1)
        muonesIniciales = int(osci.query('ACQuire:NUMACq?'))
        print('{} eventos iniciales'.format(muonesIniciales))
        print('Para el rate {} seteamos los thresholds en {}mV para el canal 1 y {}mV para el 2'.format(rate,int(threshold1*-1000),int(threshold2*-1000)))
        sleep(tiempomedicion)
        nromuones = int(osci.query('ACQuire:NUMACq?')) - muonesIniciales
        matrizdedatos[index][1] = nromuones
        print(str(nromuones) + ' coincidencias')
    np.savetxt(nombrecarpeta + nombrearchivo + strftime("%y_%m_%d.%H_%M_%s") + '.csv',matrizdedatos,delimiter=',')
osci.close()
