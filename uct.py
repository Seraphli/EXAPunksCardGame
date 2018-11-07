from math import *
import random


class Node(object):
    """
    A node in the game tree.
    Note wins is always from the viewpoint of playerJustMoved.
    Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        # the move that got us to this node - 'None' for the root node
        self.move = move
        # 'None' for the root node
        self.parent_node = parent
        self.child_nodes = []
        self.wins = 0
        self.visits = 0
        # future child nodes
        self.untried_moves = state.get_moves()
        # the only part of the state that the Node needs later
        self.player_just_moved = state.player_just_moved

    def uct_select_child(self):
        """
        Use the UCB1 formula to select a child node.
        Often a constant UCTK is applied so we have
        lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits
        to vary the amount of exploration versus exploitation.
        """
        s = sorted(self.child_nodes, key=lambda c: c.Q + sqrt(
            2 * log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, m, s):
        """
        Remove m from untried_moves and add a new child node for this move.
        Return the added child node.
        """
        n = Node(move=m, parent=self, state=s)
        self.untried_moves.remove(m)
        self.child_nodes.append(n)
        return n

    def update(self, result):
        """
        Update this node - one additional visit and result additional wins.
        Result must be from the viewpoint of player_just_moved.
        """
        self.visits += 1
        self.wins += result

    @property
    def Q(self):
        return self.wins / self.visits

    def __repr__(self):
        return '[M:' + str(self.move) + \
               ' W/V:' + str(round(self.wins, 2)) + '/' + str(self.visits) + \
               ' Q:' + str(round(self.Q, 2)) + \
               ' U:' + str(self.untried_moves) + ']'

    def tree_to_string(self, indent):
        s = self.indent_string(indent) + str(self)
        for c in self.child_nodes:
            s += c.tree_to_string(indent + 1)
        return s

    @staticmethod
    def indent_string(indent):
        s = '\n'
        for i in range(1, indent + 1):
            s += '| '
        return s

    def children_to_string(self):
        s = ''
        for c in self.child_nodes:
            s += str(c) + '\n'
        return s


def uct(root_state, iter_max, verbose=False):
    """
    Conduct a UCT search for iter_max iterations starting from root_state.
    Return the best move from the root_state.
    Assumes 2 alternating players (player 1 starts),
    with game results in the range [0.0, 1.0].
    """

    root_node = Node(state=root_state)

    for i in range(iter_max):
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
    return sorted(root_node.child_nodes,
                  key=lambda c: c.Q)[-1].move
