import json
import math as _math
import os

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition, NoTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, TwoLineListItem, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivy.uix.widget import Widget
from kivy.clock import Clock

# ── Data loading ──────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load(name):
    with open(os.path.join(DATA_DIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


# ── Math solver (same logic as Flask app) ─────────────────────────────────────

def solve_media_ponderada(values, weights):
    total_w = sum(weights)
    if total_w == 0:
        raise ValueError("Soma dos pesos não pode ser zero.")
    result = sum(v * w for v, w in zip(values, weights)) / total_w
    steps = [f"Nota {i+1}: {v} × {w} = {v*w}" for i, (v, w) in enumerate(zip(values, weights))]
    steps += [f"Soma ponderada: {sum(v*w for v,w in zip(values,weights))}",
              f"Soma dos pesos: {total_w}",
              f"Média = {round(result, 2)}"]
    return round(result, 2), steps


def solve_fatorial(n):
    if n < 0 or n > 20:
        raise ValueError("Use um inteiro entre 0 e 20.")
    result = _math.factorial(n)
    return result, [f"{n}! = {' × '.join(str(i) for i in range(n,0,-1)) or '1'} = {result}"]


def solve_eq1(a, b):
    if a == 0:
        return ("∞ soluções" if b == 0 else "Sem solução"), []
    x = -b / a
    return round(x, 6), [f"{a}x + {b} = 0", f"{a}x = {-b}", f"x = {round(x,6)}"]


def solve_eq2(a, b, c):
    if a == 0:
        return solve_eq1(b, c)
    d = b**2 - 4*a*c
    steps = [f"Δ = {b}² - 4×{a}×{c} = {d}"]
    if d < 0:
        return "Sem raízes reais (Δ < 0)", steps
    sd = _math.sqrt(d)
    x1 = (-b + sd) / (2*a)
    x2 = (-b - sd) / (2*a)
    steps += [f"√Δ = {round(sd,4)}", f"x₁ = {round(x1,4)}", f"x₂ = {round(x2,4)}"]
    if d == 0:
        return f"x = {round(x1,6)} (raiz dupla)", steps
    return f"x₁ = {round(x1,4)}   x₂ = {round(x2,4)}", steps


def calc_area(shape, vals):
    if shape == "Círculo":
        r = vals[0]; v = _math.pi * r**2
        return round(v,4), [f"A = π × {r}² = {round(v,4)}"]
    if shape == "Quadrado":
        l = vals[0]; v = l**2
        return v, [f"A = {l}² = {v}"]
    if shape == "Retângulo":
        b,h = vals; v = b*h
        return v, [f"A = {b} × {h} = {v}"]
    if shape == "Triângulo":
        b,h = vals; v = b*h/2
        return v, [f"A = ({b} × {h}) / 2 = {v}"]
    if shape == "Trapézio":
        B,b,h = vals; v = (B+b)*h/2
        return v, [f"A = (({B}+{b}) × {h}) / 2 = {v}"]
    raise ValueError(f"Forma desconhecida: {shape}")


def calc_volume(shape, vals):
    if shape == "Cubo":
        a = vals[0]; v = a**3
        return v, [f"V = {a}³ = {v}"]
    if shape == "Paralelepípedo":
        c,l,a = vals; v = c*l*a
        return v, [f"V = {c} × {l} × {a} = {v}"]
    if shape == "Esfera":
        r = vals[0]; v = 4/3*_math.pi*r**3
        return round(v,4), [f"V = (4/3) × π × {r}³ = {round(v,4)}"]
    if shape == "Cilindro":
        r,h = vals; v = _math.pi*r**2*h
        return round(v,4), [f"V = π × {r}² × {h} = {round(v,4)}"]
    if shape == "Cone":
        r,h = vals; v = _math.pi*r**2*h/3
        return round(v,4), [f"V = (π × {r}² × {h}) / 3 = {round(v,4)}"]
    raise ValueError(f"Sólido desconhecido: {shape}")


def calc_perimetro(shape, vals):
    if shape == "Círculo":
        r = vals[0]; v = 2*_math.pi*r
        return round(v,4), [f"P = 2 × π × {r} = {round(v,4)}"]
    if shape == "Quadrado":
        l = vals[0]; v = 4*l
        return v, [f"P = 4 × {l} = {v}"]
    if shape == "Retângulo":
        b,h = vals; v = 2*(b+h)
        return v, [f"P = 2 × ({b}+{h}) = {v}"]
    if shape == "Triângulo":
        a,b,c = vals; v = a+b+c
        return v, [f"P = {a}+{b}+{c} = {v}"]
    raise ValueError(f"Forma desconhecida: {shape}")


# ── Reusable Widgets ──────────────────────────────────────────────────────────

def section_label(text, color="#4f46e5"):
    return MDLabel(
        text=text, font_style="H6", bold=True,
        theme_text_color="Custom", text_color=get_hex(color),
        size_hint_y=None, height=dp(40), padding=[dp(16), 0],
    )


def body_label(text, color=None):
    lbl = MDLabel(
        text=text, font_style="Body1",
        theme_text_color="Custom" if color else "Secondary",
        text_color=get_hex(color) if color else None,
        size_hint_y=None,
        padding=[dp(16), dp(4)],
    )
    lbl.bind(texture_size=lambda *_: lbl.setter("height")(lbl, lbl.texture_size[1] + dp(8)))
    return lbl


def get_hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0,2,4)) + (1,)


