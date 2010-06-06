import xmpp, random, getpass

class GameClient(object):
    def __init__(self, jid=None, password=None, resource='gameclient'):
        self.peer = None
        self.peer_random_values = None
        self.first = None
        self.jid = jid
        self.password = password
        self.base_resource = resource
    
    def connect(self, jid=None, password=None, resource=None):
        if not jid:
            jid = raw_input('JID: ')
        self.jid = xmpp.protocol.JID(jid)
        
        if resource != None:
            self.base_resource = resource
        self.jid.setResource(self.base_resource)
        
        if not password:
            self.password = getpass.getpass('Password for %s: ' % jid)
        else:
            self.password = password

        self.conn = xmpp.Client(self.jid.getDomain(), debug=[])
        self.conn.connect()
        
        message_handlers = [x for x in dir(self) if x.startswith('handleMessage')]
        for mh in message_handlers:
            self.conn.RegisterHandler('message', getattr(self, mh))

        self.conn.auth(self.jid.getNode(), self.password, self.jid.getResource())
        
        if hasattr(self.conn, 'Bind'):
            self.jid = xmpp.protocol.JID(self.conn.Bind.bound[-1])
        self.conn.send(xmpp.protocol.Presence(priority=-1))
    
    def exit(self):
        self.conn.disconnect()
        raise SystemExit
    
    def process(self, timeout=0):
        return self.conn.Process(timeout)
    
    def processBulk(self, iterations=10, timeout=1):
        retval = []
        for i in range(iterations):
            retval.append(self.process(timeout))
        return retval
    
    def getNamespace(self):
        return "%s-ns" % self.base_resource
    
    def sendText(self, text):
        if self.peer:
            self.conn.send(xmpp.protocol.Message(self.peer, text))
        else:
            raise Exception, "No Peer Found"
    
    def sendOther(self, tag, text):
        if self.peer:
            new_node = xmpp.simplexml.Node(tag, payload=[text])
            new_node.setNamespace(self.getNamespace())
            message = xmpp.protocol.Message(self.peer,payload=[new_node])
            self.conn.send(message)
        else:
            raise Exception, "No Peer Found"
        
    def handleMessageBody(self, conn, msg):
        if msg.getBody():
            print "%s: %s" % (msg.getFrom(), msg.getBody())
            raise xmpp.NodeProcessed
    
    def handleMessageCoinToss(self, conn, msg):
        tag = msg.getTag('coinToss', namespace=self.getNamespace())
        if tag:
            self.peer_random_values = [int(x) for x in tag.getData().split(" ")]
            raise xmpp.NodeProcessed
    
    def getPeer(self):
        print "Searching for peer..."
        roster = self.conn.getRoster()        
        
        while True:
            possible = []
            self.processBulk()            

            jids = roster.getItems()
            for j in jids:
                res = roster.getResources(j)
                for r in res:
                    if r.startswith(self.base_resource):
                        possible.append("%s/%s" % (j,r))
            
            if len(possible) == 0:
                print "No peers found. Enter Q to quit, anything else to continue waiting."
                if raw_input().upper() == 'Q':
                    break
                else:
                    continue
            else:
                item = 1
                for p in possible:
                    print "%s.\t%s" % (item, p)
                    item
                print "C.\tContinue Waiting"
                print "Q.\tQuit"
                operation = None
                while not operation:
                    operation = None
                    selection = raw_input('Enter your selection: ')
                    if selection.upper() == 'Q':
                        operation = 'break'
                    elif selection.upper() == 'C':
                        operation = 'continue'
                    else:
                        try:
                            self.peer = possible[int(selection) - 1]
                            operation = 'break'
                        except:
                            print "Invalid selection"
                    
                if operation == 'break':
                    break
                elif operation == 'continue':
                    continue

        if not self.peer:
            self.exit()
    
    def getFirstTurn(self):
        if self.first != None:
            return self.first
        
        print "Highest number goes first..."
        
        my_random_values = []
        for i in range(10):
            my_random_values.append(random.randint(0,60000))
        
        self.sendOther('coinToss'," ".join([str(x) for x in my_random_values]))
        
        while not self.peer_random_values:
            self.process(1)
        
        for m,y in zip(my_random_values, self.peer_random_values):
            if m == y:
                continue
            elif m > y:
                print "You go first"
                self.first = True
            else:
                print "You go second"
                self.first = False
            break
            
        if self.first != None:
            return self.first
        else:
            print "A perfect tie on all ten random numbers! I quit."
            self.exit()

    
if __name__ == '__main__':
    import time
    gc = GameClient()
    gc.connect()
    gc.getPeer()
    gc.getFirstTurn()
    start = time.time()
    while time.time() - start < 25:
        gc.process(1)
    gc.exit()