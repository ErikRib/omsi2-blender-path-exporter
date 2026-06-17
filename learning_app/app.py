import json
import os
from flask import Flask, render_template, request, jsonify
from modules.math_solver import (
    weighted_average, factorial, solve_first_degree, solve_second_degree,
    calculate_area, calculate_volume, calculate_perimeter,
    AREA_FORMULAS, VOLUME_FORMULAS, PERIMETER_FORMULAS,
)

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


# ── MATH ──────────────────────────────────────────────────────────────────────

@app.route("/math")
def math_index():
    return render_template("math/index.html")


@app.route("/math/media-ponderada", methods=["GET", "POST"])
def math_media():
    result = None
    error = None
    if request.method == "POST":
        try:
            raw_values = request.form.get("valores", "").strip()
            raw_weights = request.form.get("pesos", "").strip()
            values = [float(x) for x in raw_values.split(",")]
            weights = [float(x) for x in raw_weights.split(",")]
            result = weighted_average(values, weights)
        except ValueError as e:
            error = str(e)
        except Exception:
            error = "Verifique os valores inseridos."
    return render_template("math/media_ponderada.html", result=result, error=error)


@app.route("/math/fatorial", methods=["GET", "POST"])
def math_factorial():
    result = None
    error = None
    if request.method == "POST":
        try:
            n = int(request.form.get("n", ""))
            result = factorial(n)
        except ValueError as e:
            error = str(e)
    return render_template("math/fatorial.html", result=result, error=error)


@app.route("/math/equacao-1-grau", methods=["GET", "POST"])
def math_eq1():
    result = None
    error = None
    if request.method == "POST":
        try:
            a = float(request.form.get("a", ""))
            b = float(request.form.get("b", ""))
            result = solve_first_degree(a, b)
        except ValueError:
            error = "Insira valores numéricos válidos."
    return render_template("math/equacao1.html", result=result, error=error)


@app.route("/math/equacao-2-grau", methods=["GET", "POST"])
def math_eq2():
    result = None
    error = None
    if request.method == "POST":
        try:
            a = float(request.form.get("a", ""))
            b = float(request.form.get("b", ""))
            c = float(request.form.get("c", ""))
            result = solve_second_degree(a, b, c)
        except ValueError:
            error = "Insira valores numéricos válidos."
    return render_template("math/equacao2.html", result=result, error=error)


@app.route("/math/area", methods=["GET", "POST"])
def math_area():
    result = None
    error = None
    shape = None
    if request.method == "POST":
        try:
            shape = request.form.get("shape", "")
            params = AREA_FORMULAS[shape]["params"]
            kwargs = {p: float(request.form.get(p, "")) for p in params}
            result = calculate_area(shape, **kwargs)
        except KeyError:
            error = "Selecione uma forma geométrica."
        except ValueError:
            error = "Insira valores numéricos válidos."
    return render_template("math/area.html", formulas=AREA_FORMULAS, result=result, error=error, shape=shape)


@app.route("/math/volume", methods=["GET", "POST"])
def math_volume():
    result = None
    error = None
    shape = None
    if request.method == "POST":
        try:
            shape = request.form.get("shape", "")
            params = VOLUME_FORMULAS[shape]["params"]
            kwargs = {p: float(request.form.get(p, "")) for p in params}
            result = calculate_volume(shape, **kwargs)
        except KeyError:
            error = "Selecione um sólido geométrico."
        except ValueError:
            error = "Insira valores numéricos válidos."
    return render_template("math/volume.html", formulas=VOLUME_FORMULAS, result=result, error=error, shape=shape)


@app.route("/math/perimetro", methods=["GET", "POST"])
def math_perimeter():
    result = None
    error = None
    shape = None
    if request.method == "POST":
        try:
            shape = request.form.get("shape", "")
            params = PERIMETER_FORMULAS[shape]["params"]
            kwargs = {p: float(request.form.get(p, "")) for p in params}
            result = calculate_perimeter(shape, **kwargs)
        except KeyError:
            error = "Selecione uma forma geométrica."
        except ValueError:
            error = "Insira valores numéricos válidos."
    return render_template("math/perimetro.html", formulas=PERIMETER_FORMULAS, result=result, error=error, shape=shape)


@app.route("/math/quiz")
def math_quiz():
    return render_template("math/quiz.html")


# ── PORTUGUESE ────────────────────────────────────────────────────────────────

@app.route("/portugues")
def portugues_index():
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    return render_template("portuguese/index.html", data=data)


