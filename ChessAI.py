import random

pieceScore = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 10, "K": 0}
checkmate = 1000
stalemate = 0
depth = 2


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

# Find best move based on material alone looking 2 move ahead so that it avoid bad trades
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = checkmate
    bestPlayerMove = None
    random.shuffle(validMoves) # Add variety to the player move because many moves results in same score

    for playerMove in validMoves: # The person that mave the next move
        gs.makeMove(playerMove) # Make the move
        opponentMoves = gs.getValidMoves() # Generate opponent moves
        if gs.stalemate:
            opponentMaxScore = stalemate
        elif gs.checkmate:
            opponentMaxScore = -checkmate
        else:
            opponentMaxScore = -checkmate # Opponents best move is -1000 in our perspective or really bad score in our pov
            for opponentMove in opponentMoves: # Going through the opponents' next move
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = checkmate # Make the checkmate move really high score
                elif gs.stalemate:
                    score = stalemate
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board) # Both white and black wants to score high
                if score > opponentMaxScore:
                    opponentMaxScore = score # Highest score opponent can get
                gs.undoMove()
        # Minimizing opponents maxScore
        if opponentMaxScore < opponentMinMaxScore: # If opponents best score lower than their previous best score
            opponentMinMaxScore = opponentMaxScore # becomes best player move
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


# Helper method to make the first recursive call
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, depth, gs.whiteToMove)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

def scoreBoard(gs):
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]] # Scores the white pieces as +
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # Scores the black pieces as -

# Score the board based on material
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]] # Scores the white pieces as +
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # Scores the black pieces as -

    return score