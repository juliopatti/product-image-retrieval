import argparse

from product_images.downloader import ImageDownloader
from product_images.sources.openverse import OpenverseSource


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "query",
        help="Product name to search for",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    source = OpenverseSource()

    downloader = ImageDownloader(
        output_dir="data/images/openverse",
    )

    images = source.search(
        query=args.query,
        limit=args.limit,
    )

    for image in images:
        path = downloader.download(image)

        print(
            image.source_id,
            image.width,
            image.height,
            image.license,
            "->",
            path,
        )


if __name__ == "__main__":
    main()