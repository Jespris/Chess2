"""
Responsible for finding a good move for the AI
"""

import random as r
import Engine


piece_values = {6: 0, 5: 9, 4: 3, 3: 3, 2: 5, 1: 1}
# black wants a negative score, white positive
CHECKMATE = 1000
STALEMATE = 0
CPU_PERFORMANCE = 10
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

white_square_control = [[4, 4, 4, 4, 4, 4, 4, 4],
                     [3, 4, 4, 4, 4, 4, 4, 3],
                     [3, 3, 4, 4, 4, 4, 3, 3],
                     [2, 3, 3, 4, 4, 3, 3, 2],
                     [2, 2, 3, 4, 4, 3, 2, 2],
                     [2, 2, 2, 3, 3, 2, 2, 2],
                     [1, 1, 1, 2, 2, 1, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1]]

black_square_control = [[1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 2, 2, 1, 1, 1],
                        [2, 2, 2, 3, 3, 2, 2, 2],
                        [2, 2, 3, 4, 4, 3, 2, 2],
                        [2, 3, 3, 4, 4, 3, 3, 2],
                        [3, 3, 4, 4, 4, 4, 3, 3],
                        [3, 4, 4, 4, 4, 4, 4, 3],
                        [4, 4, 4, 4, 4, 4, 4, 4]]

piece_position_scores = {3: knight_scores, 6: opening_king_scores if not ENDGAME else endgame_king_scores,
                         5: queen_scores, 2: rook_scores, 4: bishop_scores, 1: white_pawn_scores,
                         -1: black_pawn_scores}

rook_directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
bishop_directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
queen_directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]]

piece_directions = {2: rook_directions, 4: bishop_directions, 5: queen_directions}


def find_random_move(legal_moves):
    return legal_moves[r.randint(0, len(legal_moves) - 1)]


"""def find_best_move_candidate_version(gamestate, legal_moves, return_queue):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies, candidate_moves
    next_move = None
    if len(legal_moves) == 1:
        next_move = legal_moves[0]
    candidate_moves = []
    counter = 0
    BOARD_HASH = {}
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
        actual_depth = 4
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
    return_queue.put((next_move, (counter, actual_depth)))"""


def find_best_move(gamestate, legal_moves, return_queue):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies
    next_move = None
    actual_depth = 1
    counter = 0
    if len(legal_moves) == 1:
        next_move = legal_moves[0]

    if not next_move:
        board_state_copies = 0
        actual_depth = get_good_depth(gamestate)
        if len(gamestate.move_log) <= 10:  # opening
            next_move = gamestate.get_opening()
        if not next_move:
            find_move_nega_max_alpha_beta(gamestate, legal_moves, actual_depth, -CHECKMATE, CHECKMATE, 1 if gamestate.white_to_move else -1, actual_depth)
        print("Looked at", counter, "boardstates,", board_state_copies, "skipped copies, depth", actual_depth)
    return_queue.put((next_move, (counter, actual_depth)))


def find_move_nega_max_alpha_beta(gamestate, legal_moves, depth, alpha, beta, turn_mult, actual_depth):
    global next_move, counter, ENDGAME, BOARD_HASH, board_state_copies
    if depth == 0:
        return turn_mult * score_board(gamestate)

    sorted_moves = sort_legal_moves(legal_moves, gamestate)

    # check if endgame
    if not ENDGAME and len(gamestate.move_log) > 50:
        ENDGAME = evaluate_endgame(gamestate.board)

    max_score = -CHECKMATE
    for move in sorted_moves:
        counter += 1
        gamestate.make_move(move)
        next_moves = gamestate.get_legal_moves()
        board_state = gamestate.boardstates_log[-1]
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


def sort_legal_moves(legal_moves, gamestate):
    # move ordering (check more forcing moves first)
    # only relevant if captures are available aka after first moves
    if len(gamestate.move_log) >= 2:
        sorted_moves = []
        # check each legal move and sort them, captures and checks first
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            gamestate.get_legal_moves()  # to update the in check variable
            if move.piece_captured != 0 or gamestate.in_check:  # move is capture or check
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # then pieces before pawns
        for i in range(len(legal_moves) - 1, -1, -1):
            move = legal_moves[i]
            gamestate.make_move(move)
            if abs(move.piece_moved) != 1:
                sorted_moves.append(move)
                legal_moves.pop(i)
            gamestate.undo_move()
        # append the rest to the new list
        r.shuffle(legal_moves)
        for unforcing_move in legal_moves:
            sorted_moves.append(unforcing_move)
    else:
        sorted_moves = legal_moves
    return sorted_moves


def get_good_depth(gamestate):
    """performance = CPU_PERFORMANCE * 1000
    if len(gamestate.states_depth_log) > 3:
        depth_log = gamestate.states_depth_log
        depth = depth_log[-1][1]
        depth_change = 0
        for i in range(-1, -3, -1):
            if depth_log[i][0] < performance:  # too low depth
                depth_change += 1
            elif depth_log[i][0] > performance * 5:  # too high depth
                depth_change -= 1
        if abs(depth_change) == 2:
            depth += depth_change // 2
    else:
        depth = 4"""
    depth = 4 if not ENDGAME else 6
    return depth


