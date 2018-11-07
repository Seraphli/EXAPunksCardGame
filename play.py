import pyautogui
import cv2
from PIL import ImageGrab
from util import get_path
from card_game import CardGameState
import copy
from cfg import CardNo, Cfg
from auto_play import uct_play_game


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
        im = ImageGrab.grabclipboard()
        assert im is not None, 'Take a snapshot first!'
        im.save('snapshot.png', 'PNG')
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


def main():
    cvp = CVProc()
    table, readable_table = cvp.get_card_table()
    cg = CardGameState(copy.deepcopy(table))
    moves = uct_play_game(cg)


if __name__ == '__main__':
    main()
