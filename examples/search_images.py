import argparse

from product_images.downloader import ImageDownloader
from product_images.sources.wikimedia import WikimediaSource


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
        help="Number of images to retrieve",
    )

    args = parser.parse_args()

    source = WikimediaSource()
    downloader = ImageDownloader()

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