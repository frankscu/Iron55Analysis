import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import optimize
import scipy.interpolate as itp

def csv_reader(fileName):
    with open(fileName) as incsvfile:
        htimes=[]
        hamps=[]
        readCSV=csv.reader(incsvfile,delimiter=',')
        next(readCSV)
        for row in readCSV:
            #print(row)
            time    = row[0]
            amp    = row[1]

            htimes.append(time)
            hamps.append(amp)

    return htimes, hamps

def readData(situation):
    ################## load the excel file ##################
    fileName = '../OverMOSLaser/'+situation+'.csv'
    #print("Processing File: ",fileName)

    times,amps=csv_reader(fileName)

    data_list=[times,amps]

    dataArray = np.array(data_list)
    return dataArray

def minusBaseLine(dataArray,basedataArray):
    newdataArray=[]
    times=1e9*dataArray[0,4:].astype('float')
    amps=1e3*dataArray[1,4:].astype('float')
    baseamps=1e3*basedataArray[1,4:].astype('float')
    newdataArray.append(times)
    newdataArray.append(amps-baseamps)
    return newdataArray


def getRiseTime(dataArray):
    slicedataArray=[]
    slicedataArray.append(dataArray[0][200:280])
    slicedataArray.append(dataArray[1][200:280])
    idataArray=interpolate(slicedataArray)
    newtimes=idataArray[0].astype('float')
    newamps=idataArray[1].astype('float')
    ftimes= lambda v: (newtimes[(np.abs(newamps-v)).argmin()])
    riseamp = max(newamps)*1 # maximum
    risetime = ftimes(riseamp)
    return risetime, riseamp

def interpolate(dataArray):
    idataArray=[]
    newtimes=dataArray[0].astype('float')
    newamps=dataArray[1].astype('float')

    itimes=np.linspace(newtimes[0],newtimes[-1],num=int(len(newtimes)*10))
    tck=itp.splrep(newtimes,newamps,s=0)
    iamps=itp.splev(itimes,tck,der=0)
    idataArray.append(itimes)
    idataArray.append(iamps)
    return idataArray

def markerRisetime(pn,risetime,riseamp):
    f1=plt.figure(pn+1,figsize=(10,7.5))
    plt.plot([0,0],[-1000,6000],'k--',lw=2)
    plt.plot([risetime,risetime],[riseamp-500,riseamp+500],'k--',lw=2)

    #plt.plot([risetime-110,risetime+20],[riseamp,riseamp],'k--',lw=2)
    plt.annotate('',(0,riseamp),[risetime,riseamp],\
                 arrowprops={'arrowstyle':'<->'})

    plt.text(risetime-80,riseamp+40,'{:.2f} ns'.format(risetime),fontsize=15)

def drawSinglePlot(pn, situation, marker, bias_voltage, dataArray):

    times=1e9*dataArray[0,4:].astype('float')
    amps=1e3*dataArray[1,4:].astype('float')

    f1=plt.figure(pn,figsize=(10,7.5))

    plt.plot(times,amps,label=situation[0:2])
    #plt.yscale('log')
    plt.xlabel('Time [ns]',fontsize=24)
    plt.ylabel('Voltages [mV]',fontsize=24)
    plt.xlim((-50,300))
    plt.ylim((-1000,8000))
    plt.grid()

def drawPlot(pn, situation, marker, bias_voltage, dataArray, newdataArray):

    times=1e9*dataArray[0,4:].astype('float')
    amps=1e3*dataArray[1,4:].astype('float')
    newamps=newdataArray[1].astype('float')

    f1=plt.figure(pn,figsize=(10,7.5))

    plt.plot(times,amps,label=bias_voltage+" V")
    #plt.yscale('log')
    plt.xlabel('Time [ns]',fontsize=24)
    plt.ylabel('Voltages [mV]',fontsize=24)
    plt.xlim((-50,300))
    plt.ylim((-1000,8000))
    plt.grid()

    f2=plt.figure(pn+1,figsize=(10,7.5))

    plt.plot(times,newamps,label=situation+"_"+bias_voltage+" V")
    #plt.yscale('log')
    plt.xlabel('Time [ns]',fontsize=24)
    plt.ylabel('Voltages-BaseLine [mV]',fontsize=24)
    plt.xlim((0,300))
    plt.ylim((-1000,8000))
    plt.grid()

