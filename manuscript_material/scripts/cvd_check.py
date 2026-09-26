"""Colour-vision-deficiency check: simulate every figure preview under protanopia, deuteranopia, tritanopia and greyscale.

Run from the repository root after the figures:  python manuscript_material/scripts/cvd_check.py
Writes qa/cvd/<figure>_cvd.png (2 x 3 grid: original, three simulations, greyscale). Simulation uses the
Machado, Oliveira and Fernandes (2009) matrices at full severity, applied in linear RGB.
"""
import glob
import os

import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), '..')
M = {'Protanopia': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
     'Deuteranopia': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
     'Tritanopia': [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def simulate(img, m):
    a = to_lin(np.asarray(img, dtype=float) / 255)
    return Image.fromarray((to_srgb(a @ np.array(m).T) * 255).round().astype('uint8'))


def main():
    os.makedirs(os.path.join(OUT, 'qa', 'cvd'), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(OUT, 'figures', 'previews', '*.png')) + glob.glob(os.path.join(OUT, 'extended_data', 'previews', '*.png'))):
        im = Image.open(f).convert('RGB')
        im = im.resize((im.width // 2, im.height // 2))
        panels = [('Original', im)] + [(k, simulate(im, m)) for k, m in M.items()] + [('Greyscale', im.convert('L').convert('RGB'))]
        W, H = im.width, im.height + 30
        grid = Image.new('RGB', (W * 3, H * 2), 'white')
        for i, (name, p) in enumerate(panels):
            x, y = (i % 3) * W, (i // 3) * H
            grid.paste(p, (x, y + 30))
            ImageDraw.Draw(grid).text((x + 10, y + 8), name, fill='black')
        grid.save(os.path.join(OUT, 'qa', 'cvd', os.path.basename(f).replace('.png', '_cvd.png')))
        print('wrote', os.path.basename(f))


if __name__ == '__main__':
    main()