def spacer(h=8):
    w = Widget(size_hint_y=None, height=dp(h))
    return w


def make_card(padding=16, radius=12, elevation=2, **kwargs):
    return MDCard(
        padding=dp(padding), radius=[dp(radius)],
        elevation=elevation, size_hint_y=None,
        **kwargs
    )


def scrollable_box():
    scroll = MDScrollView()
    box = MDBoxLayout(
        orientation="vertical",
        size_hint_y=None,
        spacing=dp(8),
        padding=[dp(12), dp(8)],
    )
    box.bind(minimum_height=box.setter("height"))
    scroll.add_widget(box)
    return scroll, box


def toolbar(title, app, show_back=True):
    bar = MDTopAppBar(title=title, elevation=2)
    if show_back:
        bar.left_action_items = [["arrow-left", lambda x: app.go_back()]]
    return bar


# ── Base Screen ───────────────────────────────────────────────────────────────

class BaseScreen(MDScreen):
    def on_back(self):
        MDApp.get_running_app().go_back()


# ── HOME ──────────────────────────────────────────────────────────────────────

class HomeScreen(BaseScreen):
    def build(self):
        app = MDApp.get_running_app()
        root = MDBoxLayout(orientation="vertical")

        bar = MDTopAppBar(title="Aprenda+", elevation=2)
        root.add_widget(bar)

        scroll, box = scrollable_box()

        greeting = MDLabel(
            text="O que você quer aprender hoje?",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            size_hint_y=None, height=dp(40),
            padding=[dp(16), 0],
        )
        box.add_widget(greeting)
        box.add_widget(spacer(4))

        modules = [
            ("🐍  Python", "Do zero ao avançado", "#1e293b", "python_hub"),
            ("📐  Matemática", "Equações, geometria e mais", "#4f46e5", "math_hub"),
            ("📝  Português", "Gramática e redação", "#059669", "pt_hub"),
            ("🇺🇸  Inglês", "A1 até C1", "#dc2626", "en_hub"),
        ]

        for title, sub, color, target in modules:
            card = make_card(height=dp(88))
            card.md_bg_color = get_hex(color)
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=title, font_style="H6", bold=True,
                theme_text_color="Custom", text_color=(1,1,1,1),
                size_hint_y=None, height=dp(36),
            ))
            inner.add_widget(MDLabel(
                text=sub, font_style="Body2",
                theme_text_color="Custom", text_color=(1,1,1,.75),
                size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            card.bind(on_release=lambda _, t=target: app.navigate(t))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


# ── PYTHON ────────────────────────────────────────────────────────────────────

class PythonHubScreen(BaseScreen):
    def build(self):
        app = MDApp.get_running_app()
        data = app.py_data

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar("🐍 Python", app))

        scroll, box = scrollable_box()

        colors = {"basico": "#16a34a", "intermediario": "#ca8a04", "avancado": "#dc2626"}

        for level in data["levels"]:
            color = colors.get(level["id"], "#6b7280")
            card = make_card(height=dp(80))
            card.md_bg_color = get_hex(color)
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=f"{level['icon']}  {level['name']}",
                font_style="H6", bold=True,
                theme_text_color="Custom", text_color=(1,1,1,1),
                size_hint_y=None, height=dp(34),
            ))
            inner.add_widget(MDLabel(
                text=f"{level['description']} — {len(level['topics'])} tópicos",
                font_style="Body2",
                theme_text_color="Custom", text_color=(1,1,1,.8),
                size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            level_id = level["id"]
            card.bind(on_release=lambda _, lid=level_id: app.open_py_level(lid))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


class PythonLevelScreen(BaseScreen):
    def build(self, level):
        app = MDApp.get_running_app()
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(f"🌿 {level['name']}", app))

        scroll, box = scrollable_box()

        for i, topic in enumerate(level["topics"]):
            card = make_card(height=dp(76))
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=f"{i+1}. {topic['title']}",
                font_style="Subtitle1", bold=True,
                theme_text_color="Primary",
                size_hint_y=None, height=dp(32),
            ))
            badges = []
            if topic.get("code_examples"):
                badges.append(f"💻 {len(topic['code_examples'])} exemplos")
            if topic.get("quiz"):
                badges.append(f"🧠 {len(topic['quiz'])} questões")
            inner.add_widget(MDLabel(
                text="  ".join(badges) if badges else topic["explanation"][:60] + "...",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            lid = level["id"]
            tid = topic["id"]
            card.bind(on_release=lambda _, l=lid, t=tid: app.open_py_topic(l, t))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


class PythonTopicScreen(BaseScreen):
    def build(self, level_id, topic):
        app = MDApp.get_running_app()
        self._quiz_state = {}

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(topic["title"], app))

        scroll, box = scrollable_box()

        # Explanation
        card = make_card()
        card.md_bg_color = get_hex("#1e293b")
        exp = MDLabel(
            text=topic["explanation"],
            font_style="Body1",
            theme_text_color="Custom", text_color=(1,1,1,.9),
            size_hint_y=None,
        )
        exp.bind(texture_size=lambda *_: exp.setter("height")(exp, exp.texture_size[1]+dp(8)))
        card.add_widget(exp)
        box.add_widget(card)

        # Concepts
        if topic.get("concepts"):
            box.add_widget(section_label("💡 Conceitos-chave"))
            for c in topic["concepts"]:
                chip = MDLabel(
                    text=f"• {c}", font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    padding=[dp(8), dp(2)],
                )
                chip.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                box.add_widget(chip)
            box.add_widget(spacer(4))

        # Code examples
        if topic.get("code_examples"):
            box.add_widget(section_label("💻 Exemplos de Código", "#1e293b"))
            for ex in topic["code_examples"]:
                box.add_widget(MDLabel(
                    text=ex["title"], font_style="Subtitle2", bold=True,
                    theme_text_color="Primary",
                    size_hint_y=None, height=dp(28), padding=[dp(4), 0],
                ))
                # Code block
                code_card = make_card(padding=12, radius=8)
                code_card.md_bg_color = get_hex("#0f172a")
                code_lbl = MDLabel(
                    text=ex["code"],
                    font_style="Body2", font_name="RobotoMono" if False else "",
                    theme_text_color="Custom", text_color=get_hex("#a3e635"),
                    size_hint_y=None,
                )
                code_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
                code_card.add_widget(code_lbl)
                box.add_widget(code_card)
                # Output
                if ex.get("output"):
                    out_lbl = MDLabel(
                        text=f"▶ {ex['output']}",
                        font_style="Caption",
                        theme_text_color="Custom", text_color=get_hex("#64748b"),
                        size_hint_y=None, padding=[dp(4), 0],
                    )
                    out_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                    box.add_widget(out_lbl)
                # Explanation
                if ex.get("explanation"):
                    hint = MDLabel(
                        text=f"ℹ {ex['explanation']}",
                        font_style="Caption", italic=True,
                        theme_text_color="Secondary",
                        size_hint_y=None, padding=[dp(4), 0],
                    )
                    hint.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                    box.add_widget(hint)
                box.add_widget(spacer(4))

        # Quiz
        if topic.get("quiz"):
            box.add_widget(section_label("🧠 Mini-Quiz", "#7c3aed"))
            for qi, q in enumerate(topic["quiz"]):
                box.add_widget(MDLabel(
                    text=f"Q{qi+1}: {q['question']}",
                    font_style="Subtitle2", bold=True,
                    theme_text_color="Primary",
                    size_hint_y=None, padding=[dp(4), dp(4)],
                ))
                box.bind(texture_size=lambda w, ts, *_: None)
                for oi, opt in enumerate(q["options"]):
                    btn = MDRaisedButton(
                        text=f"{['A','B','C','D'][oi]}. {opt}",
                        size_hint=(1, None), height=dp(44),
                        md_bg_color=get_hex("#e2e8f0"),
                        text_color=get_hex("#1e293b"),
                        elevation=0,
                    )
                    btn.bind(on_release=lambda b, qi=qi, oi=oi, correct=q["answer"],
                             exp=q["explanation"], opts=None: self._check_quiz(b, qi, oi, correct, exp, box, q["options"]))
                    box.add_widget(btn)
                    self._quiz_state.setdefault(qi, {})["btn_"+str(oi)] = btn
                box.add_widget(spacer(8))

        root.add_widget(scroll)
        self.add_widget(root)

    def _check_quiz(self, btn, qi, selected, correct, explanation, box, options):
        state = self._quiz_state.get(qi, {})
        if state.get("answered"):
            return
        state["answered"] = True
        for oi in range(len(options)):
            b = state.get("btn_"+str(oi))
            if b:
                b.disabled = True
                if oi == correct:
                    b.md_bg_color = get_hex("#dcfce7")
                    b.text_color = get_hex("#166534")
                elif oi == selected:
                    b.md_bg_color = get_hex("#fee2e2")
                    b.text_color = get_hex("#991b1b")
        msg = ("✓ Correto! " if selected == correct else "✗ Incorreto. ") + explanation
        Snackbar(text=msg, snackbar_x=dp(8), snackbar_y=dp(8),
                 size_hint_x=0.95, duration=4).open()


# ── MATH ──────────────────────────────────────────────────────────────────────

MATH_CALCS = [
    ("⚖️", "Média\nPonderada", "media"),
    ("🔢", "Fatorial", "fatorial"),
    ("📏", "Equação\n1° Grau", "eq1"),
    ("📊", "Bhaskara\n2° Grau", "eq2"),
    ("🔷", "Área", "area"),
    ("📦", "Volume", "volume"),
    ("📐", "Perímetro", "perimetro"),
]


class MathHubScreen(BaseScreen):
    def build(self):
        app = MDApp.get_running_app()
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar("📐 Matemática", app))

        scroll, box = scrollable_box()
        box.add_widget(section_label("Selecione a calculadora", "#4f46e5"))

        grid = MDGridLayout(cols=3, spacing=dp(10), size_hint_y=None,
                            padding=[dp(4), dp(4)])
        grid.bind(minimum_height=grid.setter("height"))

        for emoji, label, calc_id in MATH_CALCS:
            card = make_card(padding=10, height=dp(88), elevation=1)
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=emoji, font_style="H5",
                halign="center", size_hint_y=None, height=dp(40),
            ))
            inner.add_widget(MDLabel(
                text=label, font_style="Caption",
                halign="center", size_hint_y=None, height=dp(36),
                theme_text_color="Secondary",
            ))
            card.add_widget(inner)
            cid = calc_id
            card.bind(on_release=lambda _, c=cid: app.open_math(c))
            grid.add_widget(card)

        box.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)


