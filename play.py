import pyautogui
import cv2
from PIL import ImageGrab
from util import get_path

# heart 红桃
# spade 黑桃
# club 梅花
# diamond 方块

CardNo = {
    0: 'heart',
    1: 'spade',
    2: 'club',
    3: 'diamond',
    4: 'red_10',
    5: 'red_9',
    6: 'red_8',
    7: 'red_7',
    8: 'red_6',
    9: 'black_10',
    10: 'black_9',
    11: 'black_8',
    12: 'black_7',
    13: 'black_6',
}


class Cfg(object):
    COL = 9
    ROW = 4
    X0 = 370
    Y0 = 464
    X_INTERVAL = 134
    Y_INTERVAL = 30
    W = 15
    H = 15


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
        self.table = []
        for i in range(Cfg.COL):
            self.table.append([])
            for j in range(Cfg.ROW):
                x = Cfg.X0 + i * Cfg.X_INTERVAL
                y = Cfg.Y0 + j * Cfg.Y_INTERVAL
                raw_im = im[y:y + Cfg.H, x:x + Cfg.W, :]
                cv2.imwrite('temp.png', raw_im)
                no = self.get_one_card(raw_im)
                self.table[-1].append(CardNo[no])


def main():
    cvp = CVProc()
    cvp.get_card_table()


if __name__ == '__main__':
    main()
