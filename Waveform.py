import numpy as np
import scipy.interpolate as itp

class Waveform(object):
    def __init__(self, dataArray):
        self.times = 1e6*dataArray[0,4:].astype('float')
        self.amps = 1e3*dataArray[1,4:].astype('float')
        self.lens = len(self.times)

    def corrBaseline(self, tleft, tright):
        tleft_index=self.findNearestIndex(self.times, tleft)
        tright_index=self.findNearestIndex(self.times, tright)
        corr=sum(arr[tleft_index:tright_index])/(tright-tleft)
        amps=self.amps-corr
        return amps

    def findNearestIndex(self, arr, value):
        arr = np.array(arr)
        index = (np.abs(arr-value)).argmin()
        return index

    def findTimesNearestIndex(self, value, times, amps):
        precision = min(np.abs(amps-value))+0.001
        indexs = np.where(np.abs(amps-value)<=precision)
        return np.min(indexs)

    def interpolate(self, ntimes=100):
        itimes=np.linspace(self.times[0],self.times[-1],num=self.lens*ntimes))
        tck=itp.splrep(self.times,self.amps,s=0)
        iamps=itp.splev(itimes,tck,der=0)
        self.itimes=itimes
        self.iamps=itamps

    def getPeak(self, times=self.itimes, amps=self.iamps):
        peakindex=np.argmin(amps)
        peaktime=itimes[peakindex]
        peakamp=iamps[peakindex]
        return peaktime,peakamp,peakindex

    def reshapeWaveform(self, tleft=2, tright=5):
        peaktime,peakamp,peakindex=self.getPeak()
        tstart_index=self.findNearestIndex(peaktime-telft)
        tend_index=self.findNearestIndex(peaktime+tright)
        rtimes=self.itimes[tstart_index:tend_index]
        ramps=self.iamps[tstart_index:tend_index]
        return rtimes, ramps

    def getRiseTime(self, flow=0.25, fhigh=0.75):
        rtimes,ramps=self.reshapeWaveform()
        peaktime,peakamp,peakindex=self.getPeak(rtime,tamps)

        amplow=peakamp*flow
        amphigh=peakamp*fhigh



