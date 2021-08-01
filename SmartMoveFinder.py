"""
Responsible for finding a good move for the AI
"""

import random as r


piece_values = {'k': 0, 'q': 9, 'b': 3, 'n': 3, 'r': 5, 'p': 1}
# black wants a negative score, white positive
CHECKMATE = 1000
STALEMATE = 0
CPU_PERFORMANCE = 50
ENDGAME = False
BOARD_HASH = {}

knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]]  # TODO: tweak knight scores

opening_king_scores =   [[2, 3, 3, 1, 1, 1, 3, 2],
                 [2, 1, 1, 1, 1, 1, 1, 2],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [2, 1, 1, 1, 1, 1, 1, 2],
                 [2, 3, 3, 1, 1, 1, 3, 2]]  # prefers castles?!?

endgame_king_scores =   [[1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 2, 2, 1, 1, 1],
                         [1, 1, 2, 2, 2, 2, 1, 1],
                         [1, 1, 2, 2, 2, 2, 1, 1],
                         [1, 1, 1, 2, 2, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1]]  # active king


queen_scores = [[2, 1, 1, 1, 1, 1, 1, 2],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [2, 1, 1, 1, 1, 1, 1, 2]]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]]  # allows for fiancheetos

rook_scores =   [[2, 1, 1, 3, 3, 2, 1, 2],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [2, 1, 1, 3, 3, 2, 1, 2]]  # rooks in the center but not really

white_pawn_scores = [[9, 9, 9, 9, 9, 9, 9, 9],
                     [4, 5, 6, 7, 7, 6, 5, 4],
                     [3, 4, 5, 6, 6, 5, 4, 3],
                     [2, 3, 4, 5, 5, 4, 3, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1]]

black_pawn_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 3, 4, 5, 5, 4, 3, 2],
                     [3, 4, 5, 6, 6, 5, 4, 3],
                     [4, 5, 6, 7, 7, 6, 5, 4],
                     [9, 9, 9, 9, 9, 9, 9, 9]]

piece_position_scores = {'n': knight_scores, 'k': opening_king_scores if not ENDGAME else endgame_king_scores,
                         'q': queen_scores, 'r': rook_scores, 'b': bishop_scores, 'wp': white_pawn_scores,
                         'bp': black_pawn_scores}

rook_directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
bishop_directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
queen_directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]]

piece_directions = {'r': rook_directions, 'b': bishop_directions, 'q': queen_directions}


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


def find_best_move(gamestate, legal_moves, return_queue):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies, candidate_moves
    next_move = None
    candidate_moves = []
    counter = 0
    board_state_copies = 0
    performance = CPU_PERFORMANCE * 1000
    if len(gamestate.boardstates_log) > 3:
        actual_depth = gamestate.boardstates_log[-1][1]
        if gamestate.boardstates_log[-1][0] < performance and gamestate.boardstates_log[-2][0] < performance:  # too low depth
            actual_depth += 1
            print("Increased depth!")
        elif gamestate.boardstates_log[-1][0] > performance * 5 and gamestate.boardstates_log[-2][0] > performance * 5:  # too high depth
            actual_depth -= 1
            print("Decreased depth!")
    else:
        actual_depth = 5
    find_move_nega_max_alpha_beta_candidates(gamestate, legal_moves, actual_depth - 1, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1, actual_depth - 1)

    BOARD_HASH = {}
    counter = 0
    if len(candidate_moves) > 1:
        good_moves = []
        candidate_moves.sort(key=lambda x: x[1])  # sort by eval
        best_candidate_eval = candidate_moves[-1][1]  # last in list is best move with bad depth
        for move in range(len(candidate_moves) - 1, -1, -1):
            if candidate_moves[move][1] < best_candidate_eval - abs(best_candidate_eval) / 10:
                candidate_moves.pop(move)
        cand_moves = ''
        candidate_moves.reverse()
        for move in candidate_moves:
            good_moves.append(move[0])
            cand_moves += move[0].get_notation() + ", "
        print("candidate moves:", cand_moves)
        if len(good_moves) > 1:
            find_move_nega_max_alpha_beta(gamestate, good_moves, actual_depth, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1, actual_depth)
        else:
            next_move = good_moves[0]
    else:
        if candidate_moves:
            next_move = candidate_moves[0][0]
    print("Looked at", counter, "boardstates,", board_state_copies, "skipped copies, depth", actual_depth)
    print(gamestate.boardstates_log)
    return_queue.put((next_move, (counter, actual_depth)))


