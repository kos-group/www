"""Genera las ilustraciones SVG isométricas de site/img/ (vector art propio, sin recursos de terceros).

Uso:  python -I tools/illustrations.py   (desde la raíz del repo; reescribe site/img/ill-*.svg)

Solo atributos de presentación (fill, stroke, opacity...): la CSP de nginx prohíbe estilos en línea.
Paleta: azul y gris del logo, sus tonos y el acento naranja (ver la cabecera de site/styles.css).
"""
import math
import os

BLUE = "#1761A0"
BLUE_D = "#104A7A"
NAVY = "#0B2540"
BLUE_M = "#3C82C4"
BLUE_L = "#8DB8E0"
BLUE_XL = "#CFE1F2"
BLUE_T = "#EAF2FA"
GRAY = "#9E9E9E"
GRAY_M = "#C4C4C4"
GRAY_L = "#E3E3E3"
GRAY_T = "#F4F4F4"
WHITE = "#FFFFFF"
ACC = "#F7931E"
ACC_D = "#D97706"
ACC_L = "#FCCB8E"

C = math.cos(math.radians(30))
S = math.sin(math.radians(30))


class Scene:
    def __init__(self, w, h, ox, oy, scale):
        self.w, self.h, self.ox, self.oy, self.k = w, h, ox, oy, scale
        self.items = []  # (orden, svg)
        self.defs = []

    def p(self, x, y, z=0.0):
        sx = self.ox + (x - y) * C * self.k
        sy = self.oy + (x + y) * S * self.k - z * self.k
        return sx, sy

    @staticmethod
    def pts(points):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    def add(self, order, svg):
        self.items.append((order, svg))

    def box(self, x, y, z, w, d, h, top, left, right, order=None, stroke=None):
        o = order if order is not None else x + y + z + (w + d) / 2
        st = f' stroke="{stroke}" stroke-width="1" stroke-linejoin="round"' if stroke else ""
        t = [self.p(x, y, z + h), self.p(x + w, y, z + h), self.p(x + w, y + d, z + h), self.p(x, y + d, z + h)]
        fl = [self.p(x, y + d, z), self.p(x + w, y + d, z), self.p(x + w, y + d, z + h), self.p(x, y + d, z + h)]
        fr = [self.p(x + w, y, z), self.p(x + w, y + d, z), self.p(x + w, y + d, z + h), self.p(x + w, y, z + h)]
        g = (f'<polygon points="{self.pts(fl)}" fill="{left}"{st}/>'
             f'<polygon points="{self.pts(fr)}" fill="{right}"{st}/>'
             f'<polygon points="{self.pts(t)}" fill="{top}"{st}/>')
        self.add(o, g)

    def top_rect(self, x, y, z, w, d, fill, order, opacity=None, rx=False):
        op = f' opacity="{opacity}"' if opacity is not None else ""
        t = [self.p(x, y, z), self.p(x + w, y, z), self.p(x + w, y + d, z), self.p(x, y + d, z)]
        self.add(order, f'<polygon points="{self.pts(t)}" fill="{fill}"{op}/>')

    def face_x(self, x, y, z, d, h, fill, order, opacity=None):
        """Rectángulo en el plano x = cte (cara derecha), de y..y+d y z..z+h."""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        t = [self.p(x, y, z), self.p(x, y + d, z), self.p(x, y + d, z + h), self.p(x, y, z + h)]
        self.add(order, f'<polygon points="{self.pts(t)}" fill="{fill}"{op}/>')

    def face_y(self, x, y, z, w, h, fill, order, opacity=None):
        """Rectángulo en el plano y = cte (cara izquierda), de x..x+w y z..z+h."""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        t = [self.p(x, y, z), self.p(x + w, y, z), self.p(x + w, y, z + h), self.p(x, y, z + h)]
        self.add(order, f'<polygon points="{self.pts(t)}" fill="{fill}"{op}/>')

    def line(self, a, b, color, width, order, dash=None, opacity=None):
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(order, f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                        f'stroke-width="{width}" stroke-linecap="round"{ds}{op}/>')

    def polyline_y(self, x0, y, z0, xs_zs, color, width, order):
        """Línea de gráfico sobre la cara y = cte."""
        pts = [self.p(x0 + u, y, z0 + v) for u, v in xs_zs]
        self.add(order, f'<polyline points="{self.pts(pts)}" fill="none" stroke="{color}" stroke-width="{width}" '
                        f'stroke-linecap="round" stroke-linejoin="round"/>')

    def polyline_x(self, x, y0, z0, ys_zs, color, width, order):
        pts = [self.p(x, y0 + u, z0 + v) for u, v in ys_zs]
        self.add(order, f'<polyline points="{self.pts(pts)}" fill="none" stroke="{color}" stroke-width="{width}" '
                        f'stroke-linecap="round" stroke-linejoin="round"/>')

    def node(self, x, y, z, r, fill, order, ring=None):
        sx, sy = self.p(x, y, z)
        g = ""
        if ring:
            g += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r * 2:.1f}" fill="{ring}" opacity="0.25"/>'
        g += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.1f}" fill="{fill}"/>'
        self.add(order, g)

    def raw(self, order, svg):
        self.add(order, svg)

    def render(self, title, bg=True):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
               f'aria-label="{title}">', f"<title>{title}</title>"]
        if self.defs:
            out.append("<defs>" + "".join(self.defs) + "</defs>")
        if bg:
            out.append(f'<ellipse cx="{self.w / 2:.0f}" cy="{self.h * 0.56:.0f}" rx="{self.w * 0.47:.0f}" '
                       f'ry="{self.h * 0.42:.0f}" fill="url(#bgfade)"/>')
        for _, s in sorted(self.items, key=lambda t: t[0]):
            out.append(s)
        out.append("</svg>")
        return "\n".join(out) + "\n"


