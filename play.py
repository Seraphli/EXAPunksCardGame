import pyautogui
import cv2
from PIL import ImageGrab
from util import get_path
from card_game import CardGame
import copy
from cfg import CardNo, Cfg
from tqdm import trange
from uct import Node
import random


class CVProc(object):
    def __init__(self):
        self.templates = {}
        for k in CardNo.keys():
            self.templates[k] = cv2.imread(get_path('res/template') +
                                           f'/{k}.png')

    def get_one_card(self, raw_im):
        for k, v in self.templates.items():
            res = cv2.matchTemplate(raw_im, v,
                                    cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if min_val < 0.001:
                return k

    def get_card_table(self):
        # im = ImageGrab.grabclipboard()
        # assert im is not None, 'Take a snapshot first!'
        # im.save('snapshot.png', 'PNG')
        im = cv2.imread('snapshot.png')
        table = []
        readable_table = []
        for i in range(Cfg.COL):
            table.append([-1])
            readable_table.append(['empty'])
            for j in range(Cfg.ROW + 4):
                x = Cfg.X0 + i * Cfg.X_INTERVAL
                y = Cfg.Y0 + j * Cfg.Y_INTERVAL
                raw_im = im[y:y + Cfg.H, x:x + Cfg.W, :]
                no = self.get_one_card(raw_im)
                if no is not None:
                    table[-1].append(no)
                    readable_table[-1].append(CardNo[no])

        return table, readable_table


def clone(o):
    import pickle
    return pickle.loads(pickle.dumps(o))


def play_game(cg, actions):
    if cg.game_over():
        return True, actions
    if len(actions) > 10:
        return False, actions
    a = cg.get_action()
    l_a = len(a)
    if len(actions) < 5:
        g = trange(l_a)
    else:
        g = range(l_a)
    for a_idx in g:
        _actions = copy.deepcopy(actions)
        _actions.append(clone(a[a_idx]))
        _cg = cg.clone()
        _cg.take_action(_cg.get_action()[a_idx])
        res = play_game(_cg, _actions)
        if res[0]:
            return True, res[1]
    return False, actions


def uct_play_game(root_state, iter_max, verbose=False):
    root_node = Node(state=root_state)

    for _ in trange(iter_max):
        node = root_node
        state = root_state.clone()

        # Select
        # node is fully expanded and non-terminal
        while not node.untried_moves and node.child_nodes:
            node = node.uct_select_child()
            state.do_move(node.move)

        # Expand
        # if we can expand (i.e. state/node is non-terminal)
        if node.untried_moves:
            m = random.choice(node.untried_moves)
            state.do_move(m)
            # add child and descend tree
            node = node.add_child(m, state)

        # Rollout - this can often be made orders of magnitude quicker
        # using a state.get_random_move() function
        # while state is non-terminal
        while state.get_moves():
            state.do_move(random.choice(state.get_moves()))

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
    return sorted(root_node.child_nodes, key=lambda c: c.visits)[-1].move


def main():
    cvp = CVProc()
    table, readable_table = cvp.get_card_table()
    cg = CardGame(copy.deepcopy(table))
    uct_play_game(cg, 2000)
    res = play_game(cg, [])
    print(res)


if __name__ == '__main__':
    main()
