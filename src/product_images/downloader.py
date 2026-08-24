import time
from pathlib import Path

import httpx
from PIL import Image

from product_images.models import ImageCandidate


class ImageDownloader:
    USER_AGENT = (
        "product-image-retrieval/0.1 "
        "(https://github.com/juliopatti/product-image-retrieval)"
    )

    def __init__(
        self,
        output_dir: str | Path = "data/images",
        max_size_mb: int = 15,
        max_retries: int = 3,
    ):
        self.output_dir = Path(output_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_retries = max_retries

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, candidate: ImageCandidate) -> Path:
        response = self._get_with_retry(str(candidate.image_url))

        content_type = response.headers.get("content-type", "")

        if not content_type.startswith("image/"):
            raise ValueError(
                f"URL did not return an image: {content_type}"
            )

        if len(response.content) > self.max_size_bytes:
            raise ValueError(
                f"Image exceeds {self.max_size_bytes} bytes"
            )

        extension = self._extension_from_content_type(content_type)

        filename = (
            f"{candidate.source}_{candidate.source_id}{extension}"
        )

        destination = self.output_dir / filename
        destination.write_bytes(response.content)

        try:
            with Image.open(destination) as image:
                image.verify()
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        return destination

    def _get_with_retry(self, url: str) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = httpx.get(
                url,
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT},
            )

            if response.status_code not in {429, 503}:
                response.raise_for_status()
                return response

            if attempt == self.max_retries:
                response.raise_for_status()

            retry_after = response.headers.get("retry-after")

            if retry_after and retry_after.isdigit():
                wait_seconds = int(retry_after)
            else:
                wait_seconds = 2 ** attempt

            print(
                f"Rate limited ({response.status_code}). "
                f"Retrying in {wait_seconds}s..."
            )

            time.sleep(wait_seconds)

        raise RuntimeError("Unexpected download failure")

    @staticmethod
    def _extension_from_content_type(content_type: str) -> str:
        content_type = content_type.split(";")[0].strip().lower()

        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

        return extensions.get(content_type, ".img")