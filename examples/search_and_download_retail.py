import hashlib

from product_images.downloader import ImageDownloader
from product_images.extractors.retail_page import RetailPageExtractor
from product_images.models import ImageCandidate
from product_images.searchers.web import WebProductSearcher


PRODUCT_NAME = "banana prata"
LIMIT = 10


searcher = WebProductSearcher()
extractor = RetailPageExtractor()
downloader = ImageDownloader(
    output_dir="data/images/retail",
)


results = searcher.search(
    product_name=PRODUCT_NAME,
    limit=LIMIT,
)


for result in results:
    page_url = result["url"]

    print()
    print("Página:", page_url)

    try:
        page = extractor.extract(page_url)

        if not page["image_url"]:
            print("-> Nenhuma imagem encontrada")
            continue

        source_id = hashlib.sha256(
            page_url.encode()
        ).hexdigest()[:12]

        candidate = ImageCandidate(
            source="retail",
            source_id=source_id,
            image_url=page["image_url"],
            page_url=page_url,
        )

        path = downloader.download(candidate)

        print("Produto:", page["title"])
        print("Extração:", page["image_source"])
        print("Imagem:", page["image_url"])
        print("Salvo:", path)

    except Exception as error:
        print(
            "-> ERRO:",
            type(error).__name__,
            str(error),
        )