import os
import random
from dataclasses import dataclass

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Color, Vector2, display, draw, event
from pygame.time import Clock

G = 400.0


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


def main() -> None:
    pygame.init()
    font = pygame.font.SysFont("Courier New", 16)
    screen = pygame.display.set_mode((800, 600))
    size = Vector2(screen.get_size())
    big = Circle(size / 2, (size / 2).y * 0.9)
    ball = Ball(big.c.copy(), 10, Vector2(0, 0), Color("red"))
    balls: list[Ball] = [ball]

    run = True
    clock = Clock()
    while run:
        dt = clock.tick(60) / 1000
        fps = clock.get_fps()
        for e in event.get():
            match e.type:
                case pygame.QUIT:
                    run = False
                case pygame.MOUSEBUTTONDOWN:
                    ball = Ball(
                        Vector2(e.pos),
                        10,
                        Vector2(0, 0),
                        Color(random.randint(0, 255**4)),
                    )
                    balls.append(ball)

        for ball in balls:
            ball.update(dt)
            d = ball.c - big.c
            if d.length() + ball.r >= big.r:
                n = d.normalize()
                # ball.c -= (d.length() + ball.r - big.r) * n
                c = ball.d * n
                ball.d -= 2 * c * n

        screen.fill("black")
        for ball in balls:
            draw.circle(screen, ball.color, ball.c, ball.r)
        draw.circle(screen, "white", big.c, big.r, 1)
        draw.circle(screen, "white", big.c, 1)
        screen.blit(font.render(f"{fps=:.1f}", False, "white"), (0, 0))
        display.flip()


if __name__ == "__main__":
    main()
