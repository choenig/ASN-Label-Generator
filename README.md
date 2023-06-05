# License

The files in this repository are mainly covered under the MIT-License.

`AveryLabels.py` is public domain, as of the author (see header in that file).

# Requirements

You need to have the DejaVu fonts available.

On MacOS with brew:

    brew tap homebrew/cask-fonts
    brew install font-dejavu

# Usage

    # init venv and activate
    python3 -m venv .venv && . .venv/bin/activate

    # install requirements
    pip install -r requirements

    # generate labels for year 2023, start at 1, create 16x2 labels
    ./gen-asn.py :81:x3 23:1:x2

    # see gen-asn.py --help for more details
    ./gen-asn.py --help
