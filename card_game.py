from cfg import Cfg


class CardGame(object):
    def __init__(self, table):
        self.table = table
        self.free_slot = -1

    def get_action(self):
        last_card = []
        for col in self.table:
            last_card.append(col[-1])

        actions = []
        for i in range(Cfg.COL - 1):
            for j in range(i + 1, Cfg.COL):
                if self.available(last_card[i], last_card[j]):
                    actions.append((i, j))
                if self.available(last_card[j], last_card[i]):
                    actions.append((j, i))

        if self.free_slot == -1:
            for i in range(Cfg.COL):
                if last_card[i] >= 0:
                    actions.append((10, i))

        # TODO: 一叠一起移动
        for i in range(Cfg.COL):
            for j in range(len(self.table[i]), 1):
                pass
        return actions

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
