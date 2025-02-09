"""
Responsible for storing all the information about the current state of the chess game.
Responsible for determining the valid moves  at the current state of the chess game.
Keep a move log.
"""

import numpy as np
import ChessMain as cm

class GameState():
    def __init__(self):
        # 8x8 2D List
        # First Char: b = Black, w = White
        # Second Char: type of piece
        # -- blank
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ])
        self.moveFunctions = {"P": self.getPawnMoves, "B": self.getBishopMoves, "N": self.getKnightMoves,
                              "R": self.getRookMoves,"Q": self.getQueenMoves, "K": self.getKingMoves,}

        self.moveLog = []
        self.whiteToMove = True
        self.enemyColor = "b"
        self.allyColor = "w"
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = () # Square where enPassant capture is possible
        self.enPassantLog = [self.enPassantPossible] # Store last enPassantPossible to be able to undo enPassant
        # Castling rights
        self.castlingwKs = True
        self.castlingwQs = True
        self.castlingbKs = True
        self.castlingbQs = True
        self.castleRightsLog = [CastleRights(self.castlingwKs, self.castlingbKs, self.castlingwQs, self.castlingbQs)]
        # Can try saving positions

    # Takes a Move and executes it (castling, en-passant, and pawn promotion is not included)
    def makeMove(self, move):
        self.board[move.startRow, move.startCol] = "--"
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log the move to undo later
        self.whiteToMove = not self.whiteToMove # Swap players
        self.enemyColor = "b" if self.whiteToMove else "w"
        self.allyColor = "w" if self.whiteToMove else "b"
        # Update Kings location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.pawnPromotion:
            global promotedPiece
            if cm.humanTurn:
                promotedPiece = input("Promote to Q, R, B, or N: ")
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
            else:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Update enPassantPossible only if pieceMoved is pawn and it moved by 2 squares and left or right have allyColor
        if (move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2 and
                ((move.endCol > 0 and self.board[move.endRow][move.endCol - 1] == self.allyColor + 'P') or
                 (move.endCol < 7 and self.board[move.endRow][move.endCol + 1] == self.allyColor + 'P'))):
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol) # Start col also works
            self.enPassantLog = [self.enPassantPossible]
        else: # Making sure if any other move it removes the possible enPassant
            self.enPassantPossible = ()

        # Enpassant, it removes the pawn on the same starting row but to the end row
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'  # Capture the pawn

        # Castle move
        if move.castleMove:
            if move.endCol == move.startCol + 2: # KingSide castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # Moves rook
                self.board[move.endRow][move.endCol+1] = '--' # Erase old rook
            else: #QueesnSide castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # Moves rook
                self.board[move.endRow][move.endCol - 2] = '--'  # Erase old rook

        # Update castling rights when a king or rook moves
        self.updateCastleRights(move)
        self.checks = [] # Reset check

     # Undo last move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()

            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Switch turn players
            self.enemyColor = "b" if self.whiteToMove else "w"
            self.allyColor = "w" if self.whiteToMove else "b"

            # Update Kings location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo EnPassant
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--' # Remove the pawn that did the enPassant
                self.board[move.startRow][move.endCol] = move.pieceCaptured # Puts the pawn back on the square it was capture from

            # Allow enPassant back again no matter what
            self.enPassantPossible = self.enPassantLog[-1]

            # Undo castling rights
            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1] # Set current castling rights to the last one on the list
            self.castlingwKs = castleRights.wKs
            self.castlingbKs = castleRights.bKs
            self.castlingwQs = castleRights.wQs
            self.castlingbQs = castleRights.bQs

            # Undo castle move
            if move.castleMove:
                if move.endCol - move.startCol == 2:  # KingSide castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # Moves rook back
                    self.board[move.endRow][move.endCol - 1] = '--'  # Erase old rook
                else:  # QueesSide castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]  # Moves rook
                    self.board[move.endRow][move.endCol + 1] = '--'  # Erase old rook

            self.checks = []
            self.checkmate = False
            self.stalemate = False

    # Get all valid moves considering checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: # 1 Check, block or move king
                moves = self.getAllPossibleMoves()

                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]

                pieceChecking = self.board[checkRow][checkCol] #Enemy causing the check
                validSquares = [] # Square that pieces can move to

                # If knight, must capture or move
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8): #Give valid square where a piece need to move to
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # Once you reach the piece that checks stop
                            break
                # Remove all moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K': # Not King
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # Move don't block check or capture piece
                            moves.remove(moves[i])
            else: # Double Check
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

    # Get all moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # Number of rows
            for c in range(len(self.board[r])): # Number of cols in given row
                turn = self.board[r][c][0] # Check the first character of the board 'w' or 'b' or '-'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1] # Check the second character of the board
                    self.moveFunctions[piece](r, c, moves) # Calls the correct function base of what piece it is using a dictionary
        return moves

    # Get all the pawn moves for pawn located at row, col, and add to move list
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            rowDir = -1
            startRow = 6
            kingRow, kingCol = self.whiteKingLocation
        else:
            rowDir = 1
            startRow = 1
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + rowDir][c] == "--": # Move 1 square up
            if not piecePinned or pinDirection == (rowDir, 0):
                moves.append(Move((r, c), (r + rowDir, c), self.board))
                if r == startRow and self.board[r + 2*rowDir][c] == "--": # Move 2 square up
                    moves.append(Move((r, c), (r + 2*rowDir, c), self.board))

        if c-1 >= 0: # Captures left
            if self.board[r + rowDir][c-1][0] == self.enemyColor: # Enemy piece on left
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r + rowDir, c-1), self.board))
            elif (r + rowDir, c-1) == self.enPassantPossible:
                attackingPiece = blockingPiece = False
                if kingRow == r:
                    if kingCol < c: # King is left of the pawn
                        # Inside between the king and pawn, outside range between pawn border
                        insideRange = range(kingCol + 1, c - 1)
                        outsideRange = range(c + 1, 8)
                    else: # King is right of the pawn
                        insideRange = range(kingCol - 1, c, -1)
                        outsideRange = range(c - 2, -1, -1)
                    for i in insideRange:
                        if self.board[r][i] != "--": # If have any other piece besides the enPassant pawn blocks
                            blockingPiece = True
                    for i in outsideRange:
                        square = self.board[r][i]
                        if square[0] == self.enemyColor and (square[1] == 'R' or square[1] == 'Q'): # Attacking piece
                            attackingPiece = True
                        elif square != '--':
                            blockingPiece = True
                if not attackingPiece or blockingPiece: # if there's no attacking piece or there is a blocking piece
                    moves.append(Move((r, c), (r + rowDir, c-1), self.board, enPassant=True))

        if c+1 <= 7: # Captures right
            if self.board[r + rowDir][c+1][0] == self.enemyColor:  # Enemy piece on left
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r + rowDir, c+1), self.board))
            elif (r + rowDir, c + 1) == self.enPassantPossible:
                attackingPiece = blockingPiece = False
                if kingRow == r:
                    if kingCol < c:  # King is left of the pawn
                        # Inside between the king and pawn, outside range between pawn border
                        insideRange = range(kingCol + 1, c)
                        outsideRange = range(c + 2, 8)
                    else:  # King is right of the pawn
                        insideRange = range(kingCol - 1, c + 1, -1)
                        outsideRange = range(c - 1, -1, -1)
                    for i in insideRange:
                         if self.board[r][i] != "--":  # If have any other piece besides the enPassant pawn blocks
                            blockingPiece = True
                    for i in outsideRange:
                         square = self.board[r][i]
                         if square[0] == self.enemyColor and (square[1] == 'R' or square[1] == 'Q'):  # Attacking piece
                             attackingPiece = True
                         elif square != '--':
                             blockingPiece = True
                if not attackingPiece or blockingPiece:  # if there's no attacking piece or there is a blocking piece
                    moves.append(Move((r, c), (r + rowDir, c+1), self.board, enPassant=True))

    # Same but bishop
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        bishopDir = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # Up Left, Down Left, Up Right, Down Right
        for d in bishopDir:
            for i in range(1, 8): # Bishop can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Inside the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == self.enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Friendly piece
                            break
                else:  # Outside the board
                    break

    # Same but knight
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, 1), (-2, -1), (-1, 2), (-1, -2), (2, 1), (2, -1), (1, 2), (1, -2))
        for d in knightMoves:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != self.allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    # Same but rook
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # Can't remove queen from pin on rook, remove it on bishop
                    self.pins.remove(self.pins[i])
                break

        rookDir = ((-1,0),(1,0),(0,-1),(0,1)) # Up, Down, Left, Right
        for d in rookDir:
            for i in range(1, 8): # A Rook can only travel MAX 7 square:
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # Inside the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): # Allows pinned rook to move in the direction or opposite direction of the pin
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == self.enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # Friendly piece
                            break
                else: # Outside the board
                    break

    # Same but queen
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    # Same but king
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # Check if the move is within the board bounds
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != self.allyColor:  # Not an ally piece (empty or enemy piece)
                    if not self.squareUnderAttack(endRow, endCol):
                        moves.append(Move((r, c), (endRow, endCol), self.board))
        self.getCastleMoves(r, c, moves)

    # Generate all the valid castling moves for the current king at r, c and add them to move list
    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return # Can't castle in check
        if (self.whiteToMove and self.castlingwKs) or (not self.whiteToMove and self.castlingbKs):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.castlingwQs) or (not self.whiteToMove and self.castlingbQs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--' and not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, castleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--' and not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, castleMove=True))

    #  Returns if square under attack
    def squareUnderAttack(self, r, c):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == self.allyColor:
                        break
                    elif endPiece[0] == self.enemyColor:
                        pType = endPiece[1]
                        # 5 possibilities here in this complex conditional hits enemy that can check
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) any direction and piece 1  is a queen
                        # 4.) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        # 5.) 1 square away diagonally from king and piece is a pawn (it will check from the direction of the king, so if pawn is white (attack by -1), king will check +1)
                        if ((0 <= j <= 3 and pType == 'R') or
                                (4 <= j <= 7 and pType == 'B') or
                                (i == 1 and pType == 'P' and ((self.enemyColor == 'w' and 6 <= j <= 7) or (self.enemyColor == 'b' and 4 <= j <= 5))) or
                                (pType == 'Q') or (i == 1 and pType == 'K')):
                            return True
                        else:  # Enemy no applying attack
                            break
                else:  # Not on board
                    break
        # Knight Checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == self.enemyColor and endPiece[1] == 'N':  # enemy knight attack king
                    return True

    def checkForPinsAndChecks(self):
        pins = [] # Store location of allied pinned piece and the direction of the pinned from
        inCheck = False
        self.checks = []
        if self.whiteToMove:
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1,0), (0,-1), (1, 0), (0,1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # Store Possible Pin Reset pin
            for i in range(1, 8):
                nRow = startRow + d[0] * i
                nCol = startCol + d[1] * i
                if 0 <= nRow < 8 and 0 <= nCol < 8:
                    endPiece = self.board[nRow][nCol]
                    if endPiece[0] == self.allyColor:
                        if possiblePin == ():
                            possiblePin = (nRow, nCol, d[0], d[1])
                        else: # Second pin
                            break
                    elif endPiece[0] == self.enemyColor:
                        pType = endPiece[1]
                        # 5 possibilities here in this complex conditional hits enemy that can check
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) any direction and piece 1  is a queen
                        # 4.) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        # 5.) 1 square away diagonally from king and piece is a pawn (it will check from the direction of the king, so if pawn is white (attack by -1), king will check +1)
                        if ((0 <= j <= 3 and pType == 'R') or
                                (4 <= j <= 7 and pType == 'B') or
                                (i == 1 and pType == 'P' and ((self.enemyColor == 'w' and 6 <= j <= 7) or (self.enemyColor == 'b' and 4 <= j <= 5))) or
                                (pType == 'Q') or (i == 1 and pType == 'K')):
                            if possiblePin == (): # No piece blocking
                                inCheck = True
                                self.checks.append((nRow, nCol, d[0], d[1])) if (nRow, nCol, d[0], d[1]) not in self.checks else None
                                break
                            else: # Ally is blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # Enemy no applying check or pin
                            break
                else: # Not on board
                    break
        # Knight Checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            nRow = startRow + m[0]
            nCol = startCol + m[1]
            if 0 <= nRow < 8 and 0 <= nCol < 8:
                endPiece = self.board[nRow][nCol]
                if endPiece[0] == self.enemyColor and endPiece[1] == 'N': #enemy knight attack king
                    inCheck = True
                    self.checks.append((nRow, nCol, m[0], m[1])) if (nRow, nCol, m[0], m[1]) not in self.checks else None
        # Uses self.checks because we don't want to reset the checks everytime this method is called, only reset check when a move is made
        return inCheck, pins, self.checks

 # Update castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.castlingwKs = False
            self.castlingwQs = False
        elif move.pieceMoved == "bK":
            self.castlingbKs = False
            self.castlingbQs = False
        elif move.pieceMoved == "wR" and move.startRow == 7:
            if move.startCol == 0: # Left rook
                self.castlingwQs = False
            elif move.startCol == 7: # Right rook
                self.castlingwKs = False
        elif move.pieceMoved == "bR" and move.startRow == 0:
            if move.startCol == 0: # Left rook
                self.castlingbQs = False
            elif move.startCol == 7: # Right rook
                self.castlingbKs = False

        # If rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.castlingwQs = False
                elif move.endCol == 7:
                    self.castlingwKs = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.castlingbQs = False
                elif move.endCol == 7:
                    self.castlingbKs = False

        self.castleRightsLog.append(CastleRights(self.castlingwKs, self.castlingbKs, self.castlingwQs, self.castlingbQs))

