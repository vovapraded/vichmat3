import math
import requests
from xml.etree import ElementTree

# --- Функции для интегрирования ---
def func1(x): return math.sin(x)
def func2(x): return math.exp(-x ** 2)
def func3(x): return x ** 2
def func4(x): return 1 / (1 + x ** 2)
def func5(x): return math.log(x + 1)
def func6(x): return x ** 3 - 3 * x ** 2 + 7 * x - 10

functions = {
    1: ("sin(x)", func1),
    2: ("exp(-x^2)", func2),
    3: ("x^2", func3),
    4: ("1 / (1 + x^2)", func4),
    5: ("ln(x + 1)", func5),
    6: ("x^3 - 3x^2 + 7x - 10", func6)

}

# --- Методы численного интегрирования ---
def rectangle_method(f, a, b, n, variant='left'):
    h = (b - a) / n
    result = 0
    for i in range(n):
        x = a + i * h
        if variant == 'left':
            result += f(x)
        elif variant == 'right':
            result += f(x + h)
        elif variant == 'mid':
            result += f(x + h / 2)
    return result * h

def trapezoid_method(f, a, b, n):
    h = (b - a) / n
    result = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        result += f(a + i * h)
    return result * h

def simpson_method(f, a, b, n):
    if n % 2 == 1:
        n += 1  # Simpson's rule requires even number of intervals
    h = (b - a) / n
    result = f(a) + f(b)
    for i in range(1, n, 2):
        result += 4 * f(a + i * h)
    for i in range(2, n - 1, 2):
        result += 2 * f(a + i * h)
    return result * h / 3

# --- Правило Рунге ---
def runge_rule(I_h, I_2h, p):
    return abs(I_h - I_2h) / (2 ** p - 1)

# --- Основная программа ---
def main():
    print("Выберите функцию:")
    for i, (name, _) in functions.items():
        print(f"{i}. {name}")
    f_choice = int(input("Введите номер функции: "))
    f = functions[f_choice][1]

    a = float(input("Введите нижний предел интегрирования a: "))
    b = float(input("Введите верхний предел интегрирования b: "))
    epsilon = float(input("Введите требуемую точность ε: "))
    method = input("Выберите метод (rectangle, trapezoid, simpson): ")

    if method == 'rectangle':
        variant = input("Выберите вариант (left, right, mid): ")
        integrate = lambda f, a, b, n: rectangle_method(f, a, b, n, variant)
        order = 1 if variant in ('left', 'right') else 2
    elif method == 'trapezoid':
        integrate = trapezoid_method
        order = 2
    elif method == 'simpson':
        integrate = simpson_method
        order = 4
    else:
        print("Неверный метод")
        return

    n = 4
    while True:
        I_n = integrate(f, a, b, n)
        I_2n = integrate(f, a, b, 2 * n)
        error = runge_rule(I_2n, I_n, order)
        if error < epsilon:
            break
        n *= 2

    print(f"\nРезультат:")
    print(f"Значение интеграла ≈ {I_2n}")
    print(f"Число разбиений: {2 * n}")
    print(f"Оценка погрешности: {error}")

    wa = get_true_integral_wolfram(functions[f_choice][0], a, b, "UYKK3A-RH973TYRV2")
    print(f"Истиное значение (Wolfram Alpha): {wa}")
# --- Получение результата Wolfram Alpha ---
def get_true_integral_wolfram(func_expr, a, b, app_id):

    query = f"integrate {func_expr} from {a} to {b}"


    url = "http://api.wolframalpha.com/v2/query"
    params = {
        "input": query,
        "appid": app_id,
        "format": "plaintext",
        "output": "XML"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Wolfram API error: {response.status_code}"

    tree = ElementTree.fromstring(response.content)

    for pod in tree.findall(".//pod"):
        for subpod in pod.findall(".//subpod"):
            text = subpod.findtext("plaintext")
            if text and ("≈" in text or "=" in text):
                return text.strip()

    return "Не удалось найти численный результат в ответе Wolfram Alpha"
if __name__ == "__main__":
    main()
