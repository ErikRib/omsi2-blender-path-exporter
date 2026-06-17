import math
from fractions import Fraction


def weighted_average(values, weights):
    if len(values) != len(weights):
        raise ValueError("Quantidade de valores e pesos deve ser igual.")
    if any(w < 0 for w in weights):
        raise ValueError("Pesos não podem ser negativos.")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("A soma dos pesos não pode ser zero.")
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    result = weighted_sum / total_weight
    steps = []
    for i, (v, w) in enumerate(zip(values, weights)):
        steps.append(f"Nota {i+1}: {v} × {w} = {v * w}")
    steps.append(f"Soma ponderada: {weighted_sum}")
    steps.append(f"Soma dos pesos: {total_weight}")
    steps.append(f"Média ponderada = {weighted_sum} ÷ {total_weight} = {result:.2f}")
    return {"result": round(result, 2), "steps": steps}


def factorial(n):
    if n < 0:
        raise ValueError("Fatorial não está definido para números negativos.")
    if not isinstance(n, int):
        raise ValueError("Fatorial só é definido para inteiros.")
    if n > 20:
        raise ValueError("Número muito grande (máximo: 20).")
    result = math.factorial(n)
    if n <= 1:
        steps = [f"{n}! = 1"]
    else:
        sequence = " × ".join(str(i) for i in range(n, 0, -1))
        steps = [f"{n}! = {sequence} = {result}"]
    return {"result": result, "steps": steps}


def solve_first_degree(a, b):
    """ax + b = 0  →  x = -b/a"""
    if a == 0:
        if b == 0:
            return {"result": "Infinitas soluções", "steps": ["0 = 0 → equação identidade"]}
        return {"result": "Sem solução", "steps": [f"{b} = 0 → impossível"]}
    x = -b / a
    steps = [
        f"Equação: {a}x + {b} = 0",
        f"Isolando x: {a}x = {-b}",
        f"x = {-b} ÷ {a}",
        f"x = {x:.4f}".rstrip("0").rstrip("."),
    ]
    return {"result": round(x, 6), "steps": steps}


def solve_second_degree(a, b, c):
    """ax² + bx + c = 0 (Bhaskara)"""
    if a == 0:
        return solve_first_degree(b, c)
    discriminant = b**2 - 4 * a * c
    steps = [
        f"Equação: {a}x² + {b}x + {c} = 0",
        f"Δ = b² - 4ac = {b}² - 4×{a}×{c}",
        f"Δ = {b**2} - {4*a*c} = {discriminant}",
    ]
    if discriminant < 0:
        steps.append("Δ < 0 → sem raízes reais")
        return {"result": "Sem raízes reais", "discriminant": discriminant, "steps": steps}
    sqrt_d = math.sqrt(discriminant)
    x1 = (-b + sqrt_d) / (2 * a)
    x2 = (-b - sqrt_d) / (2 * a)
    steps += [
        f"√Δ = √{discriminant} ≈ {sqrt_d:.4f}",
        f"x₁ = (-{b} + {sqrt_d:.4f}) / (2×{a}) = {x1:.4f}",
        f"x₂ = (-{b} - {sqrt_d:.4f}) / (2×{a}) = {x2:.4f}",
    ]
    if discriminant == 0:
        steps.append("Δ = 0 → raiz dupla")
        return {"result": round(x1, 6), "discriminant": discriminant, "steps": steps, "roots": 1}
    return {
        "x1": round(x1, 6),
        "x2": round(x2, 6),
        "discriminant": discriminant,
        "steps": steps,
        "roots": 2,
    }


AREA_FORMULAS = {
    "circulo": {"formula": "π × r²", "params": ["raio"]},
    "quadrado": {"formula": "l²", "params": ["lado"]},
    "retangulo": {"formula": "b × h", "params": ["base", "altura"]},
    "triangulo": {"formula": "(b × h) / 2", "params": ["base", "altura"]},
    "trapezio": {"formula": "((B + b) × h) / 2", "params": ["base_maior", "base_menor", "altura"]},
    "losango": {"formula": "(D × d) / 2", "params": ["diagonal_maior", "diagonal_menor"]},
}

VOLUME_FORMULAS = {
    "cubo": {"formula": "a³", "params": ["aresta"]},
    "paralelepipedo": {"formula": "c × l × a", "params": ["comprimento", "largura", "altura"]},
    "esfera": {"formula": "(4/3) × π × r³", "params": ["raio"]},
    "cilindro": {"formula": "π × r² × h", "params": ["raio", "altura"]},
    "cone": {"formula": "(π × r² × h) / 3", "params": ["raio", "altura"]},
    "piramide": {"formula": "(A_base × h) / 3", "params": ["area_base", "altura"]},
}

PERIMETER_FORMULAS = {
    "circulo": {"formula": "2 × π × r", "params": ["raio"]},
    "quadrado": {"formula": "4 × l", "params": ["lado"]},
    "retangulo": {"formula": "2 × (b + h)", "params": ["base", "altura"]},
    "triangulo": {"formula": "a + b + c", "params": ["lado_a", "lado_b", "lado_c"]},
    "trapezio": {"formula": "B + b + c + d", "params": ["base_maior", "base_menor", "lado_c", "lado_d"]},
    "losango": {"formula": "4 × l", "params": ["lado"]},
}


