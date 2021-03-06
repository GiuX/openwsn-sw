#!/usr/bin/python

import logging
import random
import math

import HwModule

class HwCrystal(HwModule.HwModule):
    '''
    \brief Emulates the mote's crystal.
    '''
    
    FREQUENCY = 32768
    MAXDRIFT  = 0
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine          = engine
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        self.frequency       = self.FREQUENCY
        self.maxDrift        = self.MAXDRIFT
        
        # local variables
        self.drift           = float(random.uniform(-self.maxDrift,
                                                    +self.maxDrift))
        self.tsTick          = self.timeline.getCurrentTime()
        
        # initialize the parent
        HwModule.HwModule.__init__(self,'HwCrystal')
    
    #======================== public ==========================================
    
    def start(self):
        '''
        \brief Start the crystal.
        '''
        
        self.tsTick          = self.timeline.getCurrentTime()
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('crystal starts at '+str(self.tsTick))
    
    def getTimeLastTick(self):
        '''
        \brief Return the timestamp of the last tick.
        
        \returns The timestamp of the last tick.
        '''
        
        currentTime          = self.timeline.getCurrentTime()
        timeSinceLast        = currentTime-self.tsTick
        period               = self._getPeriod()
        
        numTicksSinceLast    = math.floor(float(timeSinceLast)/float(period))
        timeLastTick         = self.tsTick+numTicksSinceLast*period
        
        self.tsTick          = timeLastTick
        
        return timeLastTick
    
    def getTimeIn(self,numticks):
        '''
        \brief Return the time it will be in a given number of ticks.
        
        \params numticks The number of ticks of interest.
        
        \returns The time it will be in a given number of ticks.
        '''
        
        timeLastTick         = self.getTimeLastTick()
        period               = self._getPeriod()
        
        return timeLastTick+numticks*period
    
    def getTicksSince(self,eventTime):
        '''
        \brief Return the number of ticks since some timestamp.
        
        \params eventTime The time of the event of interest.
        
        \returns The number of ticks since the time passed.
        '''
        
        # get the current time
        currentTime          = self.timeline.getCurrentTime()
        
        # make sure that eventTime passed is in the past
        assert(eventTime<=currentTime)
        
        # get the time of the last tick
        timeLastTick         = self.getTimeLastTick()
        
        # return the number of ticks
        if eventTime>timeLastTick:
            return 0
        else:
            period           = self._getPeriod()
            return int(math.floor(float(timeLastTick-eventTime)/float(period)))
    
    #======================== private =========================================
    
    def _getPeriod(self):
        
        period               = float(1)/float(self.frequency)             # nominal period
        period              += float(self.drift)*float(period/1000000)    # apply drift
        
        return period
        