"""def find_move_nega_max_alpha_beta_candidates(gamestate, legal_moves, depth, alpha, beta, turn_mult, actual_depth):
    global candidate_moves, counter, ENDGAME, BOARD_HASH, board_state_copies
    if depth == 0:
        return turn_mult * score_board(gamestate)

    # move ordering (check more forcing moves first)
    # only relevant if captures are available aka after first moves
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
        openings = gamestate.get_opening()
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
    return max_score"""


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
    white_squares_controlled = {}  # dictionary with number of times each square is controlled
    black_squares_controlled = {}
    sq_controlled_weight = 12  # higher = less positional impact
    score = 0
    weights_impact = 10  # higher = less positional impact
    for row in range(8):
        for col in range(8):
            square = gamestate.board[row][col]
            if square != 0:  # not blank
                white = False
                if square != 1 and square != -1:
                    piece_score = piece_position_scores[abs(square)][row][col] / weights_impact
                else:
                    piece_score = piece_position_scores[square][row][col] / weights_impact
                if square > 0:
                    white = True
                score += piece_values[abs(square)] + piece_score if white else -(piece_values[abs(square)] + piece_score)
                # check if the squares controlled by this piece are in the squares controlled list, if not, append
                if abs(square) == 1:  # pawn
                    directions = [-1, 1]
                    for direction in directions:
                        control_square = (row - 1, col + direction) if white else (row + 1, col + direction)
                        if is_inside_board(control_square[0], control_square[1]):
                            if white:
                                if control_square not in white_squares_controlled:
                                    white_squares_controlled[control_square] = 1
                                else:
                                    white_squares_controlled[control_square] += 1
                            else:
                                if control_square not in black_squares_controlled:
                                    black_squares_controlled[control_square] = 1
                                else:
                                    black_squares_controlled[control_square] += 1
                elif abs(square) == 6:  # king
                    directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
                    for direction in directions:
                        new_row = row + direction[0]
                        new_col = col + direction[1]
                        control_square = (new_row, new_col)
                        if is_inside_board(new_row, new_col):
                            if white:
                                if control_square not in white_squares_controlled:
                                    white_squares_controlled[control_square] = 1
                                else:
                                    white_squares_controlled[control_square] += 1
                            else:
                                if control_square not in black_squares_controlled:
                                    black_squares_controlled[control_square] = 1
                                else:
                                    black_squares_controlled[control_square] += 1
                elif abs(square) == 2 or abs(square) == 5 or abs(square) == 4:
                    directions = piece_directions[abs(square)]
                    for direction in directions:
                        for rad in range(1, 8):
                            new_row = row + direction[0] * rad
                            new_col = col + direction[0] * rad
                            control_square = (new_row, new_col)
                            if is_inside_board(new_row, new_col):
                                if white:
                                    if gamestate.board[new_row][new_col] == 0:  # empty square
                                        if control_square not in white_squares_controlled:
                                            white_squares_controlled[control_square] = 1
                                        else:
                                            white_squares_controlled[control_square] += 1
                                    elif gamestate.board[new_row][new_col] != 0:  # a piece blocking larger radius so break
                                        if control_square not in white_squares_controlled:
                                            white_squares_controlled[control_square] = 1
                                        else:
                                            white_squares_controlled[control_square] += 1
                                        break
                                else:
                                    if gamestate.board[new_row][new_col] == 0:  # empty square
                                        if control_square not in black_squares_controlled:
                                            black_squares_controlled[control_square] = 1
                                        else:
                                            black_squares_controlled[control_square] += 1
                                    elif gamestate.board[new_row][new_col] != 0:  # a piece blocking larger radius so break
                                        if control_square not in black_squares_controlled:
                                            black_squares_controlled[control_square] = 1
                                        else:
                                            black_squares_controlled[control_square] += 1
                                        break
                            else:  # not inside board so no point checking larger radius
                                break
                elif abs(square) == 3:  # knight
                    directions = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [-1, 2], [1, -2], [-1, -2]]
                    for direction in directions:
                        new_row = row + direction[0]
                        new_col = col + direction[1]
                        control_square = (new_row, new_col)
                        if 0 <= new_row < 8 and 0 <= new_col < 8:
                            if white:
                                if control_square not in white_squares_controlled:
                                    white_squares_controlled[control_square] = 1
                                else:
                                    white_squares_controlled[control_square] += 1
                            else:
                                if control_square not in black_squares_controlled:
                                    black_squares_controlled[control_square] = 1
                                else:
                                    black_squares_controlled[control_square] += 1

    # compare square control
    white_squares = []
    black_squares = []
    for i in white_squares_controlled:
        if i not in black_squares_controlled:
            white_squares.append(i)
        else:  # disputed square
            if white_squares_controlled[i] - black_squares_controlled[i] > 0:  # white controls square
                white_squares.append(i)
                # print("White controls disputed square", Engine.get_rank_file(i[0], i[1]))
    for j in black_squares_controlled:
        if j not in white_squares_controlled:
            black_squares.append(j)
        else:  # disputed square
            if black_squares_controlled[j] - white_squares_controlled[j] > 0:  # black controls square
                black_squares.append(j)
                # print("Black controls disputed square", Engine.get_rank_file(j[0], j[1]))

    white_control_points = 0
    black_control_points = 0
    for square in white_squares:
        white_control_points += white_square_control[square[0]][square[1]]
    for square in black_squares:
        black_control_points += black_square_control[square[0]][square[1]]

    square_controlled_eval = (white_control_points - black_control_points) / sq_controlled_weight
    # print("Square controlled evaluation:", square_controlled_eval)
    score += square_controlled_eval
    return score


def evaluate_endgame(board):
    pieces = 0
    for row in range(8):
        for col in range(8):
            if board[row][col] != 0 and abs(board[row][col]) != 1:
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
            if board[row][col] > 0:
                score += piece_values[board[row][col][1]]
            elif board[row][col] < 0:
                score -= piece_values[board[row][col][1]]
    return score

