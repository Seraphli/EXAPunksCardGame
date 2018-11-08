import pyautogui
import cv2
import pyscreenshot as ImageGrab
from util import get_path
from card_game import CardGameState
import copy
from cfg import CardNo, Cfg
from auto_play import uct_play_game
import time


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

    def get_card_table(self, im):
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


def convert_pos(idxes):
    if idxes[0] == 10:
        return 1425, 300
    else:
        return (Cfg.X0 + idxes[0] * Cfg.X_INTERVAL,
                Cfg.Y0 + (idxes[1] - 1) * Cfg.Y_INTERVAL)


def perform_moves(moves):
    from direct_input import PressLMouse, ReleaseLMouse
    for move in moves:
        s, c = move
        start_pos = convert_pos(c)
        end_pos = convert_pos(s)
        pyautogui.moveTo(start_pos[0], start_pos[1], duration=0.1)
        time.sleep(0.1)
        PressLMouse(0, 0)
        time.sleep(0.1)
        pyautogui.moveTo(end_pos[0], end_pos[1] + 30, duration=0.1)
        time.sleep(0.1)
        ReleaseLMouse(0, 0)
        time.sleep(0.1)


def test_play():
    im = cv2.imread('snapshot.png')
    cvp = CVProc()
    table, readable_table = cvp.get_card_table(im)
    cg = CardGameState(copy.deepcopy(table))


def debug_play():
    import pickle
    with open('cg.pkl', 'rb') as f:
        cg = pickle.load(f)
    cg.get_moves()


def main():
    from direct_input import PressLMouse, ReleaseLMouse
    # Sleep 5 sec for user to switch to game
    time.sleep(5)
    n_game = 2
    cvp = CVProc()
    for _ in range(n_game):
        # Start new game
        pyautogui.moveTo(1375, 900)
        PressLMouse(0, 0)
        time.sleep(0.1)
        ReleaseLMouse(0, 0)
        time.sleep(12)

        im = ImageGrab.grab()
        im.save('snapshot.png', 'PNG')
        im = cv2.imread('snapshot.png')
        table, readable_table = cvp.get_card_table(im)
        cg = CardGameState(copy.deepcopy(table))
        moves = uct_play_game(cg)
        if moves:
            perform_moves(moves)
            time.sleep(2)


if __name__ == '__main__':
    main()
    # test_play()
    # debug_play()
