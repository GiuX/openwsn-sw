import sys
import os
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openUI'))     # openUI/

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from lbrClient     import lbrClient
import OpenWindow
import OpenFrameState
import OpenFrameLbr

import Tkinter

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class MoteStateGui(object):
    
    GUI_UPDATE_PERIOD = 500
    
    def __init__(self,moteProbe_handlers,
                      moteConnector_handlers,
                      moteState_handlers,
                      lbrClient_handlers,
                      lbrConnectParams_cb):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
        self.lbrClient_handlers     = lbrClient_handlers
        self.lbrConnectParams_cb    = lbrConnectParams_cb
        
        # local variables
        self.window                 = OpenWindow.OpenWindow("mote state GUI")
        self.framesState            = {}
        self.frameLbr               = None
        
        #===== framesState
        
        tempStatesFrame             = Tkinter.Frame(self.window)
        tempStatesFrame.grid(row=0)
        frameOrganization = [
            [
                moteState.moteState.ST_ISSYNC,
                moteState.moteState.ST_ASN,
                moteState.moteState.ST_MYDAGRANK,
                moteState.moteState.ST_OUPUTBUFFER,
            ],
            [
                moteState.moteState.ST_IDMANAGER,
                moteState.moteState.ST_MACSTATS,
            ],
            [
                moteState.moteState.ST_SCHEDULE,
            ],
            [
                moteState.moteState.ST_NEIGHBORS,
                moteState.moteState.ST_QUEUE,
            ],
        ]
        for row in range(len(frameOrganization)):
            tempRowFrame = Tkinter.Frame(tempStatesFrame)
            tempRowFrame.grid(row=row)
            for column in range(len(frameOrganization[row])):
                stateType = frameOrganization[row][column]
                self.framesState[stateType]   = OpenFrameState.OpenFrameState(
                                                    tempRowFrame,
                                                    frameName=stateType,
                                                    row=0,
                                                    column=column
                                                )
                self.framesState[stateType].startAutoUpdate(
                                                    self.GUI_UPDATE_PERIOD,
                                                    self.moteState_handlers[0].getStateElem,
                                                    (stateType,)
                                                )
                self.framesState[stateType].show()
        
        #===== frameLbr
        
        self.frameLbr = OpenFrameLbr.OpenFrameLbr(self.window,
                                                  self.lbrClient_handlers[0],
                                                  self.lbrConnectParams_cb,
                                                  row=1)
        self.frameLbr.show()
        
    #======================== public ==========================================
    
    def start(self):
        self.window.startGui()
    
    #======================== private =========================================

class MoteStateGui_app(object):
    
    def __init__(self):
        self.moteProbe_handlers        = []
        self.moteConnector_handlers    = []
        self.moteState_handlers        = []
        self.lbrClient_handlers        = []
        
        # create a moteProbe for each mote connected to this computer
        serialPorts    = moteProbe.utils.findSerialPorts()
        tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
        for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
            self.moteProbe_handlers.append(moteProbe.moteProbe(serialPort,tcpPort))
        
        # create a moteConnector for each moteProbe
        for mp in self.moteProbe_handlers:
           self.moteConnector_handlers.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
        
        # create a moteState for each moteConnector
        for mc in self.moteConnector_handlers:
           self.moteState_handlers.append(moteState.moteState(mc))
        
        # create an lbrClient for each moteConnector
        for mc in self.moteConnector_handlers:
           self.lbrClient_handlers.append(lbrClient.lbrClient(mc))
        
        # create an open GUI
        gui = MoteStateGui(self.moteProbe_handlers,
                           self.moteConnector_handlers,
                           self.moteState_handlers,
                           self.lbrClient_handlers,
                           self.indicateConnectParams)
        
        # start threads
        for lc in self.lbrClient_handlers:
           lc.start()
        for ms in self.moteState_handlers:
           ms.start()
        for mc in self.moteConnector_handlers:
           mc.start()
        gui.start()
    
    #======================== GUI callbacks ===================================
    
    def indicateConnectParams(self,connectParams):
        try:
            self.lbrClient_handlers[0].connect(connectParams['LBRADDR'],
                                               connectParams['LBRPORT'],
                                               connectParams['USERNAME'])
        except KeyError:
            log.error("malformed connectParams={0}".format(connectParams))
    
def main():
    app = MoteStateGui_app()
    
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('moteStateGui.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbeUtils',
                   'moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'ParserError',
                   'ParserData',
                   'moteState',
                   'lbrClient',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()