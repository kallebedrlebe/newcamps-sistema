"""Captura de tela com PyAutoGUI/Pillow (Windows only)."""
import sys
from pathlib import Path

if sys.platform != "win32":
    raise ImportError("screen_capture só funciona no Windows")

import pyautogui
from PIL import Image


def capturar_tela(caminho: str | Path | None = None) -> Image.Image:
    img = pyautogui.screenshot()
    if caminho:
        img.save(str(caminho))
    return img


def capturar_regiao(x: int, y: int, largura: int, altura: int) -> Image.Image:
    return pyautogui.screenshot(region=(x, y, largura, altura))
