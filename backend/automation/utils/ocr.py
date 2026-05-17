"""Pipeline OCR: OpenCV para pré-processamento → Pytesseract para extração."""
import cv2
import numpy as np
import pytesseract
from PIL import Image


def imagem_para_texto(img: Image.Image, lang: str = "por") -> str:
    arr = np.array(img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resultado = pytesseract.image_to_string(thresh, lang=lang, config="--psm 6")
    return resultado.strip()


def extrair_de_arquivo(caminho: str, lang: str = "por") -> str:
    img = Image.open(caminho)
    return imagem_para_texto(img, lang)
