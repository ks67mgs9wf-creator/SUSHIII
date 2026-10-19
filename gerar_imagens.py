"""Gera as 12 ilustrações dos pratos em static/img/ (1.svg ... 12.svg).

Uso:  python gerar_imagens.py
Para usar fotos reais, salve-as em static/img/ com o número do prato (ex.: 1.jpg);
elas têm prioridade sobre as ilustrações.
"""
import math
import os
import random
import xml.dom.minidom as md

NORI, ARROZ, ARROZ_L = "#1E2B26", "#FBFBF4", "#E4E4D6"


def svg(bg, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" fill="{bg}"/>'
            f'<circle cx="100" cy="104" r="88" fill="#000" opacity=".07"/><circle cx="100" cy="100" r="88" fill="#FFFFFF"/>'
            f'<circle cx="100" cy="100" r="80" fill="none" stroke="#DCE7E3" stroke-width="2"/>{body}</svg>')


def topo(kind):
    if kind == "salmao":
        c, l = "#F2825E", "#FBC3A8"
    elif kind == "atum":
        c, l = "#B02A3E", "#D9566B"
    else:
        c, l = "#F6A58E", "#EF8068"
    s = f'<rect x="-49" y="-28" width="98" height="30" rx="13" fill="{c}"/>'
    if kind == "camarao":
        s += "".join(f'<path d="M{x} -26 Q{x+4} -12 {x} 0" stroke="{l}" stroke-width="4" fill="none"/>' for x in range(-36, 40, 14))
        s += '<path d="M44 -20 q14 -10 8 8 q-4 8 -8 4z" fill="#EF8068"/>'
    else:
        s += "".join(f'<path d="M{x} -24 Q{x+10} -14 {x} -4" stroke="{l}" stroke-width="3" fill="none" opacity=".8"/>' for x in (-30, -8, 14, 34))
    return s


def niguiri(cx, cy, sc, kind):
    return (f'<g transform="translate({cx} {cy}) scale({sc})"><rect x="-44" y="-12" width="88" height="34" rx="14" fill="{ARROZ}" stroke="{ARROZ_L}" stroke-width="2"/>'
            + topo(kind) + '</g>')


def maki(cx, cy, r, tipo, fill):
    g = f'<g transform="translate({cx} {cy})">'
    if tipo == "hosso":
        g += f'<circle r="{r}" fill="{NORI}"/><circle r="{r*.78}" fill="{ARROZ}"/><circle r="{r*.4}" fill="{fill}"/>'
    else:
        outer = {"phila": "#F2825E", "hot": "#D99A3A"}.get(tipo, ARROZ)
        g += f'<circle r="{r}" fill="{outer}" stroke="{ARROZ_L if outer == ARROZ else "#00000022"}" stroke-width="2"/>'
        if tipo == "hot":
            random.seed(int(cx * 7 + cy))
            g += "".join(f'<circle cx="{random.uniform(-r*.8, r*.8):.1f}" cy="{random.uniform(-r*.8, r*.8):.1f}" r="1.6" fill="#B87A22"/>' for _ in range(14))
        elif tipo == "phila":
            g += f'<circle r="{r*.9}" fill="none" stroke="#FBC3A8" stroke-width="3" stroke-dasharray="8 6"/>'
        else:
            random.seed(int(cx * 5 + cy))
            g += "".join(f'<circle cx="{r*.86*math.cos(a):.1f}" cy="{r*.86*math.sin(a):.1f}" r="1.5" fill="#CDBB8A"/>' for a in [i * math.pi / 7 for i in range(14)])
        g += f'<circle r="{r*.68}" fill="{NORI}"/><circle r="{r*.56}" fill="{ARROZ}"/><circle r="{r*.28}" fill="{fill}"/>'
        if tipo == "skin":
            g += f'<circle cx="{r*.1}" cy="-{r*.1}" r="2" fill="#7BB661"/>'
        if tipo == "phila":
            g += f'<circle r="{r*.12}" fill="#FFFFFF"/>'
    return g + '</g>'


def trio(tipo, fill, r):
    return "".join(maki(x, y, r, tipo, fill) for x, y in ((72, 78), (128, 78), (100, 130)))


