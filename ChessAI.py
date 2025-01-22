import random

pieceScore = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 10, "K": 0}
checkmate = 1000
stalemate = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

# Find best move based on material alone
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whitePlayer else -1
    maxScore = -checkmate
    bestMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkmate:
            score = checkmate
        elif gs.stalemate:
            score = stalemate
        else:
            score = turnMultiplier * scoreMaterial(gs.board)
        if score > maxScore:
            score = maxScore
            bestMove = playerMove
    return bestMove

# Score the board based on material
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score