def drawMultipleTraces():
    bias_voltage=[0,1,2,3,4,5,10]
    fPdfRisetime = PdfPages('longPassivePixels.pdf')
    for j in range(0,6):
        fPdf = PdfPages('longPassivePixels_Pos'+str(j)+'.pdf')
        risetimes=[]
        amps=[]
        for i in range(7*j,7*(j+1)):
            situation = "F1longPassivePixels000" + str(int(i*2+1)).zfill(2)
            situationBase = "F1longPassivePixels000" + str(int(i*2)).zfill(2)
            data = readData(situation)
            basedata = readData(situationBase)
            newdata = minusBaseLine(data,basedata)
            irisetime, iamp=getRiseTime(newdata)
            markerRisetime(j*2,irisetime,iamp)
            risetimes.append(irisetime)
            amps.append(iamp)
            drawPlot(j*2,situation,i,str(bias_voltage[i%7]),data,newdata)

        f1=plt.figure(j*2,figsize=(10,7.5))
        plt.legend(prop={'size':15})
        plt.xlim((50,250))
        plt.ylim((-1000,3000))
        fPdf.savefig()
        f2=plt.figure(j*2+1,figsize=(10,7.5))
        plt.legend(prop={'size':15})
        plt.xlim((0,300))
        plt.ylim((-1000,3000))
        fPdf.savefig()
        fPdf.close()

        plotRiseTime(j,bias_voltage,risetimes,amps)

    f3=plt.figure(100,figsize=(10,7.5))
    plt.legend(prop={'size':15})
    fPdfRisetime.savefig()

    f4=plt.figure(101,figsize=(10,7.5))
    plt.legend(prop={'size':15})
    fPdfRisetime.savefig()

    fPdfRisetime.close()

def plotRiseTime(j, bias_voltage, risetimes, amps):
    location=['A','B','C','D','E','F']
    markerList=['*-', '.-', 'v-', '^-', '+-', 'o-',]
    f3=plt.figure(100,figsize=(10,7.5))
    plt.plot(bias_voltage,amps,markerList[j],label="Point_"+location[j])
    plt.xlabel('Bias Voltage [V]',fontsize=24)
    plt.ylabel('Maximum Voltage[mV]',fontsize=24)
    plt.xlim((-1,11))
    plt.ylim((0,3000))

    f4=plt.figure(101,figsize=(10,7.5))
    plt.plot(bias_voltage,risetimes,markerList[j],label="Point_"+location[j])
    plt.xlabel('Bias Voltage [V]',fontsize=24)
    plt.ylabel('Time [ns]',fontsize=24)
    plt.xlim((-1,11))
    plt.ylim((100,130))

def drawTraces():
    markerList=['*','*-','*-.', \
                '.','.-','.-.', \
                'v','v-','v-.', \
                '^','^-','^-.', \
                '+','+-','+-.', \
                'o','o-','o-.']
    situationList=["F1longPassivePixels00100","F1longPassivePixels00102", "C4longPassivePixels00000"]
    situationBaseList=["F1longPassivePixels00099","F1longPassivePixels00101"]

    bias_voltageList=["Pixel4_Bias_5","Pixel4_Bias_10","Pixel4_Bias 1.0",\
                      "Pixel4_Bias_1.5","Pixel4_Bias_2.0",\
                      "Pixel4_Bias_3.0","Pixel4_Bias_4.0"]
    fPdf = PdfPages('LaserPosA.pdf')
    for i in range(0,2):
        data = readData(situationList[i])
        if(i<2):
            basedata = readData(situationBaseList[i])
            newdata = minusBaseLine(data,basedata)
            risetime,riseamp=getRiseTime(newdata)
            drawPlot(1,situationList[i],markerList[i],bias_voltageList[i],data,newdata)
            markerRisetime(1,risetime,riseamp)
        else:
            drawSinglePlot(2,situationList[i],markerList[i],bias_voltageList[0],data)
        print('')
    f1=plt.figure(1,figsize=(10,7.5))
    plt.legend(prop={'size':15})
    plt.xlim((-50,350))
    plt.ylim((-100,200))
    f1.show()
    fPdf.savefig()

    f2=plt.figure(2,figsize=(10,7.5))
    plt.legend(prop={'size':15})
    plt.xlim((-50,350))
    plt.ylim((-100,200))
    f2.show()
    fPdf.savefig()
    fPdf.close()

if __name__ == "__main__":
    #drawMultipleTraces()
    drawTraces()
input("Press Enter to continue...")
