import httpx

from product_images.models import ImageCandidate
from product_images.sources.base import ImageSource


class OpenverseSource(ImageSource):

    API_URL = "https://api.openverse.org/v1/images/"

    USER_AGENT = (
        "product-image-retrieval/0.1 "
        "(https://github.com/juliopatti/product-image-retrieval)"
    )

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ImageCandidate]:

        response = httpx.get(
            self.API_URL,
            params={
                "q": query,
                "page_size": limit,
            },
            timeout=20,
            headers={
                "User-Agent": self.USER_AGENT,
            },
        )

        response.raise_for_status()

        data = response.json()

        candidates = []

        for item in data.get("results", []):
            image_url = item.get("thumbnail") or item.get("url")

            if not image_url:
                continue

            candidate = ImageCandidate(
                source="openverse",
                source_id=item["id"],
                image_url=image_url,
                page_url=item.get("foreign_landing_url"),
                width=item.get("width"),
                height=item.get("height"),
                mime_type=None,
                license=item.get("license"),
                license_url=item.get("license_url"),
                author=item.get("creator"),
            )

            candidates.append(candidate)

        return candidates