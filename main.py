"""Entry program for make.fun's "Sum up 20 November's world news in one
image" bounty (news-image-20261120).

The repository holds the finished front page in entry.png, typeset by
compose.py.  This program copies it, byte for byte, into the output
directory: $MAKEFUN_OUTPUT_DIR outside the grader's container, /output
inside it.  Standard library only, no network, fully deterministic --
every run writes exactly the same bytes.
"""

import os
import shutil
from pathlib import Path


def main():
    src = Path(__file__).with_name("entry.png")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
