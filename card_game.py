from cfg import Cfg, CardNo, SpecialCardNo


class Card(object):
    def __init__(self, no, pos):
        self.no = no
        self.pos = pos

    def __repr__(self):
        if self.no in CardNo:
            return f'c: {CardNo[self.no]}, pos: {self.pos}'
        else:
            return f'c: {SpecialCardNo[self.no]}, pos: {self.pos}'


class Slot(Card):
    pass


class CardGame(object):
    def __init__(self, table):
        self.table = table
        _table = []
        for i in range(Cfg.COL):
            col = self.table[i]
            _table.append([])
            for j in range(len(col)):
                _table[-1].append(Card(col[j], (i, j)))
        self.table = _table
        self.free_slot = Card(-1, (10, 0))

    def get_action(self):
        movable_cards = []
        # Last card
        for i in range(Cfg.COL):
            col = self.table[i]

            stack = False
            if len(col) > 2:
                stack = False
                for j in range(len(col) - 1, 0, -1):
                    if self.available(col[j - 1].no, col[j].no):
                        stack = True
                    else:
                        break
                if stack:
                    movable_cards.append(col[j])

            if len(col) > 1 and not stack:
                movable_cards.append(col[-1])

        if self.free_slot.no != -1:
            movable_cards.append(self.free_slot)

        available_slots = []
        for i in range(Cfg.COL):
            last_card = self.table[i][-1]
            if last_card.no != -2:
                available_slots.append(last_card)

        if self.free_slot.no == -1:
            available_slots.append(self.free_slot)

        actions = []
        for s in available_slots:
            for c in movable_cards:
                if s.pos[0] == c.pos[0]:
                    continue
                if s.pos[0] == 10 and len(self.table[c.pos[0]]) != c.pos[1]:
                    continue
                if s.no == self.table[c.pos[0]][c.pos[1] - 1]:
                    continue
                if s.pos[0] == 10 and \
                        self.available(self.table[c.pos[0]][c.pos[1] - 1].no,
                                       self.table[c.pos[0]][c.pos[1]].no):
                    continue
                if self.available(s.no, c.no):
                    actions.append((s.pos, c.pos))
        return actions

    def take_action(self, a):
        card_a_pos, card_b_pos = a
        if card_a_pos[0] == 10:
            card_b = self.table[card_b_pos[0]][card_b_pos[1]]
            self.table[card_b_pos[0]].remove(card_b)
            card_b.pos = (10, 0)
            self.free_slot = card_b
        elif card_b_pos[0] == 10:
            card_b = self.free_slot
            card_b.pos = (card_a_pos[0], len(self.table[card_a_pos[0]]))
            self.table[card_a_pos[0]].append(card_b)
            self.free_slot = Card(-1, (10, 0))
        else:
            card_b = self.table[card_b_pos[0]][card_b_pos[1]]
            cards = [card_b]
            row = card_b.pos[1]
            while len(self.table[card_b.pos[0]]) - 1 > row:
                _card = self.table[card_b.pos[0]][row + 1]
                cards.append(_card)
                row += 1

            for c in cards:
                self.table[c.pos[0]].remove(c)
                c.pos = (card_a_pos[0], len(self.table[card_a_pos[0]]))
                self.table[card_a_pos[0]].append(c)

            # Check if the col need fold
            if len(self.table[card_a_pos[0]]) == 5:
                card_no = self.table[card_a_pos[0]][1].no
                if card_no < 4:
                    fold = True
                    for i in range(2, 5):
                        if card_no != self.table[card_a_pos[0]][i].no:
                            fold = False
                            break
                    if fold:
                        self.table[card_a_pos[0]] = [
                            Card(-2, (card_a_pos[0], 0))]

    def game_over(self):
        is_game_over = True
        for col in self.table:
            if len(col) == 1 and (col[0].no == -1 or col[0].no == -2):
                continue
            elif len(col) == 6:
                for j in range(len(col) - 1, 0, -1):
                    if not self.available(col[j - 1].no, col[j].no):
                        is_game_over = False
                        break
            else:
                is_game_over = False
            if not is_game_over:
                break
        if self.free_slot.no != -1:
            is_game_over = False
        if not is_game_over and not self.get_action():
            is_game_over = True
        return is_game_over

    def game_progress(self):
        progress = 0
        for col in self.table:
            if len(col) == 1 and (col[0].no == -1 or col[0].no == -2):
                progress += 1
            elif len(col) == 6:
                _progress = 0
                for j in range(len(col) - 1, 0, -1):
                    if self.available(col[j - 1].no, col[j].no):
                        _progress += 1
                    else:
                        break
                progress += _progress / 5
            else:
                _progress = 0
                for j in range(len(col) - 1, 0, -1):
                    if self.available(col[j - 1].no, col[j].no):
                        _progress += 1
                    else:
                        break
                progress += _progress / len(col)
        return progress / 9

    def clone(self):
        import pickle
        return pickle.loads(pickle.dumps(self))

    @staticmethod
    def available(card_a_no, card_b_no):
        if card_a_no == -1:
            return True
        if card_a_no < 4 and card_a_no == card_b_no:
            return True
        if 4 <= card_a_no <= 7 and card_b_no - card_a_no == 6:
            return True
        if 9 <= card_a_no <= 12 and card_a_no - card_b_no == 4:
            return True
        return False


class CardGameState(CardGame):
    def __init__(self, table):
        super(CardGameState, self).__init__(table)
        self.player_just_moved = 0

    def do_move(self, move):
        self.take_action(move)

    def get_moves(self):
        return self.get_action()

    def get_result(self, playerjm):
        return self.game_progress()