def bg_defs(sc):
    sc.defs.append(
        '<radialGradient id="bgfade" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0" stop-color="{BLUE_XL}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{BLUE_T}" stop-opacity="0"/></radialGradient>')


def platform(sc, x, y, w, d, h=0.5, order=-100):
    sc.box(x, y, 0, w, d, h, WHITE, BLUE_XL, GRAY_L, order=order)


def bars(sc, x, y, z, heights, accent_idx=None, step=1.1, size=0.7):
    for i, hh in enumerate(heights):
        acc = i == accent_idx
        sc.box(x + i * step, y, z, size, size, hh,
               ACC_L if acc else BLUE_L, ACC if acc else BLUE, ACC_D if acc else BLUE_D)


def monitor(sc, x, y, z, w, h, order=None):
    """Panel vertical (plano y) con gráfico."""
    o = order if order is not None else x + y + z + 1
    sc.box(x, y, z, w, 0.25, h, GRAY_L, NAVY, BLUE_D, order=o)
    sc.face_y(x + 0.2, y + 0.25, z + 0.25, w - 0.4, h - 0.5, WHITE, o + 0.01)
    sc.polyline_y(x + 0.4, y + 0.25, z + 0.6,
                  [(0, 0.2), (0.7, 0.9), (1.4, 0.6), (2.1, 1.5), (2.8, 1.2), (w - 1.0, 2.1)], BLUE, 3, o + 0.02)
    sc.node(*(x + 0.4 + w - 1.0, y + 0.25, z + 0.6 + 2.1), 4, ACC, o + 0.03, ring=ACC)
    sc.face_y(x + 0.4, y + 0.25, z + h - 0.75, 1.4, 0.18, BLUE_L, o + 0.02)
    sc.face_y(x + 2.0, y + 0.25, z + h - 0.75, 0.8, 0.18, GRAY_M, o + 0.02)


def doc(sc, x, y, z, w=1.6, d=2.1, lines=4, accent=False, order=None):
    o = order if order is not None else x + y + z + 1
    sc.box(x, y, z, w, d, 0.08, WHITE, GRAY_L, GRAY_M, order=o)
    for i in range(lines):
        ll = w - 0.5 if i % 2 == 0 else w - 0.9
        sc.top_rect(x + 0.25, y + 0.3 + i * 0.38, z + 0.081, ll, 0.12,
                    ACC if (accent and i == lines - 1) else (BLUE_L if i else BLUE), o + 0.01)


def phone(sc, x, y, z, color=NAVY, order=None):
    o = order if order is not None else x + y + z + 1
    sc.box(x, y, z, 1.3, 0.2, 2.5, GRAY_M, color, BLUE_D, order=o)
    sc.face_y(x + 0.12, y + 0.2, z + 0.25, 1.06, 2.0, BLUE_T, o + 0.01)
    return o


