import base64
from functools import lru_cache
from html import escape
from pathlib import Path

import streamlit.components.v1 as components

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SLIDES = [
    {
        "title": "Dados claros",
        "text": "Acompanhe indicadores financeiros e visualize resultados em um só lugar.",
        "layers": [
            ("bolinhas_slide1.png", "left:2%; top:54%; width:34%;", None),
            ("card_slide1.png", "left:8%; top:23%; width:92%;", 0.4),
            ("elem_slide1.png", "left:6%; top:10%; width:20%;", 0.9),
        ],
    },
    {
        "title": "Transformamos dados em decisões",
        "text": "Explore indicadores e identifique tendências com análises visuais.",
        "layers": [
            ("fundo_slide2.png", "left:-18%; top:0; width:115%; opacity:.9;", None),
            ("square_slide2.png", "right:6%; top:10%; width:24%;", 0.2),
            ("card_slide2.png", "left:6%; top:29%; width:90%;", 0.6),
            ("elem_slide2.png", "left:4%; top:60%; width:22%;", 1.1),
        ],
    },
    {
        "title": "Compare. Analise. Planeje.",
        "text": "Compare cenários financeiros e descubra novas possibilidades para o planejamento.",
        "layers": [
            ("fundo_slide3.png", "left:0; top:0; width:100%;", None),
            ("card_slide3.png", "left:4%; top:34%; width:96%;", 0.5),
            ("elem_slide3.png", "right:8%; top:70%; width:19%;", 1.0),
        ],
    },
]

STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html,
body {
    width: 100%;
    height: 100%;
    background: transparent;
}

body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    overflow: hidden;
}

.carousel {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    container-type: size;
    background: linear-gradient(165deg, #0B2859 0%, #174D83 55%, #267DB2 100%);
}

.track {
    display: flex;
    width: 100%;
    height: 100%;
    transition: transform 0.7s cubic-bezier(.65, 0, .35, 1);
}

.slide {
    --u: min(1cqw, calc((100cqh - 120px) / 100));
    position: relative;
    flex: 0 0 100%;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.stage {
    position: absolute;
    top: 0;
    left: 50%;
    width: calc(var(--u) * 100);
    height: calc(var(--u) * 100);
    transform: translateX(-50%);
}

.layer {
    position: absolute;
    height: auto;
    max-width: none;
}

.floating {
    animation: float 4s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

.caption {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 52px;
    padding: 0 8%;
    text-align: center;
    color: #FFFFFF;
    z-index: 5;
}

.caption h2 {
    font-size: clamp(17px, 5cqw, 23px);
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 10px;
}

.caption p {
    font-size: clamp(11px, 2.7cqw, 13px);
    line-height: 1.5;
    opacity: 0.9;
}

.dots {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 26px;
    display: flex;
    justify-content: center;
    gap: 8px;
    z-index: 6;
}

.dot {
    width: 7px;
    height: 7px;
    border: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.45);
    cursor: pointer;
    transition: background 0.3s;
}

.dot.active {
    background: #FFFFFF;
}

@media (prefers-reduced-motion: reduce) {
    .track,
    .floating {
        transition: none;
        animation: none;
    }
}
"""

SCRIPT = """
const frame = window.frameElement;

function fit() {
    try {
        const target = window.parent.document.querySelector('.st-key-auth_content');
        if (frame && target) {
            frame.style.height = target.offsetHeight + 'px';
        }
    } catch (e) {}
}

fit();
setTimeout(fit, 300);

try {
    const target = window.parent.document.querySelector('.st-key-auth_content');
    if (target) {
        new window.parent.ResizeObserver(fit).observe(target);
    }
} catch (e) {}

const track = document.querySelector('.track');
const dots = [...document.querySelectorAll('.dot')];

let current = 0;
let timer;

function go(index) {
    current = (index + dots.length) % dots.length;
    track.style.transform = `translateX(-${current * 100}%)`;
    dots.forEach((dot, i) => dot.classList.toggle('active', i === current));
}

function start() {
    clearInterval(timer);
    timer = setInterval(() => go(current + 1), 4500);
}

dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
        go(i);
        start();
    });
});

start();
"""


@lru_cache(maxsize=None)
def _encode(filename):
    return base64.b64encode((ASSETS / filename).read_bytes()).decode("utf-8")


def _render_layer(filename, style, delay):
    css_class = "layer" if delay is None else "layer floating"
    delay_style = "" if delay is None else f"animation-delay:{delay}s;"

    return (
        f'<img class="{css_class}" style="{style}{delay_style}" '
        f'src="data:image/png;base64,{_encode(filename)}" alt="">'
    )


def _render_slide(slide):
    layers = "".join(_render_layer(*layer) for layer in slide["layers"])

    return (
        '<div class="slide">'
        f'<div class="stage">{layers}</div>'
        '<div class="caption">'
        f'<h2>{escape(slide["title"])}</h2>'
        f'<p>{escape(slide["text"])}</p>'
        '</div>'
        '</div>'
    )


def render_carousel(height=620):
    slides = "".join(_render_slide(slide) for slide in SLIDES)

    dots = "".join(
        f'<button class="dot{" active" if i == 0 else ""}" '
        f'type="button" aria-label="Slide {i + 1}"></button>'
        for i in range(len(SLIDES))
    )

    html = f"""
    <style>{STYLE}</style>
    <div class="carousel">
        <div class="track">{slides}</div>
        <div class="dots">{dots}</div>
    </div>
    <script>{SCRIPT}</script>
    """

    components.html(html, height=height, scrolling=False)