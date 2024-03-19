# okienko do logów musi być thread safe
# każda figura ma pola wyznaczone do ruchu + roszada -2p
# mechanizm tur

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget, QGraphicsItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QRectF, QMutex
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QTextEdit
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsRectItem

# Klasa reprezentująca pole na szachownicy
class ChessboardItem(QGraphicsItem):

    def __init__(self, row, col, size):
        super().__init__()
        self.setPos(col * size, row * size)
        self.size = size

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget=None):
        # Rysowanie szachownicy
        color = Qt.white if (self.x() / self.size + self.y() / self.size) % 2 == 0 else Qt.darkGray
        painter.fillRect(self.boundingRect(), color)

    def piece(self):
        return self.piece

    def setPiece(self, piece):
        self.piece = piece
        if piece:
            piece.setPos(self.x(), self.y())

# Klasa reprezentująca figurę szachową
class ChessPiece(QGraphicsPixmapItem):

    def __init__(self, piece_type, color, size):
        super().__init__()
        self.original_size = size
        self.piece_type = piece_type
        self.color = color
        self.setPiece(piece_type, color, size)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.isBeingDragged = False
        self.previous_row = None
        self.previous_col = None
        self.current_row = None
        self.current_col = None

    def setPiece(self, piece_type, color, size):
        self.filename = f"assets/{color.lower()}/{piece_type.lower()}.png"
        self.setPixmapWithSize(size)

    def setPixmapWithSize(self, size):
        size = round(size)
        pixmap = QPixmap(self.filename).scaled(size, size)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.previous_row, self.previous_col = self.currentPosition()
        #print(self.currentPosition())
        self.isBeingDragged = True
        self.setPixmapWithSize(self.original_size * 1.2)
        # print(f"{self.piece_type},{self.getValidMoves()}")
        self.valid_moves = None
        self.paintValidMoves()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isBeingDragged = False
        self.clearValidPaints()
        #self.current_row, self.current_col = self.currentPosition()
        self.setPixmapWithSize(self.original_size)

        self.checkPosition()
        #print(f"{self.currentPosition()}\n")

        self.checkMove()    
        super().mouseReleaseEvent(event)

    def checkMove(self):
        self.colorBool = True if self.color == "white" else False
        self.current_row, self.current_col = self.currentPosition()
        if self.checkTurn(self.colorBool):
            #print("1")  
            if self.moveIsNotInTheSamePlace():
                #print("2")
                if self.isValidMove():
                    #print("3")
                    if self.isNotOccupied():
                        #print("4")
                        self.scene().turn = not self.scene().turn
                        #print('\nwhite turn' if self.scene().turn else '\nblack turn')
                        chessboard.addMessage(self.chessNotation())
                        chessboard.addMessage('white turn' if self.scene().turn else 'black turn')
                        #self.previous_row =None
                        #self.previous_col = None
                        #self.current_row = None
                        #self.current_col = None
            
    def checkTurn(self, colorBool):
        if self.scene().turn != colorBool:
            #print('not your turn')
            chessboard.addMessage('not your turn')
            self.setPos(self.previous_col * 64, self.previous_row * 64)
            return False
        else:
            return True
        
    def moveIsNotInTheSamePlace(self):
        if self.previous_row == self.current_row and self.previous_col == self.current_col:
            return False
        else:
            return True
        
    def isValidMove(self):
        #print(self.valid_moves)
        if (self.current_row, self.current_col) in self.valid_moves:
            #print("tak")
            return True
        else:
            #print(self.current_row, self.current_row)
            self.setPos(self.previous_col * 64, self.previous_row * 64)
            #print("2xnie")
            return False

    def isNotOccupied(self):
                target_items = self.scene().items(self.mapToScene(self.boundingRect().center()))
                #print(target_items)
                for item in target_items:
                    #sprawdzenie czy przeciwnik nie stoi na polu docelowym
                    if isinstance(item, ChessPiece):
                        if item.color != self.color:
                            self.scene().removeItem(item)
                            return True
                    #sprawdzenie czy sojusznik nie stoi na polu docelowym
                    elif isinstance(item, QGraphicsRectItem):
                        self.setPos(self.previous_col * 64, self.previous_row * 64)
                        return False
                else:
                    return True

    def checkPosition(self):
        x = round(self.x() / 64) * 64
        y = round(self.y() / 64) * 64
        self.setPos(x, y)
    
    def currentPosition(self):
        current_row = int(self.y() / 64)
        current_col = int(self.x() / 64)

        return current_row, current_col
    
    def clearValidPaints(self):
        items = self.scene().items()
        for item in items:
            if isinstance(item, QGraphicsRectItem):
                self.scene().removeItem(item)
    
    def paintValidMoves(self):
        valid_moves, possible = self.getValidMoves()
        #print(valid_moves)
        self.valid_moves = valid_moves
        if possible:
            for move in valid_moves:
                x, y = move
                square = QGraphicsRectItem(y*64, x*64, 64, 64)
                items = self.scene().items(QRectF(y*64, x*64, 64, 64))
                for item in items:
                    if isinstance(item, ChessPiece):
                        items_row = int(item.y() / 64)
                        items_col = int(item.x() / 64)
                        if items_row == x*64 and items_col == y*64:
                            square.setBrush(QBrush(QColor(255, 0, 0, 100)))  # Red for occupied square
                            self.scene().addItem(square)
                        
                else:
                    square.setBrush(QBrush(QColor(0, 255, 0, 100)))  # Green for unoccupied square
                    self.scene().addItem(square)
        else:
            x, y = self.currentPosition()
            square = QGraphicsRectItem(y*64, x*64, 64, 64)
            square.setBrush(QBrush(QColor(255, 0, 0, 100)))
            self.scene().addItem(square)

    def chessNotation(self):
        name = self.piece_type
        if name == "knight":
            name="N"
        elif name == "bishop":
            name="B"
        elif name == "rook":
            name="R"
        elif name == "queen":
            name="Q"
        elif name == "king":
            name="K"
        elif name == "pawn":
            name="P"
        current_row, current_col = self.currentPosition()
        row = 8 - current_row
        col = chr(current_col + 97)
        #print(f"{name}{col}{row}")
        chessboard.addMessage(f"{name}{col}{row}")

    def getValidMoves(self):

        valid_moves = []

        current_row, current_col = self.currentPosition()
        
        direction = -1 if self.color == "white" else 1

        if self.piece_type == "pawn":

            if 0 <= current_row + direction <= 7:
                valid_moves.append((current_row + direction, current_col))

                # pierwszy ruch piona
                if (current_row == 1 and self.color == "black") or (current_row == 6 and self.color == "white"):
                    valid_moves.append((current_row + 2 * direction, current_col))
                                
            items = self.scene().items()

            #sprawdź czy na przekątnych polach są figury przeciwnika, jeżeli tak to dodaj do możliwych ruchów
            for col_offset in [-1, 1]:
                target_row = current_row + direction
                target_col = current_col + col_offset
                if 0 <= target_row <= 7 and 0 <= target_col <= 7:
                    for item in items:
                        if isinstance(item, ChessPiece):
                            items_row = int(item.y() / 64)
                            items_col = int(item.x() / 64)
                            if item.color != self.color and items_row == target_row and items_col == target_col:
                                valid_moves.append((items_row, items_col))
            
            #sprawdź czy na przeciwnym polu jest figura
            for item in items:
                if isinstance(item, ChessPiece):
                    items_row = int(item.y() / 64)
                    items_col = int(item.x() / 64)
                    if item.color != self.color:
                        if items_row == current_row + direction and items_col == current_col:
                            valid_moves.remove((current_row + direction, current_col))
                            break

        elif self.piece_type == "rook":

            for col in range(8):
                if col != current_col:
                    valid_moves.append((current_row, col))

            for row in range(8):
                if row != current_row:
                    valid_moves.append((row, current_col))

        elif self.piece_type == "knight":

            for row_offset in [-2, -1, 1, 2]:
                for col_offset in [-2, -1, 1, 2]:
                    if abs(row_offset) != abs(col_offset):
                        target_row = current_row + row_offset
                        target_col = current_col + col_offset
                        if 0 <= target_row <= 7 and 0 <= target_col <= 7:
                            valid_moves.append((target_row, target_col))
        
        elif self.piece_type == "bishop":

            for row_offset in [-1, 1]:
                for col_offset in [-1, 1]:
                    target_row = current_row + row_offset
                    target_col = current_col + col_offset
                    while 0 <= target_row <= 7 and 0 <= target_col <= 7:
                        valid_moves.append((target_row, target_col))
                        target_row += row_offset
                        target_col += col_offset

        elif self.piece_type == "queen":

            for col in range(8):
                if col != current_col:
                    valid_moves.append((current_row, col))

            for row in range(8):
                if row != current_row:
                    valid_moves.append((row, current_col))

            for row_offset in [-1, 1]:
                for col_offset in [-1, 1]:
                    target_row = current_row + row_offset
                    target_col = current_col + col_offset
                    while 0 <= target_row <= 7 and 0 <= target_col <= 7:
                        valid_moves.append((target_row, target_col))
                        target_row += row_offset
                        target_col += col_offset

        elif self.piece_type == "king":

            for row_offset in [-1, 0, 1]:
                for col_offset in [-1, 0, 1]:
                    if row_offset == 0 and col_offset == 0:
                        continue
                    target_row = current_row + row_offset
                    target_col = current_col + col_offset
                    if 0 <= target_row <= 7 and 0 <= target_col <= 7:
                        valid_moves.append((target_row, target_col))

        items = self.scene().items()

        for item in items:
            if isinstance(item, ChessPiece):
                items_row = int(item.y() / 64)
                items_col = int(item.x() / 64)
                if item.color == self.color:
                    for move in valid_moves:
                        #jeżeli figura tego samego koloru stoi na polu docelowym to usuń ruch
                        if move == (items_row, items_col):
                            valid_moves.remove((items_row, items_col))
                        
                        #jeżeli figura tego samego koloru stoi na polu pośrednim to usuń ruch
        
        possible = True if valid_moves else False
        #print(possible, valid_moves)
        self.chessNotation() if possible else None
        # print(self.piece_type, valid_moves)
        return (valid_moves, possible)

