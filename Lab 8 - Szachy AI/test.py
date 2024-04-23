#tryb rozgrywki - 2 graczy albo AI         -0,5p
#adres ip i port - do komunikacji po sieci -0,5
#zapis historii gry w sql lite3            -1p
#zapis historii do XML                     -1p
#zapis opcji w json                        -1p
#odczyt i playback historii ruchów         -1p




import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QWidget, QGraphicsItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QRectF, QMutex
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsRectItem, QTextEdit
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QLabel, QMenuBar, QMenu, QAction, QLineEdit, QRadioButton, QPushButton
from PyQt5.QtCore import QTimer, QTime

import json
import xml.etree.ElementTree as ET
import sqlite3
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from PyQt5.QtWidgets import QMessageBox

import random
import time


class ChessClock:
    def __init__(self, white_time, black_time):
        self.white_time = QTime(0, white_time)
        self.black_time = QTime(0, black_time)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self. current_player ="white"

    def start(self):
        self.timer.start(1000)

    def stop(self):
        self.timer.stop()
    
    def switch(self):
        self.stop()
        self.current_player = "black" if self.current_player=="white" else "white"
        self.start()

    def update_time(self):
        if self.current_player == "white":
            self.white_time = self.white_time.addSecs(-1)
        else:
            self.black_time = self.black_time.addSecs(-1)

    def get_time(self):
        return self.white_time.toString(), self.black_time.toString()


# Klasa reprezentująca pole na szachownicy
class ChessboardItem(QGraphicsItem):

    def __init__(self, row, col, size):
        super().__init__()
        self.setPos(col * size, row * size)
        self.size = size
        self.table_save = []


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

