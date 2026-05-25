class GameObject:

    def update(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must implement update()")

    def draw(self, surface):
        raise NotImplementedError(f"{self.__class__.__name__} must implement draw()")

    def interact(self, other=None):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} at ({getattr(self, 'x', '?')}, {getattr(self, 'y', '?')})>"