# Klasa reprezentująca szachownicę
class ChessboardScene(QGraphicsScene):

    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size
        self.initBoard()
        self.turn = True #true - white, false - black
        #print('white turn' if self.turn else 'black turn')

    def initBoard(self):
        border = QGraphicsRectItem(0, 0, 8*self.size, 8*self.size)
        border.setPen(QPen(Qt.black, 2))
        self.addItem(border)

        for i in range(8):
            for j in range(8):
                item = ChessboardItem(i, j, self.size)
                self.addItem(item)

        figures=['rook','knight','bishop','queen','king','bishop','knight','rook', 'pawn']
        for i in range(8):
            self.addChessPiece(figures[-1], "black", 1, i)
            self.addChessPiece(figures[i], "black", 0, i)
            self.addChessPiece(figures[-1], "white", 6, i)
            self.addChessPiece(figures[i], "white", 7, i)

    def addChessPiece(self, piece_type, color, row, col):
        piece = ChessPiece(piece_type, color, self.size)
        piece.setPos(col * self.size, row * self.size)
        self.addItem(piece)

# Klasa reprezentująca widżet szachownicy
class ChessboardWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.initLogWindow()
        self.initUI()
        

    def initLogWindow(self):
        self.log_mutex = QMutex()
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.show()
        self.addMessage("white turn")
        
    
    def addMessage(self, message):

        self.log_mutex.lock()
        self.log_window.append(message)
        self.log_mutex.unlock()


    def initUI(self):

        self.setWindowTitle('Chess')
        self.setGeometry(100, 100, 640, 640)
        self.createChessboard()
        self.show()

    def createChessboard(self):

        layout = QVBoxLayout()
        view = QGraphicsView(self)
        scene = ChessboardScene(64)

        view.setScene(scene)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(view)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chessboard = ChessboardWidget()
    sys.exit(app.exec_())
