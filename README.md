# License

The files in this repository are mainly covered under the MIT-License.

`AveryLabels.py` is public domain, as of the author (see header in that file).

# Requirements

You need to have the DejaVu fonts available.

On MacOS with brew:
- `brew tap homebrew/cask-fonts`
- `brew install font-dejavu`

On Linux with apt:
- `sudo apt install fonts-dejavu`

# Usage
## Init venv and activate
`python3 -m venv .venv && . .venv/bin/activate`

## Install requirements
`pip install -r requirements`

## Arguments

| Arg name        | Default   | Remarks                                                                                                                                                                                              |
|-----------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--rows`/`-r`   |     16    | number of rows, default is 16                                                                                                                                                                        |
| `--cols`/`-c`   |     5     | number of columns, default is 5                                                                                                                                                                      |
|  `--year`/`-y`  |     0     | Year can be omitted, default year is 0                                                                                                                                                               |
| `--first`/`-f`  |     1     | First is the starting ASN and can be omitted, default start is 1                                                                                                                                     |
| `--last`/`-l`   |           | Last is the last ASN to generate. It can either be an integer or a value starting with 'x' like 'x3' which means to generate 3 blocks of 16 labels. If omitted, a full sheet of labels is generated. |
| `--url`/`-u`    | ASNxxxxxx | paperless-ngx instance url, ex: `http://192.168.10.1:5000`. If set, the generated QR code will point to that specific document. If not set, the default ASN will be used                             |
| `--output`/`-o` |           | The name of the pdf to generate, default 'output.pdf'                                                                                                                                                |


## Generate labels
generate labels for year 2024, start at 1

`./gen-asn.py --year 24 --first 1`

generate labels for year 2024, start at 1, specifying paperless-ngx instance

`./gen-asn.py --year 24 --first 1 --url http://192.168.1.1:5000`

## Help
see gen-asn.py --help for more details

`./gen-asn.py --help`

## Paperless-ngx

It is possible to make [paperless-ngx](https://docs.paperless-ngx.com/) automatically recognize the ASN from the label and associate it with the document. To do this follow the paperless-ngx [documentation](https://docs.paperless-ngx.com/advanced_usage/#barcodes)

Remember to set the correct prefix. If you use the url option use: `<url>/documents?archive_serial_number=`, for example: `http://192.168.10.1:5000/documents?archive_serial_number=`, otherwise `ASN`.