# MARK: AI class
class Ai:
    def __init__(self):
        self.Q = {}
        print("AI istnieje")
        self.valid_moves_history = []
        self.last_valid_moves = []
        self.epsilon = 0.8
        self.learning_rate = 2
        self.discount_factor = 0.9 
        self.init_Q_table()
        self.zbicie = False
        self.q = 0
        self.powtorz = False

    def init_Q_table(self):
        items = chessboard.scene.items()
        
        for row in range(8):
            for col in range(8):
                #znajdź figurę na danym polu
                for item in items:
                    if isinstance(item, ChessPiece) and item.color=="black":
                        if item.currentPosition() == (row, col):

                            self.valid_moves, _ = item.getValidMoves(False)
                            self.last_valid_moves += self.valid_moves
                            for action in self.valid_moves:
                                self.Q[((row, col), action)] = 0
                                if item.piece_type == "king": self.Q[((row, col), action)] = -10
        self.valid_moves_history += self.last_valid_moves

    #metoda epsilno-greedy
    def choose_action(self):
        while True:
            print(f'dokonuję wyboru Q, {self.epsilon}')
            if self.powtorz or random.uniform(0, 1) < self.epsilon:
                key = random.choice(list(self.Q.keys()))
                value = self.Q[key]
                if value == None: 
                    self.powtorz = True
                    continue
                else:
                    if key[1] in self.last_valid_moves:
                        pos1, pos2= key
                        self.powtorz =False
                        return pos1, pos2, value
            else:
                
                max_value=0
                for key, value in self.Q.items():
                    if value > max_value:
                        max_value = value
                if max_value == 0:
                    choice = random.choice(list(self.Q.keys()))
                    pos1, pos2 = choice
                    return pos1, pos2, 0
                else:
                    print(1)
                    for key, value in self.Q.items():
                        if value == max_value:
                            if key[1] in self.last_valid_moves:
                                self.epsilon=0.6 if self.epsilon < 0.01 else None
                                pos1, pos2= key
                                return pos1, pos2, value
                    
    def update_Q(self, state, action, reward, next_state):
        currentQ = self.Q[(state, action)]
        max_next_Q = max(self.Q.values()) if next_state in self.Q else 0
        self.Q[(state, action)] += self.learning_rate * (reward + self.discount_factor * max_next_Q - currentQ)+5*self.zbicie
        
        self.zbicie = False
        self.q = 0

    def get_actual_valid_moves(self):
        items = chessboard.scene.items()
        self.last_valid_moves = []
        for item in items:
            if isinstance(item, ChessPiece) and item.color=="black":
                row, col = item.currentPosition()
                self.valid_moves, _ = item.getValidMoves(False)

                for action in self.valid_moves:
                    key = ((row, col), action)
                    if key not in self.Q:
                        self.Q[(row, col), action] = 0

                self.last_valid_moves += self.valid_moves
        self.valid_moves_history += self.last_valid_moves

        # jeżeli możliwość bicia to dodaj do Q znacznie większą wartość
        for item in items:
            if isinstance(item, ChessPiece) and item.color=="white":
                white_row, white_col = item.currentPosition()
                white_name = item.piece_type
                if white_name == "pawn":
                    self.q = 10
                elif white_name == "rook":
                    self.q=100
                elif white_name == "bishop":
                    self.q=30
                elif white_name == "knight":
                    self.q=30

                for state,action in self.Q.keys():
                    if action ==(white_row, white_col):
                        self.Q[(state, action)] += self.q
                        self.epsilon = 0.01
            if isinstance(item, ChessPiece) and item.color=="white" and item.piece_type == "king":
                king_row, king_col = item.currentPosition()

                for state,action in self.Q.keys():
                    if action ==(king_row, king_col):
                        self.Q[(state, action)] += 1000
                        self.epsilon = 0
            
            elif isinstance(item, ChessPiece) and item.color=="white" and item.piece_type == "queen":
                queen_row, queen_col = item.currentPosition()

                for state,action in self.Q.keys():
                    if action ==(queen_row, queen_col):
                        self.Q[(state, action)] += 1000
                        self.epsilon = 0

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
        self.numer_rundy = 0
        self.move_history=[]

    # MARK: ruch AI
    def ai_move(self):
        print("ruch AI")
        super().mouseReleaseEvent(self.event)


        wybor = None
        ilosc_prob =0
        while True:
            if wybor ==None or len(wybor)<3 :
                chessboard.ai.get_actual_valid_moves()

                wybor = chessboard.ai.choose_action()
                print(wybor)
                ilosc_prob+=1
            elif len(wybor)==3: 
                break
            elif ilosc_prob == 50:
                print("AI wpadło w pętlę bez wyjścia")
            else: print("ERROR")


        row, col =wybor[0]
        next_row, next_col = wybor[1]

        #znajdź figurę na danym polu
        items = chessboard.scene.items()
        ilosc_czarnych = 0
        proba = 0
        # for item in items:
        #     if isinstance(item, ChessPiece) and item.color=="black": ilosc_czarnych+=1
        for item in items:
            if isinstance(item, ChessPiece) and item.color=="black":
                if item.currentPosition() == (row, col):
                    print("znaleziono figurę")
                    item.setPos(next_col*64, next_row*64)
                    print("AI wykonało ruch")
                    # ChessboardWidget.show()
                    # item.checkMove()
                    self.zbicie = item.isNotOccupied()
                    item.checkIfCheckMate()
                    chessboard.switchClock(item.color)
                    chessboard.ai.update_Q((row, col), (next_row, next_col), 1, (next_row, next_col))
                    chessboard.ai.get_actual_valid_moves()
                    if chessboard.scene.turn == False: chessboard.scene.turn = True
                    else: chessboard.scene.turn = False
                    chessboard.addMessage('white turn' if chessboard.scene.turn else 'black turn')
                    break

        super().mouseReleaseEvent(self.event)


        

    def setPiece(self, piece_type, color, size):
        self.filename = f"assets/{color.lower()}/{piece_type.lower()}.png"
        self.setPixmapWithSize(size)

    def setPixmapWithSize(self, size):
        size = round(size)
        pixmap = QPixmap(self.filename).scaled(size, size)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.previous_row, self.previous_col = self.currentPosition()

        #self.printChessTable()

        #print(self.currentPosition())
        if self.scene().mate != True: 
            self.isBeingDragged = True
            self.setPixmapWithSize(self.original_size * 1.2)
        # print(f"{self.piece_type},{self.getValidMoves()}")
            self.valid_moves = None
            self.paintValidMoves()
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.event = event
        self.isBeingDragged = False
        self.clearValidPaints()
        self.setPixmapWithSize(self.original_size)

        self.checkPosition()

        self.checkMove()

        self.checkIfCheckMate()
        chessboard.switchClock(self.color)
        super().mouseReleaseEvent(event)

        if self.scene().mate == False and self.scene().turn == False:
            if chessboard.ai:
                self.ai_move()


        

    def checkIfCheckMate(self):
        #znajdź lokalizację przeciwnego króla
        king = None
        items = self.scene().items()
        for item in items:
            if isinstance(item, ChessPiece):
                if item.piece_type == "king" and item.color != self.color:
                    king = item
                    break
                else:
                    king = None
        if king is not None: 
            row, col = king.currentPosition()
            row, col =king.currentPosition()
        else:
            chessboard.addMessage("Koniec gry")
            self.scene().mate = True
            chessboard.stopClock()

            #pokaż okno z wiadomością o końcu gry
            message_box = QMessageBox()
            message_box.setWindowTitle("Game Over")
            message_box.setText("The game has ended.")
            message_box.exec_()

    # sprawdzenie czy ruch jest poprawny z valid_moves
    def checkMove(self):
        self.colorBool = True if self.color == "white" else False
        self.current_row, self.current_col = self.currentPosition()
        if self.checkTurn(self.colorBool):
            if self.moveIsNotInTheSamePlace():
                if self.isValidMove():
                    if self.isNotOccupied():
                        self.updateChessboardTable()

                        self.scene().turn = not self.scene().turn
                        chessboard.addMessage('white turn' if self.scene().turn else 'black turn')



            
    def printChessTable(self):
        for i in range(8):
            for j in range(8):
                print(f"{self.scene().chessboardTable[i][j]:3}", end=" ")
            print()
        print()

            
    def updateHistoryData(self):
        aktualna_tablica = self.scene().chessboardTable
        self.scene().chessSave["Round Number"].append(self.scene().numerRundy)
        self.scene().chessSave["Chessboard"].append(aktualna_tablica)
        # print(self.scene().chessSave["Chessboard"])
        self.scene().numerRundy += 1

    def updateChessboardTable(self):
        self.current_row, self.current_col = self.currentPosition()
        self.scene().chessboardTable[self.current_row][self.current_col] = self.scene().chessboardTable[self.previous_row][self.previous_col]
        self.scene().chessboardTable[self.previous_row][self.previous_col] = "_"
        self.printChessTable()
        self.updateHistoryData()



    
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
                            print("AI zbiło figurę") if self.color =="black" and chessboard.ai!=None else None
                            chessboard.addMessage("AI zbiło figurę") if self.color =="black" and chessboard.ai!=None else None
                            chessboard.ai.epsilon = 0. if self.color =="black" and chessboard.ai!=None else None
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
        valid_moves, possible= self.getValidMoves(True)
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
        move = f"{name}{col}{row}"
        self.move_history.append(move)
        chessboard.addMessage(move)
        self.saveMoveToSQL(move)
        self.saveToXML(move)
    
    def saveMoveToSQL(self, move):
        conn = sqlite3.connect('chess.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO {chessboard.nazwa_partii} (move) VALUES ('{move}')")

        conn.commit()
        conn.close()
    
    def saveToXML(self, move):
        m = SubElement(chessboard.root,'move')
        m.text = f'{move}'
        tree = ElementTree(chessboard.root)
        tree.write('save.xml')

    def getValidMoves(self, write):

        valid_moves = []

        current_row, current_col = self.currentPosition()
        
        direction = -1 if self.color == "white" else 1
        items = self.scene().items()


        if self.piece_type == "pawn":

            if 0 <= current_row + direction <= 7:
                valid_moves.append((current_row + direction, current_col))

                # pierwszy ruch piona
                if (current_row == 1 and self.color == "black") or (current_row == 6 and self.color == "white"):
                    valid_moves.append((current_row + 2 * direction, current_col))
                                

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
            # Horizontal moves
            for col in range(8):
                if col != current_col:
                # Check if there is a piece between the queen and the target square
                    if any(isinstance(item, ChessPiece) and int(item.y() / 64) == current_row and min(current_col, col) < int(item.x() / 64) < max(current_col, col) for item in items):
                        continue
                valid_moves.append((current_row, col))

            # Vertical moves
            for row in range(8):
                if row != current_row:
                # Check if there is a piece between the queen and the target square
                    if any(isinstance(item, ChessPiece) and int(item.x() / 64) == current_col and min(current_row, row) < int(item.y() / 64) < max(current_row, row) for item in items):
                        continue
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

            # items = self.scene().items()
            for row_offset in [-1, 1]:
                for col_offset in [-1, 1]:
                    target_row = current_row + row_offset
                    target_col = current_col + col_offset
                    while 0 <= target_row <= 7 and 0 <= target_col <= 7:
                        valid_moves.append((target_row, target_col))  # Add squares between figure and bishop
                        if any(isinstance(item, ChessPiece) and int(item.y() / 64) == target_row and int(item.x() / 64) == target_col for item in items):
                            break
                        target_row += row_offset
                        target_col += col_offset

        elif self.piece_type == "queen":
            items = self.scene().items()

            # Horizontal moves
            for col in range(8):
                if col != current_col:
                # Check if there is a piece between the queen and the target square
                    if any(isinstance(item, ChessPiece) and int(item.y() / 64) == current_row and min(current_col, col) < int(item.x() / 64) < max(current_col, col) for item in items):
                        continue
                valid_moves.append((current_row, col))

            # Vertical moves
            for row in range(8):
                if row != current_row:
                # Check if there is a piece between the queen and the target square
                    if any(isinstance(item, ChessPiece) and int(item.x() / 64) == current_col and min(current_row, row) < int(item.y() / 64) < max(current_row, row) for item in items):
                        continue
                    valid_moves.append((row, current_col))

            # Diagonal moves
            for row_offset in [-1, 1]:
                for col_offset in [-1, 1]:
                    target_row = current_row + row_offset
                    target_col = current_col + col_offset
                    while 0 <= target_row <= 7 and 0 <= target_col <= 7:
                        valid_moves.append((target_row, target_col))  
                        if any(isinstance(item, ChessPiece) and int(item.y() / 64) == target_row and int(item.x() / 64) == target_col for item in items):
                            break
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

        for item in items:
            if isinstance(item, ChessPiece):
                items_row = int(item.y() / 64)
                items_col = int(item.x() / 64)
                if item.color == self.color:
                    for move in valid_moves.copy():  # Copy the list to avoid modifying it while iterating
                        # If a piece of the same color is on the target square, remove the move
                        if move == (items_row, items_col):
                            valid_moves.remove((items_row, items_col))


        possible = True if valid_moves else False
        #print(possible, valid_moves)
        self.chessNotation() if write else None
        # print(self.piece_type, valid_moves)
        return valid_moves, possible

# Klasa reprezentująca szachownicę
class ChessboardScene(QGraphicsScene):

    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size
        self.initBoard()
        self.history = []
        self.turn = True #true - white, false - black

    def initBoard(self):
        border = QGraphicsRectItem(0, 0, 8*self.size, 8*self.size)
        border.setPen(QPen(Qt.black, 2))
        self.addItem(border)

        self.mate = False
        self.check =False

        self.initChessboardTable()
        self.initChessSave()

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

        c='w' if color == "white" else 'b'

        if piece_type == "knight":
            name="N"
        elif piece_type == "bishop":
            name="B"
        elif piece_type == "rook":
            name="R"
        elif piece_type == "queen":
            name="Q"
        elif piece_type == "king":
            name="K"
        elif piece_type == "pawn":
            name="P"
        
        self.chessboardTable[row][col] = f"{c}{name}"
        
        self.addItem(piece)

    def initChessboardTable(self):
        self.chessboardTable = [['_' for _ in range(8)] for _ in range(8)]
    
    def initChessSave(self):
        self.numerRundy = 0
        self.chessSave = {"Round Number": [], "Chessboard": []}
    
    def removeAllItems(self):
        items = self.items()
        for item in items:
            if isinstance(item, ChessPiece):
                self.removeItem(item)

class IPandPort(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.ip = QLineEdit(self)
        self.mask = QLineEdit(self)
        self.port = QLineEdit(self)
        self.ip.setPlaceholderText("IP")
        self.mask.setPlaceholderText("Mask prefix")
        self.port.setPlaceholderText("Port")
        self.ip_button = QPushButton("OK", self)

        self.ip_button.setGeometry(10, 120, 150, 30)
        self.ip_button.clicked.connect(self.close)

        self.ip.setGeometry(10, 10, 150, 30)
        self.mask.setGeometry(10, 45, 150, 30)
        self.port.setGeometry(10, 80, 150, 30)
        self.show()
    
    def close(self):
        self.ip = self.ip.text()
        self.port = self.port.text()
        self.mask = self.mask.text()
        print(self.ip, self.mask, self.port)
        return super().close()
    

class PlaybackGameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.numer_rundy = 0

    def initUI(self):
        self.setWindowTitle('Playback Game Window')
        self.button1 = QPushButton('->', self)
        self.button1.move(25, 50)
        self.button2 = QPushButton('<-', self)
        self.button2.move(25, 100)

        self.button1.clicked.connect(self.changeFrameOfGame, 1)
        self.button2.clicked.connect(self.changeFrameOfGame, -1)
        
        self.label = QLabel('Playback Game', self)
        self.label.text = "Runda nr.0"
        self.label.move(25, 10)
        self.setGeometry(300, 300, 150, 150)
        self.show()
    
    def changeFrameOfGame(self, next_frame):
        #odczyt danych z jsona
        ChessboardScene.chessSave = json.load(open('save.json'))
        ilosc_rund = len(ChessboardScene.chessSave["Round Number"])
        # print(ilosc_rund)
        frames = []
        for i in range(ilosc_rund):
            frames.append(ChessboardScene.chessSave["Chessboard"][i])
        print(f'{frames[1]}\n')
        print(frames[2])

        if(self.numer_rundy + next_frame > 0)or(self.numer_rundy + next_frame < ilosc_rund):
            self.label.text = f"Runda nr.{self.numer_rundy + next_frame}"
            self.numer_rundy += next_frame

            #usuń figury z planszy
            chessboard.scene.removeAllItems()
            #dodanie figur z zapisu
            for i in range(8):
                for j in range(8):
                    if frames[self.numer_rundy][i][j] != "_":
                        color = "white" if frames[self.numer_rundy][i][j][0] == "w" else "black"
                        piece = frames[self.numer_rundy][i][j][1]
                        if piece == "N":
                            piece = "knight"
                        elif piece == "B":
                            piece = "bishop"
                        elif piece == "R":
                            piece = "rook"
                        elif piece == "Q":
                            piece = "queen"
                        elif piece == "K":
                            piece = "king"
                        elif piece == "P":
                            piece = "pawn"
                        
                        chessboard.scene.addChessPiece(piece, color, i, j)
                

# Klasa reprezentująca widżet szachownicy
class ChessboardWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.ip = None
        self.mask = None
        self.port = None
        self.ai = None
        self.scene = None
        self.numer_rundy = -1
        self.game_mode = "1 gracz"
        self.nazwa_partii = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        self.initLogWindow()
        self.initMenu()
        self.initClock()
        self.initTextline()
        self.initRadioButtons()
        # self.initIpAndPortWindow()
        self.initUI()
        self.initSQL()
        self.root = Element('root')

    
    def initSQL(self):
        conn = sqlite3.connect('chess.db')
        c = conn.cursor()
        self.nazwa_partii =f"partia_{self.nazwa_partii}"
        
        c.execute(f"CREATE TABLE IF NOT EXISTS {self.nazwa_partii} (move TEXT)")
        conn.commit()
        conn.close()

    def initIpAndPortWindow(self):
        self.ip_and_port = IPandPort()
        self.ip_and_port.show()

    def initRadioButtons(self):
        self.radioButtons1 = QRadioButton("Gracz vs Gracz", self)
        self.radioButtons2 = QRadioButton("AI", self)

        self.radioButtons1.setChecked(True)
        self.radioButtons2.setChecked(False)

        self.radioButtons1.toggled.connect(lambda: self.onClicked(self.radioButtons1))
        self.radioButtons2.toggled.connect(lambda: self.onClicked(self.radioButtons2))

    
    def onClicked(self, radioButton):
        self.game_mode = radioButton.text()
        if radioButton.text() == "AI":
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("AI mode activated. Are you sure?")
            msgBox.setWindowTitle("Confirmation")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                self.setClock(5,5)
                self.ai = True
                self.initAI()
            else:
                self.ai = False

    def initAI(self):
        self.ai = Ai()

    
    def initTextline(self):
        self.textLine = QLineEdit(self)
        self.textLine.returnPressed.connect(self.onReturnPressed)

    def onReturnPressed(self):
        self.numer_rundy =self.textLine.text()
        self.textLine.clear()
        self.addMessage(self.numer_rundy)

    def initMenu(self):

        self.menuBar = QMenuBar(self)

        czas_menu = QMenu("Czas", self)
        self.menuBar.addMenu(czas_menu)
        game_menu = QMenu("Gra", self)
        self.menuBar.addMenu(game_menu)

        #time
        time_pause = QAction('pause', self)
        time_start = QAction('start', self)
        time_30minut = QAction('3|0', self)
        time_55minut = QAction('5|5', self)
        time_10minut = QAction('10 minut', self)

        time_pause.triggered.connect(self.stopClock)
        time_start.triggered.connect(self.startClock)
        time_30minut.triggered.connect(lambda: self.setClock(3,0))
        time_55minut.triggered.connect(lambda: self.setClock(5,5))
        time_10minut.triggered.connect(lambda: self.setClock(10,0))

        czas_menu.addAction(time_pause)
        czas_menu.addAction(time_start)
        czas_menu.addAction(time_55minut)
        czas_menu.addAction(time_30minut)
        czas_menu.addAction(time_10minut)

        #Gra
        save_option = QAction('save', self)
        save_option.triggered.connect(self.save)
        load_save_from_json = QAction('load save', self)
        load_save_from_json.triggered.connect(lambda: self.loadSave())
        playback = QAction('playback saved game', self)
        playback.triggered.connect(lambda: self.playback())

        game_menu.addAction(save_option)
        game_menu.addAction(load_save_from_json)
        game_menu.addAction(playback)

    def playback(self):
        self.playback_window = PlaybackGameWindow()
        self.playback_window.show()

        #usuń figury z planszy
        # self.scene.removeAllItems()
    
    def save(self):
        # zapis do jsona
        with open(f'game_info_{self.nazwa_partii}.json', 'w') as f:
            json.dump({"IP": self.ip, "Mask": self.mask, "Port": self.port, "Game Mode": self.game_mode}, f)
        
        # zapis historii do jsona
        with open('save.json', 'w') as f:
            json.dump(self.scene.chessSave, f)

    
    def loadSave(self):
        self.stopClock()
        #usunięcie aktualych fugir z szachownicy
        self.scene.removeAllItems()
        
        #załadowanie ostatniego zapisu
        ChessboardScene.chessSave = json.load(open('save.json'))
        ilosc_rund = len(ChessboardScene.chessSave["Round Number"])


        # print(self.numer_rundy)
        save = ChessboardScene.chessSave["Chessboard"][int(self.numer_rundy)-1]
        # print(save)

        #dodanie figur z zapisu
        for i in range(8):
            for j in range(8):
                if save[i][j] != "_":
                    color = "white" if save[i][j][0] == "w" else "black"
                    piece = save[i][j][1]
                    if piece == "N":
                        piece = "knight"
                    elif piece == "B":
                        piece = "bishop"
                    elif piece == "R":
                        piece = "rook"
                    elif piece == "Q":
                        piece = "queen"
                    elif piece == "K":
                        piece = "king"
                    elif piece == "P":
                        piece = "pawn"
                        
                    self.scene.addChessPiece(piece, color, i, j)    
        self.startClock()    

    def initClock(self):
        self.clock = ChessClock(5,5)
        self.add=0
        self.clock_label = QLabel(self)
        self.startClock()
        self.updateClock()
        self.clock_label.setAlignment(Qt.AlignTop | Qt.AlignRight)  # This line aligns the clock to the upper right corner

    def setClock(self, time, add):
        self.add = add
        self.clock = ChessClock(time, time)
        self.startClock()
        self.updateClock()
        
    def startClock(self):
        self.clock.start()

    def stopClock(self):
        self.clock.stop()
    
    def switchClock(self, color):
        if self.add != 0:
            if color =="white":
                self.clock.white_time = self.clock.white_time.addSecs(self.add)
            else:
                self.clock.black_time = self.clock.black_time.addSecs(self.add)
        self.clock.switch()
        self.updateClock()

    def updateClock(self):
        white_time, black_time = self.clock.get_time()
        self.clock_label.setText(f"White: {white_time}, Black: {black_time}")
        QTimer.singleShot(1000, self.updateClock)  # update every second
        

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
        self.setGeometry(100, 100, 640, 800)
        self.createChessboard()
        self.show()

    def createChessboard(self):

        layout = QVBoxLayout()
        layout.addWidget(self.clock_label)
        layout.addWidget(self.radioButtons1)
        layout.addWidget(self.radioButtons2)
        layout.addWidget(self.menuBar)
        layout.addWidget(self.textLine)
        view = QGraphicsView(self)
        self.scene = ChessboardScene(64)

        view.setScene(self.scene)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(view)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chessboard = ChessboardWidget()
    sys.exit(app.exec_())