def write(name, svg):
    path = os.path.join("site", "img", name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    if "659" in svg:
        raise SystemExit(f"{name} contiene '659' (lo busca la comprobación de datos de contacto): mueve algún punto")
    print(f"{path}: {len(svg.encode()) / 1024:.1f} KiB")


# ---------------------------------------------------------------- portada
def hero():
    sc = Scene(640, 540, 330, 168, 26)
    bg_defs(sc)
    platform(sc, 0, 0, 10, 10, 0.6)
    sc.box(0.6, 0.6, 0.6, 8.8, 8.8, 0.15, BLUE_T, BLUE_XL, BLUE_XL, order=-90)
    monitor(sc, 1.0, 1.2, 0.75, 5.0, 3.6, order=3)
    bars(sc, 6.6, 1.4, 0.75, [1.2, 2.0, 1.5, 3.1], accent_idx=3, step=0.9, size=0.6)
    doc(sc, 1.6, 6.4, 0.75, accent=True, order=7)
    doc(sc, 1.8, 6.6, 0.95, order=7.2)
    sc.box(5.6, 5.4, 0.75, 2.6, 2.6, 0.9, BLUE_L, BLUE, BLUE_D, order=12)
    sc.box(6.1, 5.9, 1.65, 1.6, 1.6, 0.7, ACC_L, ACC, ACC_D, order=13)
    phone(sc, 8.0, 4.4, 0.75, order=12.5)
    # red de nodos flotante
    nodes = [(2.0, 2.0, 7.2), (5.0, 1.0, 7.8), (8.0, 3.0, 6.8), (6.5, 6.0, 6.0), (3.0, 6.5, 6.4)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            sc.line(a, b, BLUE_L, 1.5, 50, dash="4 5")
    for i, n in enumerate(nodes):
        sc.node(*n, 7 if i != 1 else 9, ACC if i == 1 else BLUE, 51, ring=ACC if i == 1 else BLUE_L)
    sc.line((5.0, 1.0, 7.8), (5.0, 1.0, 4.6), ACC_L, 1.5, 49, dash="2 5")
    # cubos sueltos
    sc.box(10.6, 1.0, 1.5, 0.8, 0.8, 0.8, BLUE_XL, BLUE_L, BLUE_M, order=60)
    sc.box(-1.6, 7.2, 2.6, 0.6, 0.6, 0.6, ACC_L, ACC, ACC_D, order=60)
    sc.box(10.2, 8.4, 0.2, 1.0, 1.0, 1.0, GRAY_T, GRAY_L, GRAY_M, order=60)
    write("ill-hero.svg", sc.render("Ilustración: plataforma de datos con panel de análisis, documentos, "
                                    "gráfico de barras y red de nodos conectados"))


# ---------------------------------------------------------------- servicios (consultoría y análisis)
def servicios():
    sc = Scene(520, 400, 260, 120, 24)
    bg_defs(sc)
    platform(sc, 0, 0, 8, 7, 0.5)
    monitor(sc, 0.8, 1.0, 0.5, 4.6, 3.4, order=3)
    bars(sc, 5.6, 1.4, 0.5, [1.0, 1.8, 2.6], accent_idx=2, step=0.85, size=0.55)
    doc(sc, 1.2, 3.8, 0.5, order=6)
    sc.box(4.8, 4.2, 0.5, 2.2, 2.0, 0.5, BLUE_L, BLUE, BLUE_D, order=8)
    sc.box(5.2, 4.6, 1.0, 1.4, 1.2, 0.5, WHITE, GRAY_L, GRAY_M, order=9)
    # lupa
    cx, cy = sc.p(6.2, 3.0, 5.6)
    sc.raw(40, f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="34" fill="{WHITE}" opacity="0.75" stroke="{NAVY}" '
               f'stroke-width="7"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="none" stroke="{ACC}" '
               f'stroke-width="3" stroke-dasharray="6 6"/>'
               f'<line x1="{cx + 25:.1f}" y1="{cy + 25:.1f}" x2="{cx + 56:.1f}" y2="{cy + 56:.1f}" '
               f'stroke="{NAVY}" stroke-width="11" stroke-linecap="round"/>')
    write("ill-servicios.svg", sc.render("Ilustración: análisis de datos con panel, gráficos y una lupa"))


# ---------------------------------------------------------------- RINC
def rinc():
    sc = Scene(520, 400, 250, 110, 24)
    bg_defs(sc)
    platform(sc, 0, 0, 8, 7, 0.5)
    for i in range(4):
        doc(sc, 1.0 + i * 0.15, 1.2 + i * 0.15, 0.5 + i * 0.22, w=2.6, d=3.2, lines=5, accent=(i == 3), order=5 + i)
    sc.box(4.6, 4.2, 0.5, 2.4, 2.0, 0.6, BLUE_L, BLUE, BLUE_D, order=12)
    sc.box(4.9, 4.5, 1.1, 1.8, 1.4, 0.5, BLUE_XL, BLUE_M, BLUE, order=13)
    # moneda con el euro y flecha de retorno
    cx, cy = sc.p(6.0, 1.6, 5.2)
    sc.raw(40, f'<circle cx="{cx:.1f}" cy="{cy + 8:.1f}" r="40" fill="{ACC_D}"/>'
               f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="40" fill="{ACC}"/>'
               f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="30" fill="none" stroke="{ACC_L}" stroke-width="3"/>'
               f'<text x="{cx:.1f}" y="{cy + 13:.1f}" text-anchor="middle" font-family="Arial, sans-serif" '
               f'font-size="38" font-weight="700" fill="{NAVY}">€</text>')
    ax, ay = sc.p(3.0, 0.4, 5.5)
    sc.raw(41, f'<path d="M{cx - 52:.1f},{cy - 6:.1f} C{cx - 90:.1f},{cy - 40:.1f} {ax:.1f},{ay - 40:.1f} '
               f'{ax - 10:.1f},{ay + 6:.1f}" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linecap="round" '
               f'stroke-dasharray="2 9"/>'
               f'<path d="M{cx - 60:.1f},{cy - 18:.1f} l10,14 l-16,4" fill="none" stroke="{BLUE}" stroke-width="4" '
               f'stroke-linecap="round" stroke-linejoin="round"/>')
    # sello de validación
    sx, sy = sc.p(6.0, 5.3, 2.0)
    sc.raw(42, f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="17" fill="{WHITE}" stroke="{ACC}" stroke-width="3"/>'
               f'<path d="M{sx - 8:.1f},{sy:.1f} l6,6 l11,-12" fill="none" stroke="{ACC_D}" stroke-width="3.5" '
               f'stroke-linecap="round" stroke-linejoin="round"/>')
    write("ill-rinc.svg", sc.render("Ilustración: facturas apiladas y una moneda de euro que vuelve a la empresa"))


# ---------------------------------------------------------------- Portame
def portame():
    sc = Scene(520, 400, 250, 120, 24)
    bg_defs(sc)
    platform(sc, 0, 0, 8, 7, 0.5)
    phone(sc, 1.0, 4.2, 0.5, color=BLUE, order=9)
    phone(sc, 5.2, 4.2, 0.5, color=NAVY, order=11)
    for i, (x, col) in enumerate([(1.0, BLUE), (5.2, NAVY)]):
        for j in range(3):
            sc.face_y(x + 0.3, 4.4, 0.5 + 1.9 - j * 0.45, 0.7 if j else 0.5, 0.18,
                      (ACC if (i == 1 and j == 0) else BLUE_L), 12 + i * 2)
    # antenas
    for x, y in [(1.4, 1.0), (5.8, 1.2)]:
        sc.box(x, y, 0.5, 0.5, 0.5, 2.6, GRAY_L, GRAY_M, GRAY, order=x + y + 1)
        sc.node(x + 0.25, y + 0.25, 3.3, 5, BLUE, x + y + 1.1, ring=BLUE_L)
    # flecha de portabilidad
    a = sc.p(1.6, 4.3, 3.6)
    b = sc.p(5.8, 4.3, 3.6)
    mx = (a[0] + b[0]) / 2
    my = min(a[1], b[1]) - 90
    sc.raw(40, f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{mx:.1f},{my:.1f} {b[0] - 6:.1f},{b[1] - 10:.1f}" fill="none" '
               f'stroke="{ACC}" stroke-width="5" stroke-linecap="round"/>'
               f'<path d="M{b[0] - 22:.1f},{b[1] - 22:.1f} l16,12 l-16,10" fill="none" stroke="{ACC}" '
               f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    # baldosas de numeración
    for i in range(3):
        sc.box(3.0 + i * 0.9, 1.2, 0.5, 0.7, 0.7, 0.35 + i * 0.25, BLUE_XL, BLUE_L, BLUE_M)
    write("ill-portame.svg", sc.render("Ilustración: dos móviles con una flecha de portabilidad entre ellos y "
                                       "antenas de red"))


# ---------------------------------------------------------------- Integra
def integra():
    sc = Scene(520, 400, 260, 120, 22)
    bg_defs(sc)
    platform(sc, 0, 0, 9, 8, 0.5)
    hub = (3.6, 3.1, 0.5)
    mods = [(0.6, 0.6), (3.8, 0.4), (7.0, 0.8), (0.4, 6.0), (4.0, 6.4), (7.2, 5.6)]
    for (x, y) in mods:
        sc.line((x + 0.6, y + 0.6, 0.6), (hub[0] + 1.0, hub[1] + 1.0, 0.6), BLUE_L, 3, -50, dash="1 7")
    sc.box(*hub, 2.0, 2.0, 2.2, BLUE_L, BLUE, BLUE_D, order=20)
    sc.box(hub[0] + 0.5, hub[1] + 0.5, 2.7, 1.0, 1.0, 0.5, ACC_L, ACC, ACC_D, order=21)
    for i, (x, y) in enumerate(mods):
        top, l, r = ((WHITE, GRAY_L, GRAY_M) if i % 2 else (BLUE_XL, BLUE_L, BLUE_M))
        sc.box(x, y, 0.5, 1.2, 1.2, 0.6 + (i % 3) * 0.3, top, l, r)
        sc.node(x + 0.6, y + 0.6, 1.25 + (i % 3) * 0.3, 4, ACC if i == 2 else BLUE, x + y + 5)
    write("ill-integra.svg", sc.render("Ilustración: un núcleo central conectado con seis módulos de la plataforma"))


# ---------------------------------------------------------------- BOSS / mayorista
def boss():
    sc = Scene(520, 400, 250, 110, 23)
    bg_defs(sc)
    platform(sc, 0, 0, 8.5, 7.5, 0.5)
    for i in range(3):
        x = 0.8 + i * 1.5
        sc.box(x, 0.8, 0.5, 1.1, 1.6, 3.6 - i * 0.6, GRAY_L, NAVY, BLUE_D, order=2 + i)
        for j in range(4 - i):
            sc.face_y(x + 0.15, 2.4, 0.9 + j * 0.7, 0.8, 0.12, ACC if j == 0 else BLUE_L, 2.2 + i)
    doc(sc, 1.2, 4.0, 0.5, w=2.0, d=2.4, accent=True, order=8)
    doc(sc, 1.4, 4.2, 0.7, w=2.0, d=2.4, order=8.5)
    bars(sc, 5.4, 4.6, 0.5, [0.8, 1.4, 2.1], accent_idx=None, step=0.8, size=0.55)
    sc.polyline_y(5.4, 4.6, 0.5, [(0.25, 1.4), (1.05, 2.0), (1.85, 2.8), (2.4, 3.3)], ACC, 4, 30)
    sc.node(5.4 + 2.4, 4.6, 0.5 + 3.3, 6, ACC, 31, ring=ACC)
    write("ill-boss.svg", sc.render("Ilustración: servidores, facturas y un gráfico de ingresos al alza"))


# ---------------------------------------------------------------- Nosotros (negocio desde dentro)
def nosotros():
    sc = Scene(520, 400, 260, 120, 24)
    bg_defs(sc)
    platform(sc, 0, 0, 8, 7, 0.5)
    sc.box(1.0, 1.0, 0.5, 2.0, 2.0, 1.0, BLUE_L, BLUE, BLUE_D, order=2)
    sc.box(3.0, 1.0, 0.5, 2.0, 2.0, 1.0, WHITE, GRAY_L, GRAY_M, order=3)
    sc.box(1.0, 3.0, 0.5, 2.0, 2.0, 1.0, WHITE, GRAY_L, GRAY_M, order=3.1)
    sc.box(3.0, 3.0, 0.5, 2.0, 2.0, 1.0, BLUE_L, BLUE, BLUE_D, order=4)
    sc.box(1.0, 1.0, 1.5, 2.0, 2.0, 1.0, WHITE, GRAY_L, GRAY_M, order=5)
    sc.box(3.0, 1.0, 1.5, 2.0, 2.0, 1.0, BLUE_XL, BLUE_L, BLUE_M, order=6)
    sc.box(1.0, 3.0, 1.5, 2.0, 2.0, 1.0, BLUE_L, BLUE, BLUE_D, order=6.1)
    # pieza que encaja (acento), aún en el aire
    sc.box(3.0, 3.0, 3.3, 2.0, 2.0, 1.0, ACC_L, ACC, ACC_D, order=20)
    sc.line((4.0, 4.0, 3.2), (4.0, 4.0, 1.7), ACC, 2.5, 19, dash="3 6")
    sc.top_rect(3.0, 3.0, 1.52, 2.0, 2.0, ACC, 1, opacity=0.25)
    sc.box(6.2, 4.6, 0.5, 1.0, 1.0, 0.6, BLUE_XL, BLUE_L, BLUE_M, order=30)
    sc.box(5.8, 1.0, 0.5, 1.2, 1.2, 1.6, GRAY_T, GRAY_L, GRAY_M, order=30)
    write("ill-nosotros.svg", sc.render("Ilustración: bloques que forman una estructura y una pieza naranja que "
                                        "encaja en su sitio"))


if __name__ == "__main__":
    hero()
    servicios()
    rinc()
    portame()
    integra()
    boss()
    nosotros()
