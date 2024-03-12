# 1. rysowanie planszy i figur (1)
# 2. pionki mają dziedziczyć po QGraphicsItem (1)
# 3. Pionki ma dać się przesuwać i to przesuwanie powinno być w ramach siatki (2)
# 4. zmiana grafiki podczas przeciagania (1)

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget, QGraphicsItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen
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
        self.setPiece(piece_type, color, size)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.isBeingDragged = False

    def setPiece(self, piece_type, color, size):
        self.filename = f"assets/{color.lower()}/{piece_type.lower()}.png"
        self.setPixmapWithSize(size)

    def setPixmapWithSize(self, size):
        size = round(size)
        pixmap = QPixmap(self.filename).scaled(size, size)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.isBeingDragged = True
        self.setPixmapWithSize(self.original_size * 1.2)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isBeingDragged = False
        self.setPixmapWithSize(self.original_size)
        self.checkPosition()
        super().mouseReleaseEvent(event)
    
    def checkPosition(self):
        x = round(self.x() / 64) * 64
        y = round(self.y() / 64) * 64
        self.setPos(x, y)

# Klasa reprezentująca szachownicę
class ChessboardScene(QGraphicsScene):

    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size
        self.initBoard()

    def initBoard(self):
        # Draw the border around the edge of the board
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

        self.initUI()

    def initUI(self):

        self.setWindowTitle('Chessboard')
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