class MathCalcScreen(BaseScreen):
    def build(self, calc_id):
        self._calc_id = calc_id
        self._fields = []
        app = MDApp.get_running_app()

        titles = {
            "media": "⚖️ Média Ponderada", "fatorial": "🔢 Fatorial",
            "eq1": "📏 Equação 1° Grau", "eq2": "📊 Bhaskara",
            "area": "🔷 Área", "volume": "📦 Volume", "perimetro": "📐 Perímetro",
        }

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(titles.get(calc_id, "Calculadora"), app))

        scroll, box = scrollable_box()

        # Form config
        configs = {
            "media":     (["Notas (separadas por vírgula)", "Pesos (mesma ordem)"], "Calcular Média"),
            "fatorial":  (["Número inteiro (0–20)"], "Calcular Fatorial"),
            "eq1":       (["Coeficiente a (de x)", "Coeficiente b"], "Resolver ax + b = 0"),
            "eq2":       (["Coeficiente a (de x²)", "Coeficiente b (de x)", "Coeficiente c"], "Resolver com Bhaskara"),
            "area":      (["Figura: Círculo/Quadrado/Retângulo/Triângulo/Trapézio",
                           "Valor 1 (raio ou lado ou base)",
                           "Valor 2 (altura, se necessário)",
                           "Valor 3 (base menor, se trapézio)"], "Calcular Área"),
            "volume":    (["Sólido: Cubo/Paralelepípedo/Esfera/Cilindro/Cone",
                           "Valor 1 (aresta ou raio)",
                           "Valor 2 (largura, se necessário)",
                           "Valor 3 (altura, se necessário)"], "Calcular Volume"),
            "perimetro": (["Figura: Círculo/Quadrado/Retângulo/Triângulo",
                           "Valor 1", "Valor 2 (se necessário)", "Valor 3 (se triângulo)"], "Calcular Perímetro"),
        }

        field_labels, btn_label = configs.get(calc_id, (["Valor"], "Calcular"))

        hints = {
            "media": ["Ex: 8, 7.5, 9", "Ex: 2, 3, 1"],
            "fatorial": ["Ex: 7"],
            "eq1": ["Ex: 3", "Ex: -9"],
            "eq2": ["Ex: 1", "Ex: -5", "Ex: 6"],
        }
        field_hints = hints.get(calc_id, [])

        for i, label in enumerate(field_labels):
            tf = MDTextField(
                hint_text=label,
                helper_text=field_hints[i] if i < len(field_hints) else "",
                helper_text_mode="on_focus",
                size_hint_y=None, height=dp(64),
            )
            box.add_widget(tf)
            self._fields.append(tf)

        btn = MDRaisedButton(
            text=btn_label,
            size_hint=(1, None), height=dp(48),
            md_bg_color=get_hex("#4f46e5"),
        )
        btn.bind(on_release=self._calculate)
        box.add_widget(btn)
        box.add_widget(spacer(8))

        self._result_card = make_card(padding=16)
        self._result_card.md_bg_color = get_hex("#4f46e5")
        self._result_label = MDLabel(
            text="", font_style="H5", bold=True,
            theme_text_color="Custom", text_color=(1,1,1,1),
            size_hint_y=None, height=dp(48),
            halign="center",
        )
        self._steps_label = MDLabel(
            text="", font_style="Body2",
            theme_text_color="Custom", text_color=(1,1,1,.85),
            size_hint_y=None,
        )
        self._steps_label.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        self._result_card.add_widget(MDBoxLayout(
            orientation="vertical",
            size_hint_y=None, height=dp(120),
        ))
        # rebuild result card lazily
        self._result_box = box
        self._result_card.opacity = 0
        box.add_widget(self._result_card)

        root.add_widget(scroll)
        self.add_widget(root)

    def _get_floats(self, field):
        return [float(x.strip()) for x in field.text.split(",")]

    def _calculate(self, *_):
        cid = self._calc_id
        fields = self._fields
        try:
            if cid == "media":
                vals = self._get_floats(fields[0])
                weights = self._get_floats(fields[1])
                res, steps = solve_media_ponderada(vals, weights)
            elif cid == "fatorial":
                n = int(fields[0].text.strip())
                res, steps = solve_fatorial(n)
            elif cid == "eq1":
                a, b = float(fields[0].text), float(fields[1].text)
                res, steps = solve_eq1(a, b)
            elif cid == "eq2":
                a = float(fields[0].text)
                b = float(fields[1].text)
                c = float(fields[2].text)
                res, steps = solve_eq2(a, b, c)
            elif cid == "area":
                shape = fields[0].text.strip().capitalize()
                v_fields = [float(fields[i].text) for i in range(1,4) if fields[i].text.strip()]
                res, steps = calc_area(shape, v_fields)
            elif cid == "volume":
                shape = fields[0].text.strip().capitalize()
                v_fields = [float(fields[i].text) for i in range(1,4) if fields[i].text.strip()]
                res, steps = calc_volume(shape, v_fields)
            elif cid == "perimetro":
                shape = fields[0].text.strip().capitalize()
                v_fields = [float(fields[i].text) for i in range(1,4) if fields[i].text.strip()]
                res, steps = calc_perimetro(shape, v_fields)
            else:
                res, steps = "?", []

            self._result_card.clear_widgets()
            inner = MDBoxLayout(orientation="vertical", size_hint_y=None,
                                spacing=dp(4))
            inner.bind(minimum_height=inner.setter("height"))
            inner.add_widget(MDLabel(
                text=f"= {res}", font_style="H5", bold=True,
                theme_text_color="Custom", text_color=(1,1,1,1),
                halign="center", size_hint_y=None, height=dp(48),
            ))
            for s in steps:
                lbl = MDLabel(
                    text=s, font_style="Body2",
                    theme_text_color="Custom", text_color=(1,1,1,.85),
                    size_hint_y=None,
                )
                lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                inner.add_widget(lbl)
            self._result_card.add_widget(inner)
            self._result_card.opacity = 1
            self._result_card.height = None  # let it auto-size
            self._result_card.size_hint_y = None
            self._result_card.bind(minimum_height=self._result_card.setter("height"))
        except Exception as e:
            Snackbar(text=f"Erro: {e}", snackbar_x=dp(8), snackbar_y=dp(8),
                     size_hint_x=.95, duration=3).open()


