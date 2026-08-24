import json
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


class RetailPageExtractor:

    USER_AGENT = (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "Chrome/120 Safari/537.36"
    )

    def extract(self, url: str) -> dict:
        response = httpx.get(
            url,
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": self.USER_AGENT},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        product_data = self._extract_product_json_ld(soup)

        title = (
            product_data.get("name")
            if product_data
            else None
        ) or self._extract_title(soup)

        if product_data:
            image_url = self._image_from_product(product_data)

            if image_url:
                return {
                    "url": url,
                    "title": title,
                    "image_url": urljoin(url, image_url),
                    "image_source": "json_ld_product",
                }

        image_url = self._extract_og_image(soup, url)

        if image_url:
            return {
                "url": url,
                "title": title,
                "image_url": image_url,
                "image_source": "og_image",
            }

        image_url = self._extract_image_by_alt(
            soup=soup,
            page_url=url,
            title=title,
        )

        return {
            "url": url,
            "title": title,
            "image_url": image_url,
            "image_source": "image_alt" if image_url else None,
        }

    @staticmethod
    def _extract_product_json_ld(
        soup: BeautifulSoup,
    ) -> dict | None:

        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            if not script.string:
                continue

            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue

            product = RetailPageExtractor._find_product(data)

            if product:
                return product

        return None

    @staticmethod
    def _find_product(data) -> dict | None:
        if isinstance(data, list):
            for item in data:
                product = RetailPageExtractor._find_product(item)

                if product:
                    return product

        if isinstance(data, dict):
            item_type = data.get("@type")

            if item_type == "Product":
                return data

            if isinstance(item_type, list) and "Product" in item_type:
                return data

            graph = data.get("@graph")

            if graph:
                return RetailPageExtractor._find_product(graph)

        return None

    @staticmethod
    def _image_from_product(product: dict) -> str | None:
        image = product.get("image")

        if isinstance(image, str):
            return image

        if isinstance(image, list) and image:
            first = image[0]

            if isinstance(first, str):
                return first

            if isinstance(first, dict):
                return first.get("url") or first.get("contentUrl")

        if isinstance(image, dict):
            return image.get("url") or image.get("contentUrl")

        return None

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        h1 = soup.find("h1")

        if h1:
            return h1.get_text(" ", strip=True)

        og_title = soup.find(
            "meta",
            attrs={"property": "og:title"},
        )

        if og_title:
            return og_title.get("content")

        return None

    @staticmethod
    def _extract_og_image(
        soup: BeautifulSoup,
        page_url: str,
    ) -> str | None:

        for attrs in (
            {"property": "og:image"},
            {"name": "twitter:image"},
        ):
            tag = soup.find("meta", attrs=attrs)

            if tag and tag.get("content"):
                return urljoin(page_url, tag["content"])

        return None

    @staticmethod
    def _extract_image_by_alt(
        soup: BeautifulSoup,
        page_url: str,
        title: str | None,
    ) -> str | None:

        if not title:
            return None

        normalized_title = (
            title.lower()
            .replace("-", "")
            .replace(" ", "")
        )

        for image in soup.find_all("img"):
            alt = image.get("alt", "")

            normalized_alt = (
                alt.lower()
                .replace("-", "")
                .replace(" ", "")
            )

            if not normalized_alt:
                continue

            if (
                normalized_alt in normalized_title
                or normalized_title in normalized_alt
            ):
                src = (
                    image.get("src")
                    or image.get("data-src")
                )

                if src:
                    return urljoin(page_url, src)

        return None