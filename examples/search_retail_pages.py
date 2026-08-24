from product_images.searchers.web import WebProductSearcher


searcher = WebProductSearcher()

results = searcher.search(
    product_name="banana prata",
    limit=10,
)

for i, result in enumerate(results, start=1):
    print()
    print(i)
    print("Título:", result["title"])
    print("URL:", result["url"])