# ── PORTUGUESE ────────────────────────────────────────────────────────────────

class PtHubScreen(BaseScreen):
    def build(self):
        app = MDApp.get_running_app()
        data = app.pt_data

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar("📝 Português", app))

        scroll, box = scrollable_box()

        # Concept cards
        box.add_widget(section_label("🗂️ Conceitos Gramaticais", "#059669"))
        grid = MDGridLayout(cols=3, spacing=dp(10), size_hint_y=None, padding=[dp(4),0])
        grid.bind(minimum_height=grid.setter("height"))

        for c in data["conceitos"]:
            card = make_card(padding=10, elevation=1)
            card.size_hint_y = None
            card.height = dp(80)
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=c["emoji"], font_style="H5",
                halign="center", size_hint_y=None, height=dp(38),
            ))
            inner.add_widget(MDLabel(
                text=c["nome"], font_style="Caption",
                halign="center", size_hint_y=None, height=dp(24),
                theme_text_color="Secondary",
            ))
            card.add_widget(inner)
            cid = c["id"]
            card.bind(on_release=lambda _, cid=cid: app.open_pt_concept(cid))
            grid.add_widget(card)

        box.add_widget(grid)
        box.add_widget(spacer(12))

        # Grammar rules
        box.add_widget(section_label("🔤 Gramática Prática", "#059669"))
        for g in data["redacao"]["gramatica"]:
            card = make_card(height=dp(64))
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=g["topico"], font_style="Subtitle1", bold=True,
                theme_text_color="Primary", size_hint_y=None, height=dp(32),
            ))
            inner.add_widget(MDLabel(
                text=g["regra"][:70] + "...",
                font_style="Caption",
                theme_text_color="Secondary", size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            topico = g["topico"]
            card.bind(on_release=lambda _, t=topico: app.open_pt_grammar(t))
            box.add_widget(card)

        # Redação
        box.add_widget(spacer(12))
        box.add_widget(section_label("✍️ Guia de Redação", "#059669"))
        for tipo in data["redacao"]["tipos"]:
            card = make_card(height=dp(64))
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=tipo["nome"], font_style="Subtitle1", bold=True,
                theme_text_color="Primary", size_hint_y=None, height=dp(32),
            ))
            inner.add_widget(MDLabel(
                text=tipo["descricao"][:70] + "...",
                font_style="Caption",
                theme_text_color="Secondary", size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            nome = tipo["nome"]
            card.bind(on_release=lambda _, n=nome: app.open_pt_essay(n))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


class PtConceptScreen(BaseScreen):
    def build(self, conceito):
        app = MDApp.get_running_app()
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(f"{conceito['emoji']} {conceito['nome']}", app))

        scroll, box = scrollable_box()

        # Header card
        hcard = make_card()
        hcard.md_bg_color = get_hex("#059669")
        hbox = MDBoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        hbox.bind(minimum_height=hbox.setter("height"))
        hbox.add_widget(MDLabel(
            text=conceito["definicao"],
            font_style="Body1",
            theme_text_color="Custom", text_color=(1,1,1,.95),
            size_hint_y=None,
        ))
        hbox.children[0].bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        hcard.add_widget(hbox)
        box.add_widget(hcard)

        # Tip
        tip_card = make_card()
        tip_card.md_bg_color = get_hex("#f0fdf4")
        tip_lbl = MDLabel(
            text=f"💡 {conceito['dica']}",
            font_style="Body2", italic=True,
            theme_text_color="Custom", text_color=get_hex("#166534"),
            size_hint_y=None,
        )
        tip_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        tip_card.add_widget(tip_lbl)
        box.add_widget(tip_card)

        # Examples
        box.add_widget(section_label("Exemplos", "#059669"))
        examples_lbl = MDLabel(
            text="  •  ".join(conceito["exemplos"]),
            font_style="Body2",
            theme_text_color="Secondary", size_hint_y=None, padding=[dp(8), 0],
        )
        examples_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        box.add_widget(examples_lbl)

        # Sample phrases
        if conceito.get("frases"):
            box.add_widget(section_label("Frases", "#059669"))
            for f in conceito["frases"]:
                fl = MDLabel(
                    text=f"• {f.replace('**', '')}",
                    font_style="Body2",
                    theme_text_color="Primary", size_hint_y=None, padding=[dp(8), dp(2)],
                )
                fl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                box.add_widget(fl)

        # Subcategories
        if conceito.get("subcategorias"):
            box.add_widget(section_label("Tipos", "#059669"))
            for sub in conceito["subcategorias"]:
                sub_card = make_card(padding=12, elevation=0)
                sub_card.md_bg_color = get_hex("#f1f5f9")
                sub_box = MDBoxLayout(orientation="vertical", size_hint_y=None)
                sub_box.bind(minimum_height=sub_box.setter("height"))
                sub_box.add_widget(MDLabel(
                    text=sub["nome"], font_style="Subtitle2", bold=True,
                    theme_text_color="Custom", text_color=get_hex("#059669"),
                    size_hint_y=None, height=dp(28),
                ))
                ex_lbl = MDLabel(
                    text=sub["ex"], font_style="Caption",
                    theme_text_color="Secondary", size_hint_y=None,
                )
                ex_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                sub_box.add_widget(ex_lbl)
                sub_card.add_widget(sub_box)
                box.add_widget(sub_card)

        root.add_widget(scroll)
        self.add_widget(root)


class PtGrammarScreen(BaseScreen):
    def build(self, topico_nome):
        app = MDApp.get_running_app()
        data = app.pt_data
        topico = next((g for g in data["redacao"]["gramatica"] if g["topico"] == topico_nome), None)

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(topico_nome, app))

        scroll, box = scrollable_box()

        if not topico:
            box.add_widget(body_label("Conteúdo não encontrado."))
            root.add_widget(scroll)
            self.add_widget(root)
            return

        rule_card = make_card()
        rule_card.md_bg_color = get_hex("#f0fdf4")
        rule_lbl = MDLabel(
            text=f"📌 {topico['regra']}", font_style="Body1",
            theme_text_color="Custom", text_color=get_hex("#166534"),
            size_hint_y=None,
        )
        rule_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        rule_card.add_widget(rule_lbl)
        box.add_widget(rule_card)

        for ex in topico["exemplos"]:
            ecard = make_card(elevation=0)
            ecard.md_bg_color = get_hex("#fafafa")
            eb = MDBoxLayout(orientation="vertical", size_hint_y=None)
            eb.bind(minimum_height=eb.setter("height"))
            errado = MDLabel(
                text=f"✗  {ex['errado']}", font_style="Body2",
                theme_text_color="Custom", text_color=get_hex("#dc2626"),
                size_hint_y=None,
            )
            errado.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
            certo = MDLabel(
                text=f"✓  {ex['certo']}", font_style="Body2",
                theme_text_color="Custom", text_color=get_hex("#166534"),
                size_hint_y=None, bold=True,
            )
            certo.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
            exp_lbl = MDLabel(
                text=f"ℹ  {ex['explicacao']}", font_style="Caption",
                theme_text_color="Secondary", size_hint_y=None, italic=True,
            )
            exp_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
            eb.add_widget(errado)
            eb.add_widget(certo)
            eb.add_widget(exp_lbl)
            ecard.add_widget(eb)
            box.add_widget(ecard)

        root.add_widget(scroll)
        self.add_widget(root)


