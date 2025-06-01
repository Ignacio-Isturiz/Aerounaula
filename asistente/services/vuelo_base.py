from abc import ABC, abstractmethod

class BuscadorVuelosBase(ABC):
    @abstractmethod
    def buscar(self, ciudad):
        pass
