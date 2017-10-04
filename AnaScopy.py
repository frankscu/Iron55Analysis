import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import optimize

def csv_reader(fileName):
    with open(fileName) as incsvfile:
        htimes=[]
        hamps=[]
        readCSV=csv.reader(incsvfile,delimiter=',')
        next(readCSV)
        for row in readCSV:
            print(row)
            time    = row[0]
            amp    = row[1]

            htimes.append(time)
            hamps.append(amp)

    return htimes, hamps

def readData(situation):
    ################## load the excel file ##################
    fileName = '../OverMOS_1_1/'+situation+'.csv'
    print("Processing File: ",fileName)

    times,amps=csv_reader(fileName)

    data_list=[times,amps]

    dataArray = np.array(data_list)
    return dataArray

def drawPlot(situation, marker, bias_voltage, dataArray):

    times=1e3*dataArray[0,4:].astype('float')
    amps=dataArray[1,4:].astype('float')

    f1=plt.figure(1,figsize=(10,7.5))

    plt.plot(times,amps,label=situation)
    #plt.yscale('log')
    plt.xlabel('Time [ms]',fontsize=24)
    plt.ylabel('Voltages [V]',fontsize=24)
    plt.ylim((-6,4))
    plt.grid()

    f2=plt.figure(2,figsize=(10,7.5))

    plt.plot(times,amps,label=bias_voltage)
    #plt.yscale('log')
    plt.xlabel('Time [ms]',fontsize=24)
    plt.ylabel('Voltages [V]',fontsize=24)
    plt.ylim((-6,4))
    plt.grid()


################## Main Function #################
markerList=['*','*-','*-.', \
            '.','.-','.-.', \
            'v','v-','v-.', \
            '^','^-','^-.', \
            '+','+-','+-.', \
            'o','o-','o-.']
#situationList=["C1dif-meas00000","C2dif-meas00000","C2dif-meas00001","C2dif-meas00002", \
#               "C2dif-meas00003","C2dif-meas00004","C2dif-meas00005","C2dif-meas00006", \
#               "C2dif-meas00007","C2dif-meas00008"]
#
#bias_voltageList=["LED_Bias_0 V","Pixel4_Bias_0 V","Pixel4_Bias_0.5 V",\
#                  "Pixel4_Bias 1.0 V","Pixel4_Bias_1.5 V","Pixel4_Bias_2.0 V",\
#                  "Pixel4_Bias_2.5 V","Pixel4_Bias_3.0 V","Pixel4_Bias_4.0 V",\
#                  "Pixel4_Bias_5.0 V"]


situationList=["C2dif-meas00009","C2dif-meas00010","C2dif-meas00011", \
               "C2dif-meas00012","C2dif-meas00013","C2dif-meas00013","C2dif-meas00014"]

bias_voltageList=["Pixel4_Bias_0 V","Pixel4_Bias_0.5 V","Pixel4_Bias 1.0 V",\
                  "Pixel4_Bias_1.5 V","Pixel4_Bias_2.0 V",\
                  "Pixel4_Bias_3.0 V","Pixel4_Bias_4.0 V"]

fPdf = PdfPages('passive.pdf')
for i in range(0,7):
    data = readData(situationList[i])
    drawPlot(situationList[i],markerList[i],bias_voltageList[i],data)
    print('')

f1=plt.figure(1,figsize=(10,7.5))
plt.legend(prop={'size':15})
f1.show()
fPdf.savefig()

f2=plt.figure(2,figsize=(10,7.5))
plt.legend(prop={'size':15})
f2.show()
fPdf.savefig()

fPdf.close()
input("Press Enter to continue...")