class PtEssayScreen(BaseScreen):
    def build(self, tipo_nome):
        app = MDApp.get_running_app()
        data = app.pt_data
        tipo = next((t for t in data["redacao"]["tipos"] if t["nome"] == tipo_nome), None)

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(tipo_nome, app))

        scroll, box = scrollable_box()

        if not tipo:
            root.add_widget(scroll)
            self.add_widget(root)
            return

        desc = MDLabel(
            text=tipo["descricao"], font_style="Body1",
            theme_text_color="Secondary", size_hint_y=None, padding=[dp(4), dp(4)],
        )
        desc.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
        box.add_widget(desc)

        for parte in tipo["estrutura"]:
            pc = make_card(elevation=1)
            pb = MDBoxLayout(orientation="vertical", size_hint_y=None)
            pb.bind(minimum_height=pb.setter("height"))
            pb.add_widget(MDLabel(
                text=parte["parte"], font_style="Subtitle1", bold=True,
                theme_text_color="Custom", text_color=get_hex("#059669"),
                size_hint_y=None, height=dp(30),
            ))
            for dica in parte["dicas"]:
                dl = MDLabel(
                    text=f"• {dica}", font_style="Body2",
                    theme_text_color="Primary", size_hint_y=None,
                )
                dl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                pb.add_widget(dl)
            pc.add_widget(pb)
            box.add_widget(pc)

        if tipo.get("conectivos"):
            box.add_widget(section_label("📌 Conectivos", "#059669"))
            for cat, lista in tipo["conectivos"].items():
                cl = MDLabel(
                    text=f"[b]{cat.capitalize()}:[/b] {', '.join(lista)}",
                    font_style="Body2", markup=True,
                    theme_text_color="Primary", size_hint_y=None, padding=[dp(4), dp(2)],
                )
                cl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                box.add_widget(cl)

        root.add_widget(scroll)
        self.add_widget(root)


