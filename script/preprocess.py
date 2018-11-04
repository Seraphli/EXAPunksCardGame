# Screen resolution 1920 * 1080
from PIL import ImageGrab
import cv2
from util import get_path
from play import Cfg


def crop_template_from_snapshot():
    im = ImageGrab.grabclipboard()
    assert im is not None, 'Take a snapshot first!'
    im.save(get_path('.') + '/snapshot.png', 'PNG')
    im = cv2.imread(get_path('.') + '/snapshot.png')
    for i in range(Cfg.COL):
        for j in range(Cfg.ROW):
            x = Cfg.X0 + i * Cfg.X_INTERVAL
            y = Cfg.Y0 + j * Cfg.Y_INTERVAL
            raw_template = im[y:y + Cfg.H, x:x + Cfg.W, :]
            cv2.imwrite(get_path('res/raw_template') +
                        f'/{i}_{j}.png', raw_template)


if __name__ == '__main__':
    crop_template_from_snapshot()
