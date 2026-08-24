import html
import re

import httpx

from product_images.models import ImageCandidate
from product_images.sources.base import ImageSource


class WikimediaSource(ImageSource):

    API_URL = "https://commons.wikimedia.org/w/api.php"

    USER_AGENT = (
        "product-image-retrieval/0.1 "
        "(https://github.com/juliopatti/product-image-retrieval)"
    )

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ImageCandidate]:

        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": 1600,
            "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist",
        }

        response = httpx.get(
            self.API_URL,
            params=params,
            timeout=20,
            headers={
                "User-Agent": self.USER_AGENT,
            },
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", {})

        candidates = []

        for page in pages.values():
            image_info = page.get("imageinfo", [])

            if not image_info:
                continue

            info = image_info[0]
            metadata = info.get("extmetadata", {})

            candidate = ImageCandidate(
                source="wikimedia",
                source_id=str(page["pageid"]),
                image_url=info.get("thumburl", info["url"]),
                page_url=info.get("descriptionurl"),
                width=info.get("thumbwidth", info.get("width")),
                height=info.get("thumbheight", info.get("height")),
                mime_type=info.get("mime"),
                license=self._metadata_value(
                    metadata,
                    "LicenseShortName",
                ),
                license_url=self._metadata_value(
                    metadata,
                    "LicenseUrl",
                ),
                author=self._clean_html(
                    self._metadata_value(
                        metadata,
                        "Artist",
                    )
                ),
            )

            candidates.append(candidate)

        return candidates

    @staticmethod
    def _metadata_value(
        metadata: dict,
        key: str,
    ) -> str | None:
        item = metadata.get(key)

        if not item:
            return None

        return item.get("value")

    @staticmethod
    def _clean_html(value: str | None) -> str | None:
        if value is None:
            return None

        value = re.sub(r"<[^>]+>", "", value)

        return html.unescape(value).strip()