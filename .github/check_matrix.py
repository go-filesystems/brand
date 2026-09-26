"""Counts the whole brand matrix, per subject.

⛔ This exists because a kit was once laid down by hand -- on a day the pipeline's
image library was missing -- and the organisation lived for a week with three of the
seven format families and avatars at 400px instead of 512. Nobody saw it: every check
that existed tested something that WAS there.

⛔ And it is Python rather than shell because the first version used a bash
associative array, which needs bash 4. macOS ships 3.2, so it failed with "unbound
variable" -- and printed that the kit passed, because the failure was not the one the
exit status was watching. A guard that cannot run must SAY so, which is what the
subject-count floor below is for.
"""

import os
import struct
import sys

WANT = {"svg": 3, "png": 24, "jpg": 8, "avatar": 1, "ico": 1, "icns": 1, "social": 1}
SIZES = {"avatar": (512, 512), "social": (1280, 640)}


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def main():
    if not os.path.isdir("social"):
        print("::error::no social/ directory: this is not a brand kit")
        return 1
    subjects = sorted(
        os.path.splitext(n)[0] for n in os.listdir("social") if n.endswith(".png")
    )
    # A sweep that cannot read reports zero, and zero subjects would make every
    # assertion below vacuously true.
    if len(subjects) < 2:
        print(f"::error::found {len(subjects)} subjects in social/, which cannot be right")
        return 1
    print(f"checking {len(subjects)} subjects against {len(WANT)} format families")

    bad = 0
    for s in subjects:
        for family, want in WANT.items():
            n = 0
            for root, _, files in os.walk(family):
                n += sum(1 for f in files if os.path.splitext(f)[0] == s)
            if n != want:
                print(f"::error::{s}: {family} has {n} files, want {want}")
                bad = 1

    # The avatar is what GitHub shows and it was 400px the last time this went
    # wrong; the banner is what a README shows. Their pixels are checked, not only
    # their existence.
    for family, (w, h) in SIZES.items():
        for s in subjects:
            path = os.path.join(family, s + ".png")
            if not os.path.isfile(path):
                continue
            gw, gh = png_size(path)
            if (gw, gh) != (w, h):
                print(f"::error::{s}: {family} is {gw}x{gh}, want {w}x{h}")
                bad = 1

    print("every subject carries every family" if not bad else "the matrix is incomplete")
    return bad


if __name__ == "__main__":
    sys.exit(main())
