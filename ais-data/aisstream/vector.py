import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_heading(cls, heading):
        return Vector(
            math.cos(math.radians(heading)),
            math.sin(math.radians(heading)),
        )

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def _get_mag(self) -> float:
        return float((self.x**2 + self.y**2) ** 0.5)

    mag: float = property(_get_mag)

    def set_mag(self, mag):
        current_mag = self.mag
        if current_mag == 0:
            return self
        return self * (mag / current_mag)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
