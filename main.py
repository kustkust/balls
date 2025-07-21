# ruff: noqa: E741
import colorsys
import os
import random
from dataclasses import dataclass
from time import time
from typing import TYPE_CHECKING, Any

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Color, Rect, Surface, Vector2, display, draw, event
from pygame.font import Font
from pygame.math import lerp
from pygame.time import Clock
from pygame_gui import UIManager
from pygame_gui.elements import UITextBox

from record import PygameRecord

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


def collide(b1: Ball, b2: Ball) -> None:
    d = b1.c - b2.c
    # m1, m2 = b1.r * b1.r, b2.r * b2.r
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


def patch_HTMLParser() -> None:
    from pygame_gui.core.text.html_parser import HTMLParser

    if TYPE_CHECKING:
        from pygame_gui.core.interfaces import IUIAppearanceThemeInterface

    old__init__ = HTMLParser.__init__

    def __init__(
        self: HTMLParser,
        ui_theme: "IUIAppearanceThemeInterface",
        combined_ids: list[str],
        link_style: dict[str, Any],
        line_spacing: float = 1.0,
        text_direction: int = pygame.DIRECTION_LTR,
    ) -> None:
        old__init__(
            self, ui_theme, combined_ids, link_style, line_spacing, text_direction
        )
        self.pop_style("default_style")
        font_info = self.ui_theme.get_font_info(combined_ids)
        if "antialiased" in font_info:
            self.default_style["antialiased"] = font_info["antialiased"]
        self.push_style("default_style", self.default_style)

    HTMLParser.__init__ = __init__


def ease_out_quint(t: float) -> float:
    t = 1 - t
    return 1 - (t * t * t * t * t)


def main() -> None:
    pygame.init()
    # font = pygame.font.SysFont("Courier New", 16)
    pygame.display.set_caption("balls")
    screen = pygame.display.set_mode((1280, 720))
    size = Vector2(screen.get_size())
    big = Circle(size / 2, (size / 2).y * 0.9)
    balls: list[Ball] = []
    # balls.append(Ball(big.c.copy(), 10, Vector2(0, 0), Color("red")))

    run = True
    FPS = 60
    frame_time = 0
    f_begin = 0
    clock = Clock()
    p_start: Vector2 | None = None
    p_finish: Vector2 = Vector2()
    new_r = 10
    recorder = PygameRecord("gif/{dt}.gif", FPS, n=2)

    patch_HTMLParser()
    my_font: dict[str, str | int | float] = {
        "name": "Courier New",
        "point_size": "50",
        "size": "16",
        "antialiased": "0",
    }
    manager = UIManager(
        screen.get_size(),
        theme_path={
            "text_box": {
                "font": my_font,
                "colors": {
                    "dark_bg": "#00000040",
                    "normal_border": "#00000000",
                },
                "misc": {
                    "line_spacing": "0.5",
                    "border_width": "0",
                    "shadow_width": "0",
                    "padding": "0,0",
                },
            },
        },
    )
    manager.preload_fonts([my_font])
    bound = Rect((0, 0), (-1, -1))
    t = """fps={fps:.1f}<br>frame_time={frame_time:.5f}<br>recording={recording}"""
    tb = UITextBox(
        "",
        bound,
        manager=manager,
    )
    # pygame_gui.elements.UIScrollingContainer()

    update = True
    while run:
        dt = clock.tick(FPS) / 1000
        f_begin = time()
        fps = clock.get_fps()

        # CONTROL

        for e in event.get():
            match e.type:
                case pygame.QUIT:
                    run = False
                case pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        run = False
                    if e.key == pygame.K_r:
                        balls = []
                    if e.key == pygame.K_s:
                        recorder.switch()
                    if e.key == pygame.K_SPACE:
                        update = not update
                case pygame.MOUSEBUTTONDOWN:
                    if e.button == pygame.BUTTON_LEFT:
                        p_start = Vector2(e.pos)
                        p_finish = Vector2(e.pos)
                    if e.button == pygame.BUTTON_RIGHT:
                        p = Vector2(e.pos)
                        iss = []
                        for i, ball in enumerate(balls):
                            if ball.c.distance_to(p) <= new_r:
                                iss.append(i)
                        for i in reversed(iss):
                            del balls[i]
                case pygame.MOUSEMOTION:
                    if p_start is not None:
                        p_finish = Vector2(e.pos)
                case pygame.MOUSEBUTTONUP:
                    if e.button == pygame.BUTTON_LEFT:
                        p_finish = Vector2(e.pos)
                        if p_start is not None:
                            color = Color(0, 0, 0)
                            color.hsla = (random.random() * 360, 100, 50, 00)
                            ball = Ball(
                                c=p_start,
                                r=new_r,
                                v=10 * (p_start - p_finish),
                                color=color,
                            )
                            balls.append(ball)
                            p_start = None
                    if e.button == pygame.BUTTON_WHEELDOWN:
                        if p_start is not None and new_r > 1:
                            new_r -= 1
                    if e.button == pygame.BUTTON_WHEELUP:
                        if p_start is not None and new_r < 100:
                            new_r += 1
            manager.process_events(e)

        # UPDATE

        manager.update(dt)
        if update:
            for ball in balls:
                ball.c += ball.v * dt  + (0, G * dt * dt / 2)
                d = ball.c - big.c
                # ball.v += d / big.r * G * dt
                ball.v.y += G * dt
                if ball.v.length() > 0.0001:
                    ball.v -= (
                        ball.v.normalize() * S * (ball.v.length()) * dt
                    )  # slowdown
                if ball.v.length() < 0.01:
                    ball.v = Vector2()
                if d.length() + ball.r >= big.r:
                    n = d.normalize()
                    c = ball.v * n
                    ball.v -= 2 * c * n

            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    collide(balls[i], balls[j])

            for ball in balls:
                d = ball.c - big.c
                if d.length() + ball.r >= big.r:
                    n = d.normalize()
                    ball.c -= (d.length() + ball.r - big.r) * n

        # DRAW

        screen.fill("#7f7f7fff")
        for ball in balls:
            d = ball.c - big.c
            c = colorsys.hsv_to_rgb(
                (-d.angle_to((0.0, 1.0)) + 360) / 360,
                lerp(0, 1, ease_out_quint(d.length() / big.r)),
                1.0,
            )
            c = tuple(int(ch * 255) for ch in c)
            draw.circle(screen, c, ball.c, ball.r)
        if p_start is not None:
            draw.aaline(screen, "white", p_start, p_finish)
            draw.circle(screen, "white", p_start, new_r)
        # tt = write_lines(
        #     f"{fps=:.1f}",
        #     f"{frame_time=:.5f}",
        #     f"recording={recorder.recording}",
        #     f"E={e:.3f}",
        #     f"p=({p.x:.3f},{p.y:.3f})",
        #     font=font,
        #     color="white",
        # )
        # screen.blit(tt, (0, 0))
        tb.set_text(
            t.format(fps=fps, frame_time=frame_time, recording=recorder.recording)
        )
        draw.circle(screen, "white", big.c, big.r, 1)
        draw.circle(screen, "white", big.c, 1)

        manager.draw_ui(screen)
        recorder.add_frame()
        display.flip()
        frame_time = time() - f_begin


if __name__ == "__main__":
    main()
