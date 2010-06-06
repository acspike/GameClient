import pypm
import xmpp
import cPickle
import base64
from gameclient import GameClient

INPUT=0
OUTPUT=1

def PrintDevices(InOrOut):
    for loop in range(pypm.CountDevices()):
        interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
        if ((InOrOut == INPUT) & (inp == 1) |
            (InOrOut == OUTPUT) & (outp ==1)):
            print loop, name," ",
            if (inp == 1): print "(input) ",
            else: print "(output) ",
            if (opened == 1): print "(opened)"
            else: print "(unopened)"
    print

class MidiGate(GameClient):
    def __init__(self):
        super(MidiGate,self).__init__(resource='midigate')
        
        pypm.Initialize()
        
        try:
            PrintDevices(INPUT)
            indev = int(raw_input("Choose an input device: "))
            self.MidiIn = pypm.Input(indev)
        except:
            print "failed to select midi input"
            self.exit()
            
        print
        
        try:
            PrintDevices(OUTPUT)
            outdev = int(raw_input("Choose an input device: "))
            self.MidiOut = pypm.Output(outdev, 20)
        except:
            print "failed to select midi output"
            self.exit()
        
        self.connect()
        self.getPeer()
    
    def sendCData(self, tag, data):
        if self.peer:
            new_node = xmpp.simplexml.Node(tag)
            new_node.setNamespace(self.getNamespace())
            new_node.addData(data)
            message = xmpp.protocol.Message(self.peer,payload=[new_node])
            self.conn.send(message)
        else:
            raise Exception, "No Peer Found"
    
    def play(self):
        while True:
            self.process()
            if self.MidiIn.Poll(): 
                MidiData = self.MidiIn.Read(1)
                #base64 might be overkill
                data = base64.encodestring(cPickle.dumps(MidiData[0][0], 0))
                self.sendCData('midi', data)
            self.process()
            
    def handleMessageMidi(self, conn, msg):
        tag = msg.getTag('midi', namespace=self.getNamespace())
        if tag:
            data = tag.getData()
            print data
            #base64 might be overkill
            MidiData = cPickle.loads(base64.decodestring(data))
            self.MidiOut.Write([[MidiData,pypm.Time()]])
            raise xmpp.NodeProcessed

    
if __name__ == '__main__':
    mg = MidiGate()
    mg.play()
    