def temaki(fills):
    cone = f'<g transform="rotate(-14 100 100)"><path d="M100 176 L50 70 Q100 52 150 70Z" fill="{NORI}"/>'
    cone += '<path d="M100 176 L68 96 M100 176 L100 62 M100 176 L130 96" stroke="#2F4038" stroke-width="2" fill="none"/>'
    cone += f'<ellipse cx="100" cy="66" rx="50" ry="13" fill="{ARROZ}"/>'
    for i, (c, dx) in enumerate(zip(fills, (-26, -6, 14, 32))):
        cone += f'<rect x="{100+dx}" y="22" width="14" height="46" rx="6" fill="{c}" transform="rotate({(i-1.5)*9} {100+dx+7} 66)"/>'
    return cone + '</g>'


def bandeja(w, h, pecas):
    b = f'<rect x="{100-w/2}" y="{100-h/2}" width="{w}" height="{h}" rx="12" fill="#B98A5A"/>'
    b += "".join(f'<path d="M{100-w/2+8} {y} H{100+w/2-8}" stroke="#A37646" stroke-width="2"/>' for y in range(int(100 - h/2 + 14), int(100 + h/2), 16))
    return b + pecas


def combo(familia):
    p = ""
    if not familia:
        p += niguiri(66, 78, .55, "salmao") + niguiri(66, 108, .55, "atum") + niguiri(66, 138, .55, "camarao")
        for x, y, t, f in ((112, 76, "phila", "#F5E6D3"), (146, 76, "hot", "#F2825E"), (112, 114, "uramaki", "#7BB661"), (146, 114, "skin", "#8A5A3B")):
            p += maki(x, y, 15, t, f)
        p += '<ellipse cx="108" cy="146" rx="14" ry="7" fill="#F4A6B5"/><circle cx="140" cy="146" r="6" fill="#8CB369"/>'
        return bandeja(150, 106, p)
    for i, k in enumerate(("salmao", "atum", "camarao", "salmao")):
        p += niguiri(46 + (i % 2) * 40, 58 + (i // 2) * 34, .45, k)
    for i, (t, f) in enumerate((("phila", "#F5E6D3"), ("hot", "#F2825E"), ("uramaki", "#7BB661"), ("skin", "#8A5A3B"),
                                 ("hosso", "#7BB661"), ("hosso", "#F2825E"), ("phila", "#F5E6D3"), ("hot", "#F2825E"))):
        p += maki(110 + (i % 4) * 24, 56 + (i // 4) * 26, 10.5, t, f)
    for i, (t, f) in enumerate((("uramaki", "#7BB661"), ("skin", "#8A5A3B"), ("phila", "#F5E6D3"),
                                 ("hot", "#F2825E"), ("hosso", "#F2825E"), ("uramaki", "#F2825E"))):
        p += maki(52 + i * 24, 126, 10.5, t, f)
    p += '<ellipse cx="62" cy="150" rx="14" ry="6" fill="#F4A6B5"/><circle cx="96" cy="150" r="6" fill="#8CB369"/>'
    p += niguiri(140, 150, .45, "atum")
    return bandeja(172, 128, p)


N, U, H, T, C = "#DCEBE7", "#E1EAF2", "#E6EFDF", "#F5E8DC", "#DDE6EE"
ITENS = {
    1: (N, niguiri(100, 70, 1, "salmao") + niguiri(100, 128, 1, "salmao")),
    2: (N, niguiri(100, 70, 1, "atum") + niguiri(100, 128, 1, "atum")),
    3: (N, niguiri(100, 70, 1, "camarao") + niguiri(100, 128, 1, "camarao")),
    4: (U, trio("phila", "#F5E6D3", 38)),
    5: (U, trio("skin", "#8A5A3B", 38)),
    6: (U, trio("hot", "#F2825E", 38)),
    7: (H, trio("hosso", "#7BB661", 32)),
    8: (H, trio("hosso", "#F2825E", 32)),
    9: (T, temaki(["#F2825E", "#F5E6D3", "#F2825E", "#7BB661"])),
    10: (T, temaki(["#E4432D", "#F6C945", "#F5F0E6", "#E4432D"])),
    11: (C, combo(False)),
    12: (C, combo(True)),
}

if __name__ == "__main__":
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img")
    os.makedirs(pasta, exist_ok=True)
    for i, (bg, body) in ITENS.items():
        conteudo = svg(bg, body)
        md.parseString(conteudo)  # garante que o SVG é válido
        with open(os.path.join(pasta, f"{i}.svg"), "w", encoding="utf-8") as f:
            f.write(conteudo)
    print(f"{len(ITENS)} imagens geradas em {pasta}")