def find_move_nega_max_alpha_beta(gamestate, legal_moves, depth, alpha, beta, turn_mult, actual_depth):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies
    if depth == 0:
        return turn_mult * score_board(gamestate)

    max_score = -CHECKMATE
    for move in legal_moves:
        counter += 1
        gamestate.make_move(move)
        if not ENDGAME and len(gamestate.move_log) > 50:
            ENDGAME = evaluate_endgame(gamestate.board)
        next_moves = gamestate.get_legal_moves()
        board_state = gamestate.get_boardstate()
        if board_state not in BOARD_HASH:
            # print("New board state")
            score = -find_move_nega_max_alpha_beta(gamestate, next_moves, depth - 1, -beta, -alpha, -turn_mult, actual_depth)
            BOARD_HASH[board_state] = score
        else:
            # print("Board state already found!")
            board_state_copies += 1
            score = BOARD_HASH[board_state]
            # print("copied board state evaluated as", score)
        if score > max_score:
            max_score = score
            if depth == actual_depth:
                print("new best move", move.get_notation(), "evaluation:", score)
                next_move = move
        gamestate.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def find_move_nega_max_alpha_beta_candidates(gamestate, legal_moves, depth, alpha, beta, turn_mult, actual_depth):
    global candidate_moves, counter, ENDGAME, BOARD_HASH, board_state_copies
    if depth == 0:
        return turn_mult * score_board(gamestate)

    # move ordering (check more forcing moves first) - implement later
    # only relevant if capures are available aka after first moves
    if len(gamestate.move_log) >= 2:
        sorted_moves = []
        # check each legal move and sort them, captures and checks first
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            if move.piece_captured != '--' or gamestate.in_check:  # move is capture or check
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # then pieces before pawns
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            if move.piece_moved[1] != 'p':
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # append the rest to the new list
        r.shuffle(legal_moves)
        for unforcing_move in legal_moves:
            sorted_moves.append(unforcing_move)
    else:
        openings = gamestate.openings()
        sorted_moves = [openings[r.randint(0, len(openings) - 1)]]

    max_score = -CHECKMATE
    for move in sorted_moves:
        counter += 1
        gamestate.make_move(move)
        if not ENDGAME and len(gamestate.move_log) > 50:
            ENDGAME = evaluate_endgame(gamestate.board)
        next_moves = gamestate.get_legal_moves()
        board_state = gamestate.get_boardstate()
        if board_state not in BOARD_HASH:
            # print("New board state")
            score = -find_move_nega_max_alpha_beta(gamestate, next_moves, depth - 1, -beta, -alpha, -turn_mult, actual_depth)
            BOARD_HASH[board_state] = score
        else:
            # print("Board state already found!")
            board_state_copies += 1
            score = BOARD_HASH[board_state]
            # print("copied board state evaluated as", score)
        if score > max_score:
            max_score = score
            if depth == actual_depth:
                # print("new best move:", move.get_notation(), "evaluation:", score)
                candidate_moves.append((move, score))
        elif score + (abs(max_score) / 10) > max_score:
            if depth == actual_depth:
                # print("semi good move:", move.get_notation(), "evaluation:", score)
                candidate_moves.append((move, score))
        gamestate.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


"""
Score the board
"""


