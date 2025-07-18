#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0*/ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

# pylint: disable=missing-module-docstring, missing-class-docstring, import-error,import-outside-toplevel

from zodiac.toga.app import main

if __name__ == "__main__":
    import sys

    if sys.argv[0]:
        server = sys.argv[0]
    else:
        server = "http://127.0.0.1:8188"
    main(url=server).main_loop()
