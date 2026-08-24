from abc import ABC, abstractmethod

from product_images.models import ImageCandidate


class ImageSource(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ImageCandidate]:
        raise NotImplementedError