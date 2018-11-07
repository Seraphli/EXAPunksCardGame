from tqdm import trange
from uct import Node
import random
import sys
import copy


def dfs_play_game(cg, actions):
    if cg.game_over():
        return True, actions
    if len(actions) > 100:
        return False, actions
    a = cg.get_action()
    for _a in a:
        _actions = copy.deepcopy(actions)
        _actions.append(_a)
        _cg = cg.clone()
        _cg.take_action(_a)
        res = dfs_play_game(_cg, _actions)
        if res[0]:
            return True, res[1]
    return False, actions


def uct(root_state, iter_max, verbose=False, max_depth=50):
    root_node = Node(state=root_state)

    for _ in trange(iter_max, file=sys.stdout):
        node = root_node
        state = root_state.clone()
        depth = 0
        moves = []

        # Select
        # node is fully expanded and non-terminal
        while not node.untried_moves and node.child_nodes:
            node = node.uct_select_child()
            moves.append(node.move)
            state.do_move(node.move)
            depth += 1

        # Expand
        # if we can expand (i.e. state/node is non-terminal)
        if node.untried_moves:
            m = random.choice(node.untried_moves)
            moves.append(m)
            state.do_move(m)
            # add child and descend tree
            node = node.add_child(m, state)
            depth += 1

        # Rollout - this can often be made orders of magnitude quicker
        # using a state.get_random_move() function
        # while state is non-terminal
        while not state.game_over() and depth <= max_depth:
            m = random.choice(state.get_moves())
            moves.append(m)
            state.do_move(m)
            depth += 1

        if state.get_result(node.player_just_moved) == 1.0:
            return moves

        # Backpropagate
        # backpropagate from the expanded node and work back to the root node
        while node is not None:
            # state is terminal. Update node with result
            # from POV of node.playerJustMoved
            node.update(state.get_result(node.player_just_moved))
            node = node.parent_node

    # Output some information about the tree - can be omitted
    if verbose:
        print(root_node.tree_to_string(0))
    else:
        print(root_node.children_to_string())

    # return the move that was most visited
    return sorted(root_node.child_nodes, key=lambda c: c.Q)[-1].move


def uct_play_game(cg):
    max_depth = 100
    moves = []
    _cg = cg.clone()
    while not cg.game_over() and max_depth > 0:
        a_n = len(cg.get_moves())
        if a_n == 1:
            m = cg.get_moves()[0]
        else:
            m = uct(cg, min(a_n * 400, 2000), max_depth=max_depth)
            if isinstance(m, list):
                moves.extend(m)
                break
        moves.append(m)
        cg.do_move(m)
        max_depth -= 1

    for move in moves:
        _cg.do_move(move)
    print(_cg.game_over())
    print(_cg.game_progress())
    return moves


def debug_play_game(cg):
    import pickle
    with open('moves.pkl', 'rb') as f:
        moves = pickle.load(f)
    for move in moves:
        cg.do_move(move)
    print(cg.game_over())
    print(cg.game_progress())
    for col in cg.table:
        print(col)
