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

from urllib.parse import urlparse

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


def my_url(arg):
    url = urlparse(arg)
    if all((url.scheme, url.netloc)):
        return f"{url.scheme}://{url.netloc}"
    raise ArgumentTypeError('Invalid URL')


def parse_cfg(args):
    if not args.last:
        # generate one page full of labels
        last = args.first + args.rows * args.cols - 1
    elif args.last.startswith("x"):
        # generate n columns of labels
        last = args.first + args.rows * int(args.last[1:]) - 1
    else:
        # generate labels from first-last
        last = int(args.last)
    return (args.year, args.first, last)


def values(year, sn):
    id4 = f"{sn:04d}"
    asn = f"ASN{year:02d}{id4}"
    zero4 = "0" * (4 - math.ceil(math.log(sn+1, 10)))
    fg_color = colors[year % len(colors)]
    return (id4, asn, zero4, fg_color)

def render(canvas: canvas.Canvas, idx, w, h, data, url):
    (year, sn) = data[idx]
    (id4, asn, zero4, fg_color) = values(year, sn)

    # qr code
    if url is None:
        qr = QRCodeImage(asn, size=14.8*mm, border=0)
    else:
        qr = QRCodeImage(f"{url}/documents?archive_serial_number={year:02d}{id4}", size=14.8*mm, border=0)
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
    parser = argparse.ArgumentParser(description='Generate ASN')

    parser.add_argument(
        '--rows',
        '-r',
        default=16,
        type=int,
        help=f"Rows can be omitted, default rows is 16."
    )

    parser.add_argument(
        '--cols',
        '-c',
        default=5,
        type=int,
        help=f"Cols can be omitted, default cols is 5."
    )

    parser.add_argument(
        '--year',
        '-y',
        default=0,
        type=int,
        help=f"Year can be omitted, default year is 0."
    )

    parser.add_argument(
        '--first',
        '-f',
        default=1,
        type=int,
        help="First is the starting ASN and can be omitted, default start is 1."
    )

    parser.add_argument(
        '--last',
        '-l', 
        help=f"""Last is the last ASN to generate. It can either be an integer or a value starting with 'x' like 'x3' which means to 
        generate 3 blocks of labels. If omitted, a full sheet of labels is generated."""
    )
    
    parser.add_argument(
        "--url",
        "-u",
        type=my_url,
        help="Paperless-ngx instance url, ex: `http://192.168.10.1:5000`. If set, the generated QR code will point to that specific document. If not set, the default ASN will be used",
    )

    parser.add_argument(
        '--output',
        '-o',
        dest='output',
        metavar='PDF',
        default='output.pdf',
        help="The name of the pdf to generate, default 'output.pdf'"
    )

    args = parser.parse_args()

    (year, first, last) = parse_cfg(args)
    data = [[year, x] for x in range(first, last+1)]

    # reportlab.rl_config.TTFSearchPath.append(os.path.join(os.path.dirname(__file__), 'fonts'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-Bold',        'DejaVuSansMono-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-BoldOblique', 'DejaVuSansMono-BoldOblique.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono-Oblique',     'DejaVuSansMono-Oblique.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSansMono',             'DejaVuSansMono.ttf'))

    label = AveryLabels.AveryLabel(4732)
    output_pdf = f"{args.output}.pdf" if not args.output.endswith(".pdf") else args.output
    label.open(output_pdf)
    label.render(render, len(data), data, args.url)
    label.close()


if __name__ == "__main__":
    sys.exit(main())
