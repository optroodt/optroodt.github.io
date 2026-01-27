#!/usr/bin/env python3

import argparse
from os import cpu_count
from pathlib import Path
from multiprocessing import Pool
from PIL import Image

MAX_SIZE = (1920, 1920)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
NUM_PROCESSES = max(4, cpu_count() or 1)


def process_image(path: Path):
    try:
        with Image.open(path) as img:
            # Normalize mode where needed
            if img.mode in ("P", "RGBA"):
                img = img.convert("RGB")

            # Resize in place, preserving aspect ratio
            img.thumbnail(MAX_SIZE, Image.LANCZOS)

            # Save without EXIF / metadata
            save_kwargs = {}
            if path.suffix.lower() in {".jpg", ".jpeg"}:
                save_kwargs["quality"] = 90
                save_kwargs["optimize"] = True

            img.save(path, **save_kwargs)

            return f"Processed: {path}"
    except Exception as e:
        return f"Failed: {path} ({e})"


def collect_images(root: Path):
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Resize images to max 1920x1920, keep format, strip EXIF."
    )
    parser.add_argument("path", type=Path, help="Root directory to process")
    args = parser.parse_args()

    if not args.path.exists():
        raise FileNotFoundError(f"Path does not exist: {args.path}")

    images = collect_images(args.path)

    if not images:
        print("No images found.")
        return

    with Pool(processes=NUM_PROCESSES) as pool:
        print(f"Using {NUM_PROCESSES} processes")
        for result in pool.imap_unordered(process_image, images):
            print(result)


if __name__ == "__main__":
    main()

