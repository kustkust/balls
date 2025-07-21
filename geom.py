from dataclasses import dataclass
from math import sqrt

from pygame.math import Vector2


@dataclass
class Circle:
    c: Vector2
    r: float


@dataclass
class Line:
    n: Vector2
    c: float

    @property
    def A(self) -> float:
        return self.n.x

    @property
    def B(self) -> float:
        return self.n.y

    @property
    def C(self) -> float:
        return self.c

    @classmethod
    def from_2_points(cls, p1: Vector2, p2: Vector2) -> "Line | None":
        n = Vector2(p1.y - p2.y, p2.x - p1.x)
        if n.x == 0 and n.y == 0:
            return None
        n.normalize_ip()
        c = -n * p1
        return cls(n, c)

    def project_x(self, x: float) -> Vector2 | None:
        if self.n.y != 0:
            return Vector2(x, -(self.A * x + self.C) / self.B)


def solve_p2(
    a: float, b: float, c: float
) -> tuple[()] | tuple[float] | tuple[float, float]:
    D = b * b - 4 * a * c
    if D < 0:
        return ()
    if D == 0:
        return (-b / (2 * a),)
    Ds = sqrt(D)
    return ((-b - Ds) / (2 * a), (-b + Ds) / (2 * a))


def circle_line_collide(
    circle: Circle, line: Line
) -> tuple[()] | tuple[Vector2] | tuple[Vector2, Vector2]:
    (A, B), C = line.n, line.c
    (x0, y0), r = circle.c, circle.r
    A2 = A * A
    B2 = B * B
    if A2 > B2:
        a = 1 / A2
        b = 2 * (B * C / A2 + x0 * B / A - y0)
        c = (C * C / A2) + (2 * x0 * C / A) + (x0 * x0 + y0 * y0 - r * r)
        match solve_p2(a, b, c):
            case ():
                return ()
            case (y1,):
                return (Vector2(-(B * y1 + C) / A, y1),)
            case y1, y2:
                return (Vector2(-(B * y1 + C) / A, y1), Vector2(-(B * y2 + C) / A, y2))
    else:
        a = 1 / B2
        b = 2 * (A * C / B2 + y0 * A / B - x0)
        c = C * C / B2 + 2 * y0 * C / B + y0 * y0 + x0 * x0 - r * r
        match solve_p2(a, b, c):
            case ():
                return ()
            case (x1,):
                return (Vector2(x1, -(A * x1 + C) / B),)
            case x1, x2:
                return (Vector2(x1, -(A * x1 + C) / B), Vector2(x2, -(A * x2 + C) / B))

