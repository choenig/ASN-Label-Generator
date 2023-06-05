#!/usr/bin/env python3

# Copyright © 2023 Christian Hönig
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import AveryLabels

from reportlab.lib.units import mm, cm
from reportlab_qrcode import QRCodeImage
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from functools import partial

import argparse
import sys
import math

# colors are used to simply distinguish consecutive
colors = [
    "#fc990f",
    "#cec323",
    "#53adfc",
    "#b53834",
    "#4fce46",
    "#6374e2",
    "#55d1ac",
    "#ff0090",
]


# sheet config
ROWS = 16
COLS = 5
CELLS = ROWS*COLS


def parse_cfg(cfg):
    # 23:1:16
    # 23:1:x3
    parts = cfg.split(":")
    if len(parts) != 3:
        print(f"Error: invalid config: {cfg}")
        return (0, 0, 0)

    year  = int(parts[0]) if parts[0] else 0
    first = int(parts[1]) if parts[1] else 1
    if not parts[2]:
        # generate one page full of labels
        last = first + ROWS * COLS - 1
    elif parts[2].startswith("x"):
        # generate n columns of labels
        last = first + ROWS * int(parts[2][1:]) - 1
    else:
        # generate labels from first-last
        last = int(parts[2])
    return (year, first, last)


def values(year, sn):
    id4 = f"{sn:04d}"
    asn = f"ASN{year:02d}{id4}"
    zero4 = "0" * (4 - math.ceil(math.log(sn+1, 10)))
    fg_color = colors[year % len(colors)]
    return (id4, asn, zero4, fg_color)


def print_csv(data):
    def _split(l, chunk_size):
        chunked = []
        for i in range(0, len(l), chunk_size):
            chunked.append(l[i:i + chunk_size])
        return chunked

    # split data into columns
    columns = _split(data, ROWS)
    # split columns into pages
    pages = _split(columns, COLS)

    print("ID,Year,ID4,CODE,Zero4,fg")
    for page in pages:
        for r in range(0, ROWS):
            for c in range(0, COLS):
                (year, sn) = page[c][r]
                (id4, asn, zero4, fg_color) = values(year, sn)
                print(f"{sn},{year:02d},{id4},{asn},{zero4},{fg_color}")


def render(canvas: canvas.Canvas, idx, w, h, data):
    (year, sn) = data[idx]
    (id4, asn, zero4, fg_color) = values(year, sn)

    # qr code
    qr = QRCodeImage(asn, size=14.8*mm, border=0)
    qr.drawOn(canvas, 2*mm, 1*mm)

    # bg rect
    canvas.setStrokeColor("black")
    canvas.setFillColor("#e6feff")
    canvas.setLineWidth(0.4*mm)
    canvas.rect(18*mm, 1*mm, 16.0*mm, 14.8*mm, stroke=1, fill=1)
    # 'remove' left border
    canvas.setFillColor("white")
    canvas.rect(17*mm, 0*mm, 1.5*mm, 16.8*mm, stroke=0, fill=1)

    fontSize = 5.5*mm

    # year
    canvas.setFont("DejaVuSansMono-Bold", fontSize)
    canvas.setFillColor("black")
    canvas.drawRightString(w-2.8*mm, 9.5*mm, f"{year:02d}", charSpace=0)

    # zero4
    canvas.setFont("DejaVuSansMono", fontSize)
    canvas.setFillColor("#aaaaaa")
    canvas.drawString(w-16.05*mm, 3*mm, f"{zero4}", charSpace=0)

    # sn
    canvas.setFont("DejaVuSansMono-Bold", fontSize)
    canvas.setFillColor(fg_color)
    canvas.drawRightString(w-2.8*mm, 3*mm, f"{sn}", charSpace=0)


def main():
    parser = argparse.ArgumentParser(description='Generate ASN .csv')

    parser.add_argument('cfg', nargs="+", 
                        help=f"""The configuration in the format <year>:<first>:<last>. 
                        <year> can be omitted, default year is '0'. <first> is the starting ASN and can be omitted, default start is '1'. 
                        <last> is the last ASN to generate. It can either be an integer or a value starting with 'x' like 'x3' which means to 
                        generate 3 blocks of {ROWS} labels. If omitted, a full sheet of labels is generated.""")

    parser.add_argument('--output', dest='output', metavar='PDF', default='output.pdf',
                        help="The name of the pdf to generate, default 'output.pdf'")

    args = parser.parse_args()

    data = []
    for cfg in args.cfg:
        (year, first, last) = parse_cfg(cfg)
        data += [[year, x] for x in range(first, last+1)]

    # fill data to have full pages
    # if len(data) % CELLS != 0:
    #     data += [[0, 0] for i in range(0, 80 - len(data) % CELLS)]
    # print_csv(data)

    # reportlab.rl_config.TTFSearchPath.append(os.path.join(os.path.dirname(__file__), 'fonts'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-Bold',        'DejaVuSansMono-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-BoldOblique', 'DejaVuSansMono-BoldOblique.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-Oblique',     'DejaVuSansMono-Oblique.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono',             'DejaVuSansMono.ttf'))

    label = AveryLabels.AveryLabel(4732)
    output_pdf = f"{args.output}.pdf" if not args.output.endswith(".pdf") else args.output
    label.open(output_pdf)
    label.render(render, len(data), data)
    label.close()


if __name__ == "__main__":
    sys.exit(main())