# ── ENGLISH ───────────────────────────────────────────────────────────────────

EN_COLORS = {"A1":"#16a34a","A2":"#65a30d","B1":"#ca8a04","B2":"#ea580c","C1":"#dc2626"}


class EnHubScreen(BaseScreen):
    def build(self):
        app = MDApp.get_running_app()
        data = app.en_data

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar("🇺🇸 Inglês", app))

        scroll, box = scrollable_box()
        box.add_widget(section_label("Selecione seu nível", "#dc2626"))

        for level in data["levels"]:
            color = EN_COLORS.get(level["id"], "#6b7280")
            card = make_card(height=dp(76))
            card.md_bg_color = get_hex(color)
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=f"{level['id']} — {level['name_pt']}",
                font_style="H6", bold=True,
                theme_text_color="Custom", text_color=(1,1,1,1),
                size_hint_y=None, height=dp(34),
            ))
            inner.add_widget(MDLabel(
                text=level["description"],
                font_style="Body2",
                theme_text_color="Custom", text_color=(1,1,1,.8),
                size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            lid = level["id"]
            card.bind(on_release=lambda _, l=lid: app.open_en_level(l))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


class EnLevelScreen(BaseScreen):
    def build(self, level):
        app = MDApp.get_running_app()
        color = EN_COLORS.get(level["id"], "#dc2626")

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(f"{level['id']} — {level['name']}", app))

        scroll, box = scrollable_box()

        for topic in level["topics"]:
            card = make_card(height=dp(64))
            inner = MDBoxLayout(orientation="vertical", spacing=dp(2))
            inner.add_widget(MDLabel(
                text=topic["title"], font_style="Subtitle1", bold=True,
                theme_text_color="Primary", size_hint_y=None, height=dp(32),
            ))
            badges = []
            if topic.get("quiz"):
                badges.append(f"🧠 {len(topic['quiz'])} questões")
            if topic.get("grammar"):
                badges.append("📖 gramática")
            inner.add_widget(MDLabel(
                text="  ".join(badges) if badges else topic["title_pt"],
                font_style="Caption",
                theme_text_color="Secondary", size_hint_y=None, height=dp(24),
            ))
            card.add_widget(inner)
            lid = level["id"]
            tid = topic["id"]
            card.bind(on_release=lambda _, l=lid, t=tid: app.open_en_topic(l, t))
            box.add_widget(card)

        root.add_widget(scroll)
        self.add_widget(root)


class EnTopicScreen(BaseScreen):
    def build(self, level_id, topic):
        app = MDApp.get_running_app()
        self._quiz_state = {}

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(toolbar(topic["title"], app))

        scroll, box = scrollable_box()

        # Vocabulary table
        if topic.get("content"):
            box.add_widget(section_label("📋 Vocabulário / Frases", "#dc2626"))
            for item in topic["content"]:
                row_card = make_card(padding=10, elevation=0)
                row_card.md_bg_color = get_hex("#f8fafc")
                row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
                row.add_widget(MDLabel(
                    text=item["english"], font_style="Body2", bold=True,
                    theme_text_color="Primary", size_hint_x=0.5,
                ))
                row.add_widget(MDLabel(
                    text=item["portuguese"], font_style="Body2",
                    theme_text_color="Secondary", size_hint_x=0.5,
                ))
                row_card.add_widget(row)
                box.add_widget(row_card)

        # Grammar
        if topic.get("grammar"):
            g = topic["grammar"]
            box.add_widget(section_label(f"📖 Gramática: {g['topic']}", "#dc2626"))
            exp_card = make_card()
            exp_card.md_bg_color = get_hex("#fef2f2")
            exp_lbl = MDLabel(
                text=g["explanation"], font_style="Body2",
                theme_text_color="Custom", text_color=get_hex("#7f1d1d"),
                size_hint_y=None,
            )
            exp_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(8)))
            exp_card.add_widget(exp_lbl)
            box.add_widget(exp_card)
            if g.get("rules"):
                for r in g["rules"]:
                    rl = MDLabel(
                        text=f"• {r}", font_style="Body2",
                        theme_text_color="Primary", size_hint_y=None, padding=[dp(4), dp(2)],
                    )
                    rl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                    box.add_widget(rl)
            if g.get("table"):
                for row_data in g["table"]:
                    rc = make_card(padding=8, elevation=0)
                    rc.md_bg_color = get_hex("#fff1f2")
                    rl = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
                    rl.add_widget(MDLabel(text=row_data["pronoun"], font_style="Body2", bold=True, size_hint_x=.25))
                    rl.add_widget(MDLabel(text=row_data["verb"], font_style="Body2",
                                          theme_text_color="Custom", text_color=get_hex("#dc2626"), size_hint_x=.2))
                    rl.add_widget(MDLabel(text=row_data["example"], font_style="Caption", size_hint_x=.55))
                    rc.add_widget(rl)
                    box.add_widget(rc)

        # Quiz
        if topic.get("quiz"):
            box.add_widget(section_label("🧠 Quiz", "#dc2626"))
            for qi, q in enumerate(topic["quiz"]):
                q_lbl = MDLabel(
                    text=f"Q{qi+1}: {q['question']}",
                    font_style="Subtitle2", bold=True,
                    theme_text_color="Primary", size_hint_y=None,
                    padding=[dp(4), dp(4)],
                )
                q_lbl.bind(texture_size=lambda w, ts, *_: w.setter("height")(w, ts[1]+dp(4)))
                box.add_widget(q_lbl)
                for oi, opt in enumerate(q["options"]):
                    btn = MDRaisedButton(
                        text=f"{['A','B','C','D'][oi]}. {opt}",
                        size_hint=(1, None), height=dp(44),
                        md_bg_color=get_hex("#fee2e2"),
                        text_color=get_hex("#1e293b"),
                        elevation=0,
                    )
                    btn.bind(on_release=lambda b, qi=qi, oi=oi, correct=q["answer"],
                             exp=q["explanation"], opts=q["options"]:
                             self._check_quiz(b, qi, oi, correct, exp, opts))
                    box.add_widget(btn)
                    self._quiz_state.setdefault(qi, {})["btn_"+str(oi)] = btn
                box.add_widget(spacer(8))

        root.add_widget(scroll)
        self.add_widget(root)

    def _check_quiz(self, btn, qi, selected, correct, explanation, options):
        state = self._quiz_state.get(qi, {})
        if state.get("answered"):
            return
        state["answered"] = True
        for oi in range(len(options)):
            b = state.get("btn_"+str(oi))
            if b:
                b.disabled = True
                if oi == correct:
                    b.md_bg_color = get_hex("#dcfce7")
                    b.text_color = get_hex("#166534")
                elif oi == selected:
                    b.md_bg_color = get_hex("#fee2e2")
                    b.text_color = get_hex("#991b1b")
        msg = ("✓ Correct! " if selected == correct else "✗ Incorrect. ") + explanation
        Snackbar(text=msg, snackbar_x=dp(8), snackbar_y=dp(8),
                 size_hint_x=.95, duration=4).open()


