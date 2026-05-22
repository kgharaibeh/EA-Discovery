from abc import ABC, abstractmethod


class AbstractNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw_data: dict) -> dict: ...
