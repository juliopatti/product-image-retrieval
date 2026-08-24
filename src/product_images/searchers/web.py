from ddgs import DDGS


class WebProductSearcher:

    def search(
        self,
        product_name: str,
        limit: int = 10,
    ) -> list[dict]:

        query = f"{product_name} supermercado"

        results = DDGS().text(
            query,
            region="br-pt",
            max_results=limit,
        )

        return [
            {
                "title": result["title"],
                "url": result["href"],
                "description": result.get("body"),
            }
            for result in results
        ]