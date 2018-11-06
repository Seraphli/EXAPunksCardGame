from cfg import Cfg


class Card(object):
    def __init__(self, no, pos):
        self.no = no
        self.pos = pos

    def __repr__(self):
        return f'no: {self.no}, pos: {self.pos}'


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
            if len(col) > 1:
                movable_cards.append(col[-1])

            if len(col) > 2:
                stack = False
                for j in range(len(col) - 1, 1, -1):
                    if self.available(col[j - 1].no, col[j].no):
                        stack = True
                    else:
                        break
                if stack:
                    movable_cards.append(col[j])

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
                if s.pos == c.pos:
                    continue
                if self.available(s.no, c.no):
                    actions.append((s, c))
        return actions

    def take_action(self, a):
        card_a, card_b = a
        if card_a.pos[0] == 10:
            self.table[card_b.pos[0]].remove(card_b)
            card_b.pos = (10, 0)
            self.free_slot = card_b
        elif card_b.pos[0] == 10:
            card_b.pos = (card_a.pos[0], len(self.table[card_a.pos[0]]))
            self.table[card_a.pos[0]].append(card_b)
            self.free_slot = Card(-1, (10, 0))
        else:
            cards = [card_b]
            row = card_b.pos[1]
            while len(self.table[card_b.pos[0]]) - 1 > row:
                _card = self.table[card_b.pos[0]][row + 1]
                cards.append(_card)
                row += 1

            for c in cards:
                self.table[c.pos[0]].remove(c)
                c.pos = (card_a.pos[0], len(self.table[card_a.pos[0]]))
                self.table[card_a.pos[0]].append(c)

            # Check if the col need fold
            if len(self.table[card_a.pos[0]]) == 5:
                card_no = self.table[card_a.pos[0]][1].no
                fold = True
                for i in range(2, 5):
                    if card_no != self.table[card_a.pos[0]][i].no:
                        fold = False
                        break
                if fold:
                    self.table[card_a.pos[0]] = [Card(-2, (card_a.pos[0], 0))]

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
                progress += _progress / 6
        return progress / 8

    def clone(self):
        import pickle
        return pickle.loads(pickle.dumps(self))

    @staticmethod
    def available(card_a, card_b):
        if card_a == -1:
            return True
        if card_a < 4 and card_a == card_b:
            return True
        if 4 <= card_a <= 7 and card_b - card_a == 6:
            return True
        if 9 <= card_a <= 12 and card_a - card_b == 4:
            return True
        return False
