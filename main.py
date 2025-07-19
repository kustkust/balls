# ruff: noqa: E741
import os
import random
from dataclasses import dataclass

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Color, Vector2, display, draw, event, Surface
from pygame.font import Font
from pygame.time import Clock

G = 500.0
S = 0.1


@dataclass
class Circle:
    c: Vector2
    r: float


@dataclass
class Ball(Circle):
    v: Vector2
    color: Color

    def update(self, dt: float) -> None:
        self.c += self.v * dt + (0, G * dt * dt / 2)
        self.v.y += G * dt
        self.v -= self.v.normalize() * S * (self.v.length()) * dt  # slowdown
        if self.v.length() < 0.001:
            self.v = Vector2()


def collide(b1: Ball, b2: Ball) -> None:
    d = b1.c - b2.c
    l = d.length()
    if l > b1.r + b2.r or l == 0:
        return
    n = d.normalize()
    d22 = b2.v - b1.v
    c = d22 * n
    b1.v += n * c
    b2.v -= n * c
    b1.c -= n * (l - b1.r - b2.r) / 3
    b2.c += n * (l - b1.r - b2.r) / 3


def write_lines(
    *text: str,
    font: Font,
    color: Color | str = Color("white"),
    bg: Color | str = Color(0, 0, 0, 64),
) -> Surface:
    texts = []
    p = Vector2()
    for t in text:
        tmp = font.render(t, False, color)
        texts.append((tmp, Vector2(0, p.y)))
        p.y += tmp.get_size()[1]
        p.x = max(p.x, tmp.get_size()[0])
    s = Surface(p, pygame.SRCALPHA)
    s.fill(bg)
    for t, p in texts:
        s.blit(t, p)
    return s


def main() -> None:
    pygame.init()
    font = pygame.font.SysFont("Courier New", 16)
    pygame.display.set_caption("balls")
    screen = pygame.display.set_mode((800, 600))
    size = Vector2(screen.get_size())
    big = Circle(size / 2, (size / 2).y * 0.9)
    balls: list[Ball] = []
    # balls.append(Ball(big.c.copy(), 10, Vector2(0, 0), Color("red")))

    run = True
    clock = Clock()
    p_start: Vector2 | None = None
    p_finish: Vector2 = Vector2()
    new_r = 10
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
                    if e.key == pygame.K_r:
                        balls = []
                case pygame.MOUSEBUTTONDOWN:
                    if e.button == pygame.BUTTON_LEFT:
                        p_start = Vector2(e.pos)
                        p_finish = Vector2(e.pos)
                case pygame.MOUSEMOTION:
                    if p_start is not None:
                        p_finish = Vector2(e.pos)
                case pygame.MOUSEBUTTONUP:
                    if e.button == pygame.BUTTON_LEFT:
                        p_finish = Vector2(e.pos)
                        if p_start is not None:
                            ball = Ball(
                                c=p_start,
                                r=new_r,
                                v=10 * (p_start - p_finish),
                                color=Color(random.randint(0, 255**4)),
                            )
                            balls.append(ball)
                            p_start = None
                    if e.button == pygame.BUTTON_WHEELDOWN:
                        if p_start is not None and new_r > 1:
                            new_r -= 1
                    if e.button == pygame.BUTTON_WHEELUP:
                        if p_start is not None and new_r < 100:
                            new_r += 1

        for ball in balls:
            ball.update(dt)
            d = ball.c - big.c
            if d.length() + ball.r >= big.r:
                n = d.normalize()
                ball.c -= (d.length() + ball.r - big.r) * n
                c = ball.v * n
                ball.v -= 2 * c * n

        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                collide(balls[i], balls[j])

        screen.fill("black")
        for ball in balls:
            draw.circle(screen, ball.color, ball.c, ball.r)
        draw.circle(screen, "white", big.c, big.r, 1)
        draw.circle(screen, "white", big.c, 1)
        if p_start is not None:
            draw.aaline(screen, "white", p_start, p_finish)
            draw.circle(screen, "white", p_start, new_r)
        e = 0
        p = Vector2()
        for ball in balls:
            d = ball.v.length()
            e += d * d
            p += ball.v
        screen.blit(
            write_lines(
                f"{fps=:.1f}",
                f"E={e:.3f}",
                f"p=({p.x:.3f},{p.y:.3f})",
                font=font,
                color="white",
            ),
            (0, 0),
        )
        display.flip()


if __name__ == "__main__":
    main()