# ── APP ───────────────────────────────────────────────────────────────────────

class AprndaApp(MDApp):
    title = "Aprenda+"

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.theme_style = "Light"

        # Load data
        self.py_data = load("python")
        self.pt_data = load("portuguese")
        self.en_data = load("english")

        self._nav_stack = []

        self.sm = ScreenManager(transition=SlideTransition())
        self._build_home()
        return self.sm

    def _build_home(self):
        s = HomeScreen(name="home")
        s.build()
        self.sm.add_widget(s)
        self.sm.current = "home"

    def navigate(self, screen_name):
        self._nav_stack.append(self.sm.current)
        if screen_name not in [s.name for s in self.sm.screens]:
            self._build_hub(screen_name)
        self.sm.transition.direction = "left"
        self.sm.current = screen_name

    def go_back(self):
        if self._nav_stack:
            prev = self._nav_stack.pop()
            self.sm.transition.direction = "right"
            self.sm.current = prev

    def _build_hub(self, name):
        builders = {
            "python_hub": self._make_py_hub,
            "math_hub": self._make_math_hub,
            "pt_hub": self._make_pt_hub,
            "en_hub": self._make_en_hub,
        }
        if name in builders:
            builders[name]()

    def _make_py_hub(self):
        s = PythonHubScreen(name="python_hub"); s.build(); self.sm.add_widget(s)

    def _make_math_hub(self):
        s = MathHubScreen(name="math_hub"); s.build(); self.sm.add_widget(s)

    def _make_pt_hub(self):
        s = PtHubScreen(name="pt_hub"); s.build(); self.sm.add_widget(s)

    def _make_en_hub(self):
        s = EnHubScreen(name="en_hub"); s.build(); self.sm.add_widget(s)

    # Python navigation
    def open_py_level(self, level_id):
        level = next(l for l in self.py_data["levels"] if l["id"] == level_id)
        sname = f"py_level_{level_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = PythonLevelScreen(name=sname)
            s.build(level)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    def open_py_topic(self, level_id, topic_id):
        level = next(l for l in self.py_data["levels"] if l["id"] == level_id)
        topic = next(t for t in level["topics"] if t["id"] == topic_id)
        sname = f"py_topic_{level_id}_{topic_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = PythonTopicScreen(name=sname)
            s.build(level_id, topic)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    # Math navigation
    def open_math(self, calc_id):
        sname = f"math_{calc_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = MathCalcScreen(name=sname)
            s.build(calc_id)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    # Portuguese navigation
    def open_pt_concept(self, conceito_id):
        conceito = next(c for c in self.pt_data["conceitos"] if c["id"] == conceito_id)
        sname = f"pt_concept_{conceito_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = PtConceptScreen(name=sname)
            s.build(conceito)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    def open_pt_grammar(self, topico_nome):
        sname = f"pt_grammar_{topico_nome.replace(' ','_')}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = PtGrammarScreen(name=sname)
            s.build(topico_nome)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    def open_pt_essay(self, tipo_nome):
        sname = f"pt_essay_{tipo_nome.replace(' ','_')}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = PtEssayScreen(name=sname)
            s.build(tipo_nome)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    # English navigation
    def open_en_level(self, level_id):
        level = next(l for l in self.en_data["levels"] if l["id"] == level_id)
        sname = f"en_level_{level_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = EnLevelScreen(name=sname)
            s.build(level)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    def open_en_topic(self, level_id, topic_id):
        level = next(l for l in self.en_data["levels"] if l["id"] == level_id)
        topic = next(t for t in level["topics"] if t["id"] == topic_id)
        sname = f"en_topic_{level_id}_{topic_id}"
        self._nav_stack.append(self.sm.current)
        if sname not in [s.name for s in self.sm.screens]:
            s = EnTopicScreen(name=sname)
            s.build(level_id, topic)
            self.sm.add_widget(s)
        self.sm.transition.direction = "left"
        self.sm.current = sname

    def on_start(self):
        Window.bind(on_keyboard=self._handle_back)

    def _handle_back(self, window, key, *args):
        if key == 27:  # Android back button
            if self._nav_stack:
                self.go_back()
                return True
        return False


if __name__ == "__main__":
    AprndaApp().run()