@app.route("/portugues/interpretacao")
def portugues_interpretacao():
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    return render_template("portuguese/interpretacao.html", textos=data["interpretacao"])


@app.route("/portugues/interpretacao/<int:text_id>")
def portugues_interpretacao_text(text_id):
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    texto = next((t for t in data["interpretacao"] if t["id"] == text_id), None)
    if not texto:
        return render_template("404.html"), 404
    return render_template("portuguese/texto.html", texto=texto)


@app.route("/portugues/redacao")
def portugues_redacao():
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    return render_template("portuguese/redacao.html", redacao=data["redacao"])


@app.route("/portugues/gramatica")
def portugues_gramatica():
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    return render_template("portuguese/gramatica.html", gramatica=data["redacao"]["gramatica"])


@app.route("/portugues/conceitos")
def portugues_conceitos():
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    return render_template("portuguese/conceitos.html", conceitos=data["conceitos"])


@app.route("/portugues/conceitos/<conceito_id>")
def portugues_conceito(conceito_id):
    data = load_json(os.path.join(DATA_DIR, "portuguese", "content.json"))
    conceitos = data["conceitos"]
    conceito = next((c for c in conceitos if c["id"] == conceito_id), None)
    if not conceito:
        return render_template("404.html"), 404
    idx = next(i for i, c in enumerate(conceitos) if c["id"] == conceito_id)
    prev_c = conceitos[idx - 1] if idx > 0 else None
    next_c = conceitos[idx + 1] if idx < len(conceitos) - 1 else None
    return render_template("portuguese/conceito.html", conceito=conceito, prev_c=prev_c, next_c=next_c)


# ── ENGLISH ───────────────────────────────────────────────────────────────────

@app.route("/ingles")
def ingles_index():
    data = load_json(os.path.join(DATA_DIR, "english", "content.json"))
    return render_template("english/index.html", levels=data["levels"])


@app.route("/ingles/<level_id>")
def ingles_level(level_id):
    data = load_json(os.path.join(DATA_DIR, "english", "content.json"))
    level = next((l for l in data["levels"] if l["id"] == level_id.upper()), None)
    if not level:
        return render_template("404.html"), 404
    return render_template("english/level.html", level=level)


@app.route("/ingles/<level_id>/<topic_id>")
def ingles_topic(level_id, topic_id):
    data = load_json(os.path.join(DATA_DIR, "english", "content.json"))
    level = next((l for l in data["levels"] if l["id"] == level_id.upper()), None)
    if not level:
        return render_template("404.html"), 404
    topic = next((t for t in level["topics"] if t["id"] == topic_id), None)
    if not topic:
        return render_template("404.html"), 404
    return render_template("english/topic.html", level=level, topic=topic)


@app.route("/ingles/vocabulario/<level_id>")
def ingles_vocab(level_id):
    data = load_json(os.path.join(DATA_DIR, "english", "content.json"))
    vocab = data["vocabulary"].get(level_id.upper(), [])
    level = next((l for l in data["levels"] if l["id"] == level_id.upper()), None)
    return render_template("english/vocabulary.html", vocab=vocab, level=level, level_id=level_id.upper())


# ── PYTHON ────────────────────────────────────────────────────────────────────

@app.route("/python")
def python_index():
    data = load_json(os.path.join(DATA_DIR, "python", "content.json"))
    return render_template("python/index.html", levels=data["levels"])


@app.route("/python/<level_id>")
def python_level(level_id):
    data = load_json(os.path.join(DATA_DIR, "python", "content.json"))
    level = next((l for l in data["levels"] if l["id"] == level_id), None)
    if not level:
        return render_template("404.html"), 404
    return render_template("python/level.html", level=level)


@app.route("/python/<level_id>/<topic_id>")
def python_topic(level_id, topic_id):
    data = load_json(os.path.join(DATA_DIR, "python", "content.json"))
    level = next((l for l in data["levels"] if l["id"] == level_id), None)
    if not level:
        return render_template("404.html"), 404
    topic = next((t for t in level["topics"] if t["id"] == topic_id), None)
    if not topic:
        return render_template("404.html"), 404
    all_topics = level["topics"]
    topic_index = next(i for i, t in enumerate(all_topics) if t["id"] == topic_id)
    prev_topic = all_topics[topic_index - 1] if topic_index > 0 else None
    next_topic = all_topics[topic_index + 1] if topic_index < len(all_topics) - 1 else None
    return render_template("python/topic.html", level=level, topic=topic,
                           prev_topic=prev_topic, next_topic=next_topic)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
