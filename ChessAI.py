import random

pieceScore = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 10, "K": 0}
knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

# Can try rook with open files ++, rook on same file as queen or other rook
rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[100, 100, 100, 100, 100, 100, 100, 100],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [3, 3, 3, 5, 5, 3, 3, 3],
                   [2, 2, 3, 4, 4, 3, 2, 2],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [2, 2, 3, 4, 4, 3, 2, 2],
                   [3, 3, 3, 5, 5, 3, 3, 3],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [100, 100, 100, 100, 100, 100, 100, 100]]

piecePositionScores = {"wP": whitePawnScores, "bP": blackPawnScores, "N": knightScores, "B": bishopScores, "R": rookScores, "Q" : queenScores}

checkmate = 10000
stalemate = 0
maxDepth = 3

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

# Helper method to make the first recursive call
def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    # findMoveNegaMax(gs, validMoves, maxDepth, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAplhaBeta(gs, validMoves, maxDepth, -checkmate, checkmate,  1 if gs.whiteToMove else -1)
    print(counter)
    returnQueue.put(nextMove)

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

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
                print(move,score)
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
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # Score it positionally
                piecePositionScore = 0
                if square[1] != "K": # No position table for king
                    if square[1] == "P": # For pawns
                        piecePositionScore = piecePositionScores[square][row][col]
                    else: # For other piece
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1 # Scores the white pieces as +
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1 # Scores the black pieces as -

    return score