def score_board(gamestate):
    if gamestate.checkmate:
        if gamestate.white_to_move:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE
    elif gamestate.draw:
        return STALEMATE
    white_squares_controlled = []
    black_squares_controlled = []
    sq_controlled_weight = 6
    score = 0
    weights_impact = 8
    for row in range(8):
        for col in range(8):
            square = gamestate.board[row][col]
            if square != '--':  # not blank
                white = False
                if square != 'wp' and square != 'bp':
                    piece_score = piece_position_scores[square[1]][row][col] / weights_impact
                else:
                    piece_score = piece_position_scores[square][row][col] / weights_impact
                if square[0] == 'w':
                    white = True
                score += piece_values[square[1]] + piece_score if white else -(piece_values[square[1]] + piece_score)
                # check if the squares controlled by this piece are in the squares controlled list, if not, append
                if square[1] == 'p':
                    directions = [-1, 1]
                    for direction in directions:
                        control_square = [row - 1, col + direction] if white else [row + 1, col + direction]
                        if white:
                            if [row - 1, col + direction] not in white_squares_controlled and is_inside_board(control_square[0], control_square[1]):
                                white_squares_controlled.append(control_square)
                        else:
                            if [row - 1, col + direction] not in black_squares_controlled and is_inside_board(control_square[0], control_square[1]):
                                black_squares_controlled.append(control_square)
                elif square[1] == 'k':
                    directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
                    for direction in directions:
                        new_row = row + direction[0]
                        new_col = col + direction[1]
                        if white:
                            if [new_row, new_col] not in white_squares_controlled and is_inside_board(new_row, new_col):
                                white_squares_controlled.append([new_row, new_col])
                        else:
                            if [new_row, new_col] not in black_squares_controlled and is_inside_board(new_row, new_col):
                                black_squares_controlled.append([new_row, new_col])
                elif square[1] == 'r' or square[1] == 'q' or square[1] == 'b':
                    directions = piece_directions[square[1]]
                    for direction in directions:
                        for rad in range(1, 8):
                            new_row = row + direction[0] * rad
                            new_col = col + direction[0] * rad
                            if is_inside_board(new_row, new_col):
                                if white:
                                    if [new_row, new_col] not in white_squares_controlled:
                                        if gamestate.board[new_row][new_col] == '--':  # empty square
                                            white_squares_controlled.append([new_row, new_col])
                                        elif gamestate.board[new_row][new_col] != '--':  # a piece blocking larger radius so break
                                            white_squares_controlled.append([new_row, new_col])
                                            break
                                else:
                                    if [new_row, new_col] not in black_squares_controlled:
                                        if gamestate.board[new_row][new_col] == '--':  # empty square
                                            black_squares_controlled.append([new_row, new_col])
                                        elif gamestate.board[new_row][new_col] != '--':  # a piece blocking larger radius so break
                                            black_squares_controlled.append([new_row, new_col])
                                            break
                            else:  # not inside board so no point checking larger radius
                                break
                elif square[1] == 'n':
                    directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
                    for direction in directions:
                        new_row = row + direction[0]
                        new_col = col + direction[1]
                        if white:
                            if [new_row, new_col] not in white_squares_controlled and is_inside_board(new_row, new_col):
                                white_squares_controlled.append([new_row, new_col])
                        else:
                            if [new_row, new_col] not in black_squares_controlled and is_inside_board(new_row, new_col):
                                black_squares_controlled.append([new_row, new_col])
    square_controlled_eval = (len(white_squares_controlled) - len(black_squares_controlled)) / sq_controlled_weight
    score += square_controlled_eval
    return score


def evaluate_endgame(board):
    pieces = 0
    for row in range(8):
        for col in range(8):
            if board[row][col] != '--' and board[row][col][1] != 'p':
                pieces += 1
    if pieces > 4:
        return False
    return True


def is_inside_board(row, col):
    if 0 <= row < 8 and 0 <= col < 8:
        return True
    return False


def score_material(board):
    score = 0
    for row in range(8):
        for col in range(8):
            if board[row][col][0] == 'w':
                score += piece_values[board[row][col][1]]
            elif board[row][col][0] == 'b':
                score -= piece_values[board[row][col][1]]
    return score