def calculate_area(shape, **kwargs):
    if shape == "circulo":
        r = kwargs["raio"]
        result = math.pi * r**2
        steps = [f"A = π × r²", f"A = π × {r}²", f"A = π × {r**2}", f"A ≈ {result:.4f}"]
    elif shape == "quadrado":
        l = kwargs["lado"]
        result = l**2
        steps = [f"A = l²", f"A = {l}²", f"A = {result}"]
    elif shape == "retangulo":
        b, h = kwargs["base"], kwargs["altura"]
        result = b * h
        steps = [f"A = b × h", f"A = {b} × {h}", f"A = {result}"]
    elif shape == "triangulo":
        b, h = kwargs["base"], kwargs["altura"]
        result = (b * h) / 2
        steps = [f"A = (b × h) / 2", f"A = ({b} × {h}) / 2", f"A = {b*h} / 2", f"A = {result}"]
    elif shape == "trapezio":
        B, b, h = kwargs["base_maior"], kwargs["base_menor"], kwargs["altura"]
        result = ((B + b) * h) / 2
        steps = [f"A = ((B + b) × h) / 2", f"A = (({B} + {b}) × {h}) / 2", f"A = {(B+b)*h} / 2", f"A = {result}"]
    elif shape == "losango":
        D, d = kwargs["diagonal_maior"], kwargs["diagonal_menor"]
        result = (D * d) / 2
        steps = [f"A = (D × d) / 2", f"A = ({D} × {d}) / 2", f"A = {D*d} / 2", f"A = {result}"]
    else:
        raise ValueError(f"Forma '{shape}' não reconhecida.")
    return {"result": round(result, 4), "steps": steps}


def calculate_volume(shape, **kwargs):
    if shape == "cubo":
        a = kwargs["aresta"]
        result = a**3
        steps = [f"V = a³", f"V = {a}³", f"V = {result}"]
    elif shape == "paralelepipedo":
        c, l, a = kwargs["comprimento"], kwargs["largura"], kwargs["altura"]
        result = c * l * a
        steps = [f"V = c × l × a", f"V = {c} × {l} × {a}", f"V = {result}"]
    elif shape == "esfera":
        r = kwargs["raio"]
        result = (4 / 3) * math.pi * r**3
        steps = [f"V = (4/3) × π × r³", f"V = (4/3) × π × {r}³", f"V ≈ {result:.4f}"]
    elif shape == "cilindro":
        r, h = kwargs["raio"], kwargs["altura"]
        result = math.pi * r**2 * h
        steps = [f"V = π × r² × h", f"V = π × {r}² × {h}", f"V ≈ {result:.4f}"]
    elif shape == "cone":
        r, h = kwargs["raio"], kwargs["altura"]
        result = (math.pi * r**2 * h) / 3
        steps = [f"V = (π × r² × h) / 3", f"V = (π × {r}² × {h}) / 3", f"V ≈ {result:.4f}"]
    elif shape == "piramide":
        ab, h = kwargs["area_base"], kwargs["altura"]
        result = (ab * h) / 3
        steps = [f"V = (A_base × h) / 3", f"V = ({ab} × {h}) / 3", f"V = {result:.4f}"]
    else:
        raise ValueError(f"Sólido '{shape}' não reconhecido.")
    return {"result": round(result, 4), "steps": steps}


def calculate_perimeter(shape, **kwargs):
    if shape == "circulo":
        r = kwargs["raio"]
        result = 2 * math.pi * r
        steps = [f"P = 2 × π × r", f"P = 2 × π × {r}", f"P ≈ {result:.4f}"]
    elif shape == "quadrado":
        l = kwargs["lado"]
        result = 4 * l
        steps = [f"P = 4 × l", f"P = 4 × {l}", f"P = {result}"]
    elif shape == "retangulo":
        b, h = kwargs["base"], kwargs["altura"]
        result = 2 * (b + h)
        steps = [f"P = 2 × (b + h)", f"P = 2 × ({b} + {h})", f"P = 2 × {b+h}", f"P = {result}"]
    elif shape == "triangulo":
        a, b, c = kwargs["lado_a"], kwargs["lado_b"], kwargs["lado_c"]
        result = a + b + c
        steps = [f"P = a + b + c", f"P = {a} + {b} + {c}", f"P = {result}"]
    elif shape == "trapezio":
        B, b, c, d = kwargs["base_maior"], kwargs["base_menor"], kwargs["lado_c"], kwargs["lado_d"]
        result = B + b + c + d
        steps = [f"P = B + b + c + d", f"P = {B} + {b} + {c} + {d}", f"P = {result}"]
    elif shape == "losango":
        l = kwargs["lado"]
        result = 4 * l
        steps = [f"P = 4 × l", f"P = 4 × {l}", f"P = {result}"]
    else:
        raise ValueError(f"Forma '{shape}' não reconhecida.")
    return {"result": round(result, 4), "steps": steps}
