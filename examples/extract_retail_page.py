from product_images.extractors.retail_page import RetailPageExtractor


url = "https://www.rissul.com.br/banana-prata-1342/p"

extractor = RetailPageExtractor()

result = extractor.extract(url)

print("Título:", result["title"])
print("Imagem:", result["image_url"])