from abc import ABC, abstractmethod

class SugeridorBase(ABC):
    @abstractmethod
    def sugerir(self, ciudad):
        pass
