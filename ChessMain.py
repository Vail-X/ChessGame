"""
Main Driver File.
Responsible for handling user input and displaying the current GameStaye object.
"""
import pygame as p
import ChessEngine, ChessAI
from multiprocessing import Process, Queue

boardWidth = boardHeight = 512
moveLogPanelWidth = 250
moveLogPanelHeight = boardHeight
dimension = 8
squareSize = boardHeight // dimension # 64
maxFps = 15
images = {}
humanTurn = None # Enables choosing promoted piece

def loadImages():
    pieces = ["wP", "wB", "wN", "wR", "wQ", "wK", "bP", "bB", "bN", "bR", "bQ", "bK"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (squareSize, squareSize))

def main():
    p.init()
    p.display.set_caption("Chess")
    p.display.set_icon(p.image.load("images/wK.png"))

    screen = p.display.set_mode((boardWidth + moveLogPanelWidth, boardHeight))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Only generate validMoves when move is made or gs changes
    animate = False # Flah variable for when we should animate a move

    loadImages()

    running = True
    squareSelected = () # Keep track of last click (tuple: (row, col))
    playerClicks = [] # Keep track of player clicks (two tuples: [(6, 4), (4,4)])
    gameOver = False
    playerOne = True # If True then Human is playing white otherwise it is AI
    playerTwo = False  # Same but for Black
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos(); # X,Y Location of mouse
                    col = location[0] // squareSize # / by int64 gives whole number
                    row = location[1] // squareSize
                    if squareSelected == (row, col) or col >= 8: # The player clicks the same square (row, col) or user click mouse log
                        squareSelected = () # Deselecting the square
                        playerClicks = [] # Clear player clicks
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected) # Add first and second click

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                animate = True
                                moveMade = True
                                squareSelected = ()  # Resets the squares
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            # Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z and p.key.get_mods() & p.KMOD_CTRL: # Ctrl + Z
                    gs.undoMove()
                    moveMade = True # To recheck the validMoves can just hard code it but its easier
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

                if e.key == p.K_r: # Reset the board when R is press
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        # AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("Thinking...")
                returnQueue = Queue() # Used to pass data between threads
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start() # Call findBestMove(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                print("Done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawEndGameText(screen, "Stalemate" if gs.stalemate else "Black Wins" if gs.whiteToMove else "White Wins")

        clock.tick(maxFps)
        p.display.flip() #Redraw the Display

# Responsible for all the graphics within a current game state
def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

# Draw the squares
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*squareSize, r*squareSize , squareSize, squareSize))

# Highlight square selected and moves for pieces selected
def highlightSquares(screen, gs, validMoves, squareSelected):
    # Highlight last move made
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        s = p.Surface((squareSize, squareSize))
        s.set_alpha(200)  # Transperancy calue 0 is transparent 255 is opaque
        s.fill(p.Color("lightblue"))  # Highlight color for last move
        # Highlight start square
        startSquare = p.Rect(lastMove.startCol * squareSize, lastMove.startRow * squareSize, squareSize, squareSize)
        screen.blit(s, startSquare)
        # Highlight end square
        endSquare = p.Rect(lastMove.endCol * squareSize, lastMove.endRow * squareSize, squareSize, squareSize)
        screen.blit(s, endSquare)

    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # squareSelected is a piece that can be moved
            # Highlight squareSelected
            s = p.Surface((squareSize, squareSize))
            s.set_alpha(100) # Transperancy calue 0 is transparent 255 is opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*squareSize, r*squareSize))

            # Highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*squareSize, move.endRow*squareSize))

    # Potential bug if a discover check occurs because of phantom king
    if gs.inCheck:
        s = p.Surface((squareSize, squareSize))
        s.set_alpha(150)  # Slightly more opaque for emphasis
        s.fill(p.Color("red"))  # Highlight color for the king in check

        # Highlight the king in check
        kingLocation = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
        kingSquare = p.Rect(kingLocation[1] * squareSize, kingLocation[0] * squareSize, squareSize, squareSize)
        screen.blit(s, kingSquare)

        # Highlight the attacker
        for check in gs.checks:
            checkRow = check[0]
            checkCol = check[1]
            attackerSquare = p.Rect(checkCol * squareSize, checkRow * squareSize, squareSize, squareSize)
            screen.blit(s, attackerSquare)

# Draw the pieces on the board using the current Gamestate.board
def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r, c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*squareSize, r*squareSize , squareSize, squareSize))

# Draw move log
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    p.draw.rect(screen, p.Color("Black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog): # Make sure black made a move
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)


    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j] + "  "
        textObject = font.render(text, True, p.Color("White"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

# Animating a move
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    fpSquare = 10 # Frames to move 1 square
    frameCount = (abs(dR) + abs(dC)) * fpSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from it's ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*squareSize, move.endRow*squareSize, squareSize, squareSize)
        p.draw.rect(screen, color, endSquare)

        # Draw captured piece onto the rectangle
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured == 'bP' else move.endRow - 1
                endSquare = p.Rect(move.endCol * squareSize, enPassantRow * squareSize, squareSize, squareSize)
            screen.blit(images[move.pieceCaptured], endSquare)

        # Draw moving piece for each frame
        screen.blit(images[move.pieceMoved], p.Rect(c*squareSize, r*squareSize , squareSize, squareSize))

        # Highlight the last move made

        p.display.flip()
        clock.tick(120)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, False, p.Color("Gray"))
    textLocation = p.Rect(0, 0, boardWidth, boardHeight).move(boardWidth / 2 - textObject.get_width() / 2, boardHeight / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(-2,-2))

if __name__ == "__main__":
    main()