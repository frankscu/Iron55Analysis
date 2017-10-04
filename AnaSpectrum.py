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
    situation=str(situation).zfill(5)
    fileName = '../OverMOS/C2fe55_active_ac_'+situation+'.csv'
    print("Processing File: ",fileName)

    times,amps=csv_reader(fileName)

    data_list=[times,amps]

    dataArray = np.array(data_list)
    return dataArray

def drawTrace(pn,situation, dataArray):
    situation=str(situation).zfill(5)

    times=1e6*dataArray[0,4:].astype('float') # mV
    amps=1e3*dataArray[1,4:].astype('float') # us

    f1=plt.figure(pn,figsize=(10,7.5))

    plt.plot(times,amps,label=situation)
    #plt.yscale('log')
    plt.xlabel('Time [us]',fontsize=24)
    plt.ylabel('Voltages [mV]',fontsize=24)
    plt.xlim((-40,40))
    plt.ylim((-50,20))
    plt.grid()


def drawFullTrace(pn,situation, dataArray):
    situation=str(situation).zfill(5)

    times=1e6*dataArray[0,4:].astype('float') # mV
    amps=1e3*dataArray[1,4:].astype('float') # us

    f1=plt.figure(pn//12,figsize=(10,7.5))
    plt.subplot(3,4,(pn%12+1))
    plt.plot(times,amps,label=situation)
    #plt.yscale('log')
    plt.xlabel('Time [us]',fontsize=12)
    plt.ylabel('Voltages [mV]',fontsize=12)
    plt.xlim((-40,40))
    plt.ylim((-50,20))
    #plt.grid()

def specturmADC(dataArray):
    cutflags=False
    baseline=0
    times=1e6*dataArray[0,4:].astype('float') # mV
    amps=1e3*dataArray[1,4:].astype('float') # us
    if min(amps[:200]) < -8:
        cutflags=True
    elif min(amps[300:]) < -8:
        cutflags=True

    adc_channel=min(amps)
    adc_channel=baseline-adc_channel
    return cutflags, adc_channel

def drawSpecturm():
    fPdf = PdfPages('specturm_Fe55.pdf')
    adc_nchannels=[]
    adcBytdc_nchannels=[]
    tdc_nchannels=[]
    nfiles=5050
    for i in range(0,nfiles):
        data = readData(i)
        cutflags, adc_channel=specturmADC(data)
        risetimeUp,riseampUp, risetimeDown, riseampDown, risetimeflag=getRiseTime(data)
        if cutflags==True:
            continue
        drawTrace(1,i,data)
        adc_nchannels.append(adc_channel)

        tdc_channel=risetimeUp-risetimeDown
        if risetimeflag==True and tdc_channel<1 and adc_channel>12:
            tdc_nchannels.append(tdc_channel/adc_channel)
            adcBytdc_nchannels.append(adc_channel)
        print(str(adc_channel))
        print(str(tdc_channel))

    f1=plt.figure(1,figsize=(10,7.5))
    #f1.show()
    #plt.legend(prop={'size':15})
    fPdf.savefig()

    f2=plt.figure(2,figsize=(10,7.5))
    plt.hist(adc_nchannels,bins=150, histtype='step')
    plt.xlabel('Minimal Voltage [mV]',fontsize=24)
    plt.ylabel('Counts',fontsize=24)
    #plt.ylim((-6,4))
    plt.yscale('log')
    #f2.show()
    fPdf.savefig()

    f3=plt.figure(3,figsize=(10,7.5))
    plt.hist(tdc_nchannels,bins=150, histtype='step')
    plt.xlabel('Rise Time [us]',fontsize=24)
    plt.ylabel('Counts',fontsize=24)
    plt.xlim((0,0.2))
    plt.yscale('log')
    #f3.show()
    fPdf.savefig()

    f4=plt.figure(4,figsize=(10,7.5))
    hb = plt.hexbin(adcBytdc_nchannels,tdc_nchannels,cmap='Greys')
    cb = f4.colorbar(hb)
    cb.set_label("counts")
    plt.ylim((0,0.02))
    plt.xlabel('Minimal Voltage',fontsize=24)
    plt.ylabel('Rise Time [us]',fontsize=24)

    fPdf.savefig()

    fPdf.close()

def drawMultipleTraces():
    for j in range(97,98):
        print(j)
        fh=str(j*10)
        fe=str(j*10+10)
        fPdf = PdfPages('specturm'+fh+'_'+fe+'_copy.pdf')
        for i in range(int(fh),int(fe)):
            print(i)
            if i%2==0 or i==971 or i==973 or i==977: continue
            data = readData(i)
            drawTrace(j,i,data)
            risetimeUp,riseampUp, risetimeDown, riseampDown, risetimeflag=getRiseTime(data)
            if risetimeflag==True:
                markerRisetime(j,risetimeUp,riseampUp,risetimeDown,riseampDown)
            print('')

        fp=plt.figure(j,figsize=(10,7.5))
        plt.legend(prop={'size':15})
        plt.xlim((-0.5,2))
        plt.ylim((-70,20))
        #f1.show()
        fPdf.savefig()
        fPdf.close()

def ftimes(amp, times, amps):
    precision = min(np.abs(amps-amp))+0.001
    peakindexs=np.where(np.abs(amps-amp)<=precision)
    return (times[np.min(peakindexs)])

def getRiseTime(dataArray):
    risetimeflag=True
    risetimeUp=0
    risetimeDown=0
    riseampUp=0
    riseampDown=0
    slicedataArray=[]
    timesfull=1e6*dataArray[0,4:].astype('float')
    ampsfull=1e3*dataArray[1,4:].astype('float')
    peakindex=np.argmin(ampsfull)
    print( timesfull[peakindex])
    if timesfull[peakindex]>10 or timesfull[peakindex]<-10:
        risetimeFlag=False
        return risetimeUp, riseampUp, risetimeDown, riseampDown, risetimeflag
    else:
        lens=len(ampsfull)
        #print(lens)
        times=timesfull[(peakindex-int(lens/10)):(peakindex+int(lens/30))] # mV
        amps=ampsfull[(peakindex-int(lens/10)):(peakindex+int(lens/30))] # us
        slicedataArray.append(times)
        slicedataArray.append(amps)
        idataArray=interpolate(slicedataArray)
        newtimes=idataArray[0].astype('float')
        newamps=idataArray[1].astype('float')

        #ftimes= lambda v: (newtimes[(np.abs(newamps-v)).argmin()])
        #ftimes= lambda v: (newtimes[np.min(np.where(np.abs(newamps-v)<0.02))])
        newampsfull=newamps.astype('float')
        newpeakindex=np.argmin(newampsfull)

        riseampUp = min(newamps)*0.75
        riseampDown = min(newamps)*0.25
        risetimeUp = ftimes(riseampUp,newtimes[(newpeakindex-int(lens*100/2)):(newpeakindex+5)], \
                            newamps[(newpeakindex-int(lens*100/2)):(newpeakindex+5)])
        risetimeDown = ftimes(riseampDown,newtimes[(newpeakindex-int(lens*100/2)):(newpeakindex+5)], \
                            newamps[(newpeakindex-int(lens*100/2)):(newpeakindex+5)])

        #print("risetimeUp: {:.2f}".format(risetimeUp))
        #print("riseampUp: {:.2f}".format(riseampUp))
        #print("risetimeDown: {:.2f}".format(risetimeDown))
        #print("riseampDown: {:.2f}".format(riseampDown))
        return risetimeUp, riseampUp, risetimeDown, riseampDown, risetimeflag

def interpolate(dataArray):
    idataArray=[]
    newtimes=dataArray[0].astype('float')
    newamps=dataArray[1].astype('float')

    itimes=np.linspace(newtimes[0],newtimes[-1],num=int(len(newtimes)*100))
    tck=itp.splrep(newtimes,newamps,s=0)
    iamps=itp.splev(itimes,tck,der=0)
    idataArray.append(itimes)
    idataArray.append(iamps)
    return idataArray

def markerFullRisetime(pn,risetimeUp,riseampUp,risetimeDown,riseampDown):
    f1=plt.figure(pn,figsize=(10,7.5))
    plt.subplot(3,4,(pn%12+1))
    plt.plot([risetimeDown,risetimeDown],[riseampDown-10,riseampDown+10],'k--',lw=2)
    plt.plot([risetimeUp,risetimeUp],[riseampUp-10,riseampUp+10],'k--',lw=2)

    #plt.plot([risetime-110,risetime+20],[riseamp,riseamp],'k--',lw=2)
    risetimeCenter=(risetimeUp+risetimeDown)/2
    riseampCenter=(riseampUp+riseampDown)/2
    plt.annotate('',[risetimeDown,riseampCenter],[risetimeUp,riseampCenter],\
                 arrowprops={'arrowstyle':'<->'})

    risetime=risetimeUp-risetimeDown
    plt.text(risetimeCenter,riseampCenter,'{:.2f} us'.format(risetime),fontsize=15)

def markerRisetime(pn,risetimeUp,riseampUp,risetimeDown,riseampDown):
    f1=plt.figure(pn,figsize=(10,7.5))
    plt.plot([risetimeDown,risetimeDown],[riseampUp,riseampDown],'k--',lw=1)
    plt.plot([risetimeUp,risetimeUp],[riseampUp,riseampDown],'k--',lw=1)

    #plt.plot([risetime-110,risetime+20],[riseamp,riseamp],'k--',lw=2)
    risetimeCenter=(risetimeUp+risetimeDown)/2
    riseampCenter=(riseampUp+riseampDown)/2
    plt.annotate('',[risetimeDown,riseampUp],[risetimeUp,riseampUp],\
                 arrowprops={'arrowstyle':'<->'})

    risetime=risetimeUp-risetimeDown
    plt.text(risetimeUp-0.3,riseampUp,'{:.2f} us'.format(risetime),fontsize=15)

def drawSingleTraces():
    fPdf = PdfPages('specturmTimes.pdf')
    for i in range(0,24):
        data = readData(i)
        drawFullTrace(i,i,data)
        risetimeUp,riseampUp, risetimeDown, riseampDown, risetimeflag=getRiseTime(data)
        if risetimeflag==True:
            markerFullRisetime(i,risetimeUp,riseampUp,risetimeDown,riseampDown)

    for i in range(0,2):
        f1=plt.figure(i,figsize=(10,7.5))
        f1.tight_layout()
        for j in range(0,12):
            plt.subplot(3,4,(j+1))
            plt.legend(prop={'size':12})
            plt.xlim((-2,5))
            plt.ylim((-70,20))

        fPdf.savefig()
    fPdf.close()

################## Main Function #################
if __name__ == "__main__":
    #drawMultipleTraces()
    #drawSingleTraces()
    drawSpecturm()

input("Press Enter to continue...")
