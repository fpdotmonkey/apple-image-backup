"""
usage: copy_to_pictures.py [-h] [--source-directory SOURCE_DIRECTORY]
                           [--target-directory TARGET_DIRECTORY]

Copies pictures from a directory to a photos directory.

optional arguments:
  -h, --help            show this help message and exit
  --source-directory SOURCE_DIRECTORY
                        The directory from which pictures are being copied.
                        (default: ./)
  --target-directory TARGET_DIRECTORY
                        The directory to which pictures will be sent.
                        (default: ~/Pictures/)

The photos will be stored in a directory structure that reflects the creation
date of the photos as known by the EXIF metadata. Namely, the directory will
be TARGET_DIRECTORY/YYYY/mm/dd/[image_name] where YYYY is the 4-digit year, mm
the 2-digit month, and dd the 2-digit day.
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import os
import shutil

import exifread  # type: ignore
from progressbar import ProgressBar  # type: ignore


def main():
    """Main."""
    parser = ArgumentParser(
        description="Copies pictures from a directory to a photos directory.",
        epilog=(
            "The photos will be stored in a directory structure that"
            " reflects the creation date of the photos as known by the"
            " EXIF metadata. Namely, the directory will be"
            " TARGET_DIRECTORY/YYYY/mm/dd/[image_name] where YYYY is"
            " the 4-digit year, mm the 2-digit month, and dd the"
            " 2-digit day."
        ),
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source-directory",
        help=(
            "The directory from which pictures are being copied.  Only"
            " images in the root of the directory will be used."
        ),
        action="store",
        default="./",
    )
    parser.add_argument(
        "--target-directory",
        help="The directory to which pictures will be sent.",
        action="store",
        default="~/Pictures/",
    )

    args = parser.parse_args()

    source_directory = os.path.expanduser(args.source_directory)
    if source_directory[-1] != "/":
        source_directory = source_directory + "/"

    target_directory = os.path.expanduser(args.target_directory)
    if target_directory[-1] != "/":
        target_directory = target_directory + "/"

    with os.scandir(source_directory) as image_directory:
        image_paths = [image for image in image_directory if image.is_file()]

    with ProgressBar(
        max_value=len(image_paths), redirect_stdout=True
    ) as progress_bar:
        progress = 0
        for image_path in image_paths:
            try:
                with open(image_path, "rb") as image:
                    exif_tags = exifread.process_file(image)
            except OSError:
                print(f"ERROR! Couldn't open {image_path}, skipping.")
                progress += 1
                progress_bar.update(progress)
                continue
            image_datetime = exif_tags.get("EXIF DateTimeOriginal")
            if image_datetime is not None:
                new_path = datetime.strftime(
                    datetime.strptime(
                        str(image_datetime), "%Y:%m:%d %H:%M:%S"
                    ),
                    target_directory + "%Y/%m/%d/",
                )
            else:
                new_path = target_directory

            if not os.path.isdir(new_path):
                os.makedirs(new_path)

            shutil.copy2(image_path, new_path)
            progress += 1
            progress_bar.update(progress)


if __name__ == "__main__":
    main()
