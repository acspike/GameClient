import xmpp
from gameclient import GameClient

class TicTacToe(GameClient):
    def __init__(self):
        super(TicTacToe,self).__init__(resource='tictactoe')
        self.board = [str(x) for x in range(1,10)]
        self.connect()
        self.getPeer()
        self.getFirstTurn()
        self.turn = self.first
        if self.first:
            self.symbol = 'X'
            self.otherSymbol = 'O'
        else:
            self.symbol = 'O'
            self.otherSymbol = 'X'
    def play(self):
        print 'You are %ss' % self.symbol
        while True:
            if not self.turn:
                print '\nWaiting for your turn...'
                while not self.turn:
                    self.process(1)
            self.printBoard()
            
            if self.checkWinner():
                break
                
            while True:
                sel = raw_input('\nMake a selection:' )
                try:
                    sel = int(sel) - 1
                except:
                    print 'Invalid input'
                    continue
                if 0 <= sel < 9 and self.board[sel] not in ['X','O']:
                    self.board[sel] = self.symbol
                    self.sendOther('turn',str(sel))
                    self.turn = not self.turn
                    break
                else:
                    print 'Invalid input'
                    continue
                
            if self.checkWinner():
                break
                
        self.exit()
        
    def printBoard(self):
        print '\n+-+-+-+'
        print '|%s|' % '|'.join(self.board[:3])
        print '+-+-+-+'
        print '|%s|' % '|'.join(self.board[3:6])
        print '+-+-+-+'
        print '|%s|' % '|'.join(self.board[6:])
        print '+-+-+-+'
        
    def checkWinner(self):
        winner = False
        b = self.board
        combos = [
            [b[0],b[1],b[2]],
            [b[3],b[4],b[5]],
            [b[6],b[7],b[8]],
            [b[0],b[3],b[6]],
            [b[1],b[4],b[7]],
            [b[2],b[5],b[8]],
            [b[0],b[4],b[8]],
            [b[2],b[4],b[6]]]
        for c in combos:
            if c[0] == c[1] and c[1] == c[2]:
                winner = c[0]
        if winner and winner == self.symbol:
            print '\nYou win!'
        elif winner:
            print '\nYou lose.'
        elif len([x for x in b if x not in ['X','O']]) == 0:
            print "\nCat's game"
            winner = True
        return winner
            
        
    def handleMessageTurn(self, conn, msg):
        tag = msg.getTag('turn', namespace=self.getNamespace())
        if tag:
            sel = int(tag.getData())
            self.board[sel] = self.otherSymbol
            self.turn = not self.turn
            raise xmpp.NodeProcessed

    
if __name__ == '__main__':
    ttt = TicTacToe()
    ttt.play()
    