import os
import random
from dataclasses import dataclass

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Color, Vector2, display, draw, event
from pygame.time import Clock

G = 500.0
S = 0.1


@dataclass
class Circle:
    c: Vector2
    r: float


@dataclass
class Ball(Circle):
    d: Vector2
    color: Color

    def update(self, dt: float) -> None:
        self.c += self.d * dt + (0, G * dt * dt / 2)
        self.d.y += G * dt
        self.d -= self.d.normalize() * S * (self.d.length()) * dt  # slowdown


def main() -> None:
    pygame.init()
    font = pygame.font.SysFont("Courier New", 16)
    screen = pygame.display.set_mode((800, 600))
    size = Vector2(screen.get_size())
    big = Circle(size / 2, (size / 2).y * 0.9)
    balls: list[Ball] = []
    # balls.append(Ball(big.c.copy(), 10, Vector2(0, 0), Color("red")))

    run = True
    clock = Clock()
    p_start: Vector2 | None = None
    p_finish: Vector2 = Vector2()
    while run:
        dt = clock.tick(60) / 1000
        fps = clock.get_fps()
        for e in event.get():
            match e.type:
                case pygame.QUIT:
                    run = False
                case pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        run = False
                case pygame.MOUSEBUTTONDOWN:
                    p_start = Vector2(e.pos)
                case pygame.MOUSEMOTION:
                    p_finish = Vector2(e.pos)
                case pygame.MOUSEBUTTONUP:
                    p_finish = Vector2(e.pos)
                    assert p_start is not None
                    ball = Ball(
                        c=p_start,
                        r=10,
                        d=10 * (p_start - p_finish),
                        color=Color(random.randint(0, 255**4)),
                    )
                    balls.append(ball)
                    p_start = None

        for ball in balls:
            ball.update(dt)
            d = ball.c - big.c
            if d.length() + ball.r >= big.r:
                n = d.normalize()
                ball.c -= (d.length() + ball.r - big.r) * n
                c = ball.d * n
                ball.d -= 2 * c * n

        screen.fill("black")
        for ball in balls:
            draw.circle(screen, ball.color, ball.c, ball.r)
        draw.circle(screen, "white", big.c, big.r, 1)
        draw.circle(screen, "white", big.c, 1)
        if p_start is not None:
            draw.aaline(screen, "white", p_start, p_finish)
            draw.circle(screen, "white", p_start, 4)
        screen.blit(font.render(f"{fps=:.1f}", False, "white"), (0, 0))
        display.flip()


if __name__ == "__main__":
    main()