class CastleRights():
    def __init__(self, wKs, bKs, wQs, bQs):
        self.wKs = wKs
        self.bKs = bKs
        self.wQs = wQs
        self.bQs = bQs

class Move():
    # Map keys to Values
    # Change coordinates to chest notation
    rowsToRanks = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    ranksToRows = {v: k for k, v in rowsToRanks.items()}
    colsToFiles = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    filesToCols = {v: k for k, v in colsToFiles.items()}

    # En Passant is optional default is empty
    def __init__(self, startSquare, endSquare, board, enPassant = False, castleMove = False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol] # Select the piece moved/first click
        self.pieceCaptured = board[self.endRow][self.endCol] # Select the target place/second click can be "--"

        self.pawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.castleMove = castleMove
        self.enPassant = enPassant
        if enPassant:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP' # Store information of pieceCaptured to be covered later since previously we store it by end.Row and end.Col which is '--'

        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Overriding the equals method, to make a Move instance equal to each other if the ID is same
    def __eq__(self, other):
        if isinstance(other, Move): # Check if other is a Move instance
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        notation = None
        capture = "x" if self.pieceCaptured != "--" else ""

        if self.pieceMoved[1] == "P":  # file of pawn + x + end or end
            notation = (self.colsToFiles[self.startCol] + capture + self.getRankFile(self.endRow,self.endCol)) if capture else self.getRankFile(self.endRow, self.endCol)
            if self.pawnPromotion:
                notation = (self.colsToFiles[self.endCol] + self.rowsToRanks[self.endRow] + promotedPiece)
        else:
            notation = self.pieceMoved[1] + capture + self.getRankFile(self.endRow, self.endCol)
        return notation

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

        # Overiding the str() function
    def __str__(self):
        # Castle Move
        if self.castleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)
        # Pawn Moves
        if self.pieceMoved[1] == "P":
            if self.isCapture:
                moveString = self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                moveString = endSquare
            # Pawn promotion
            if self.endRow == 0 or self.endRow == 7: # Reaching the last rank
                moveString += "=Q"  # Assuming Queen promotion by default
            return moveString
            # Two of the same type of piece moving to a square, Nbd2 if both knights can move to d2
            # 1. Check the board for another instance of the piece and save the location
            # 2. Go through the valid moves and check for a move that starts from the other piece and ends on the same square as the one being moved
            # 3. Append the column/file if they share the row/rank or the row/rank if they share the same column/file

        # Piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare




