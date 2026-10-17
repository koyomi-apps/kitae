#!/usr/bin/env python3
"""Makes the web-sized screenshots in screens/ from the apps' own repositories.

    python3 scripts/make_screens.py PATH/TO/kitae-ios PATH/TO/kitae-android

iPhone: docs/screenshots/NAME-light.png and NAME-dark.png, used as they are.
Android: fastlane/metadata/android/en-US/images/phoneScreenshots/2.png to 9.png,
which come in a phone frame, so the screen is cut out of the frame first.
Everything is resized to 720 px wide and saved as WebP. Needs Pillow and NumPy.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

WIDTH = 720
INSET = 8  # pixels cut off the Android screen's edge, to lose the frame's last bits
IOS = ["today", "workout", "exercise-progress", "exercise-howto", "history", "you"]
# Android name: (light file, dark file)
ANDROID = {"plan": (2, 3), "today": (4, 5), "workout": (6, 7), "you": (8, 9)}


def save(image: Image.Image, path: Path) -> None:
    image = image.convert("RGB")
    image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS)
    image.save(path, "WEBP", quality=82, method=6)
    print(path.name, image.size)


def screen_box(folder: Path) -> tuple[int, int, int, int]:
    """Where the screen is inside the frame, found on a light screenshot (they share a frame)."""
    pixels = np.array(Image.open(folder / "4.png").convert("RGB")).astype(int)
    paper = np.array([253, 249, 240])

    def first(line, reverse=False):
        for k in range(len(line) - 1, -1, -1) if reverse else range(len(line)):
            if np.abs(line[k] - paper).max() <= 3:
                return k

    row, col = pixels[1500], pixels[:, 200]
    return (first(row) + INSET, first(col) + INSET, first(row, True) - INSET, first(col, True) - INSET)


def main(ios: Path, android: Path) -> None:
    out = Path(__file__).resolve().parent.parent / "screens"
    out.mkdir(exist_ok=True)
    for name in IOS:
        for mode in ("light", "dark"):
            save(Image.open(ios / "docs" / "screenshots" / f"{name}-{mode}.png"), out / f"ios-{name}-{mode}.webp")
    folder = android / "fastlane" / "metadata" / "android" / "en-US" / "images" / "phoneScreenshots"
    box = screen_box(folder)
    for name, (light, dark) in ANDROID.items():
        for mode, number in (("light", light), ("dark", dark)):
            save(Image.open(folder / f"{number}.png").crop(box), out / f"android-{name}-{mode}.webp")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
