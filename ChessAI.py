import random

pieceScore = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 10, "K": 0}
checkmate = 1000
stalemate = 0
maxDepth = 1


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

# Helper method to make the first recursive call
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    # findMoveMinMax(gs, validMoves, maxDepth, gs.whiteToMove)
    counter = 0
    findMoveNegaMax(gs, validMoves, maxDepth, 1 if gs.whiteToMove else -1)
    # findMoveNegaMaxAplhaBeta(gs, validMoves, maxDepth, -checkmate, checkmate,  1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

    if whiteToMove:
        maxScore = -checkmate # Worst score for white
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == maxDepth: # Make sure we only make move at the top of the recursion
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = checkmate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == maxDepth:  # Make sure we only make move at the top of the recursion
                    nextMove = move
            gs.undoMove()
        return minScore

# Same as MinMax but only 1 for loop
def findMoveNegaMax(gs, validMoves, depth, turnMultipler):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultipler * scoreBoard(gs)

    maxScore = -checkmate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultipler) # Opp best score is worse score for us so we put - to negate
        if score > maxScore:
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
    return maxScore

# Alpha is current max so we start at lowest possible score, Beta is current min so we start at the highest score possible
def findMoveNegaMaxAplhaBeta(gs, validMoves, depth, alpha, beta, turnMultipler):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultipler * scoreBoard(gs)

    # Move Ordering - Implement Later
    maxScore = -checkmate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAplhaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultipler) # Opp best score is worse score for us so we put - to negate
        if score > maxScore:
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: #Pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


# Positive is good for white, negative is good for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -checkmate # Black wins
        else:
            return checkmate # White wins
    elif gs.stalemate:
        return stalemate

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]] # Scores the white pieces as +
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # Scores the black pieces as -

    return score

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