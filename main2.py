import math
import requests
from xml.etree import ElementTree

# --- Функции для интегрирования ---
def func1(x):
    if x == 0:
        raise ZeroDivisionError("Особенность в 0")
    return 1 / math.sqrt(abs(x))

def func2(x):
    if x == 2:
        raise ZeroDivisionError("Особенность в 2")
    return 1 / (x - 2)

def func3(x):
    if x == 1:
        raise ZeroDivisionError("Особенность в 1")
    return 1 / ((x - 1) ** 2)

functions = {
    1: ("1 / sqrt(abs(x))", func1, [0.0]),
    2: ("1 / (x - 2)", func2, [2.0]),
    3: ("1 / (x - 1)^2", func3, [1.0]),
}

# --- Метод трапеций ---
def trapezoid_rule(func, a, b, n):
    h = (b - a) / n
    result = 0.0
    for i in range(n):
        x0 = a + i * h
        x1 = a + (i + 1) * h
        try:
            f0 = func(x0)
            f1 = func(x1)
            result += 0.5 * (f0 + f1) * h
        except ZeroDivisionError:
            continue  # Пропускаем разрыв
    return result

# --- Проверка сходимости по изменению значений ---
def is_convergent_split(f, a, b, breakpoints, test_integrate=None):
    epsilons = [1e-3, 1e-5, 1e-7]

    for point in breakpoints:
        if abs(point - a) < 1e-8:
            print(f"Особенность на левой границе: x = {point}")
            values = []
            for eps in epsilons:
                try:
                    val = test_integrate(f, a + eps, b, 10000)
                    values.append(val)
                except:
                    return False
            if max(values) - min(values) > 10:
                print("Резкий рост интеграла при уменьшении eps — расходимость.")
                return False

        elif abs(point - b) < 1e-8:
            print(f"Особенность на правой границе: x = {point}")
            values = []
            for eps in epsilons:
                try:
                    val = test_integrate(f, a, b - eps, 10000)
                    values.append(val)
                except:
                    return False
            if max(values) - min(values) > 10:
                print("Резкий рост интеграла при уменьшении eps — расходимость.")
                return False

        elif a < point < b:
            print(f"Особенность внутри интервала: x = {point}")
            left_vals, right_vals = [], []
            for eps in epsilons:
                try:
                    left = test_integrate(f, a, point - eps, 10000)
                    right = test_integrate(f, point + eps, b, 10000)
                    left_vals.append(left)
                    right_vals.append(right)
                except:
                    return False
            if max(left_vals) - min(left_vals) > 10 or max(right_vals) - min(right_vals) > 10:
                print("Односторонние значения нестабильны — расходимость.")
                return False

    return True

# --- Адаптивное интегрирование с правилом Рунге ---
def adaptive_integrate(f, a, b, epsilon, method=trapezoid_rule, runge_order=2):
    n = 4
    result_prev = method(f, a, b, n)
    while True:
        n *= 2
        result_new = method(f, a, b, n)
        error = abs(result_new - result_prev) / (2 ** runge_order - 1)
        if error < epsilon:
            return result_new, n, error
        result_prev = result_new

# --- Ввод ---
def select_function():
    print("Выберите функцию:")
    for i, (name, _, _) in functions.items():
        print(f"{i}. {name}")
    while True:
        try:
            f_choice = int(input("Введите номер функции: "))
            if f_choice in functions:
                return f_choice, functions[f_choice][1], functions[f_choice][0]
        except:
            pass
        print("Неверный ввод. Попробуйте снова.\n")

def read_bounds():
    while True:
        try:
            a = float(input("Введите нижний предел интегрирования a: "))
            b = float(input("Введите верхний предел интегрирования b: "))
            if a < b:
                return a, b
            print("Ошибка: a должно быть меньше b.")
        except:
            print("Ошибка ввода. Повторите.\n")

# --- Проверка особенностей и обработка ---
def check_and_handle_discontinuities(f, a, b, breakpoints):
    if breakpoints:
        print(f"Обнаружены особые точки: {breakpoints}")
        if not is_convergent_split(f, a, b, breakpoints, test_integrate=trapezoid_rule):
            print("Интеграл не существует (расходится).")
            return None, None
        print("Интеграл является несобственным, но сходится.")
        if any(abs(bp - a) < 1e-8 for bp in breakpoints):
            a += 1e-6
        if any(abs(bp - b) < 1e-8 for bp in breakpoints):
            b -= 1e-6
    return a, b

# --- Получение результата Wolfram Alpha ---
def get_true_integral_wolfram(func_expr, a, b, app_id, singularities=None):
    if singularities is None:
        singularities = []

    if not singularities:
        query = f"integrate {func_expr} from {a} to {b}"
    else:
        # Разбить на интервалы
        points = [a] + singularities + [b]
        subqueries = [
            f"integrate {func_expr} from {points[i]} to {points[i+1]}"
            for i in range(len(points) - 1)
        ]
        query = " + ".join(subqueries)

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


def find_singularities(func, a, b, steps=1_000_000, delta=1e-3):
    h = (b - a) / steps
    points = set()

    for i in range(steps + 1):
        x = a + i * h
        try:
            y = func(x)
            if not math.isfinite(y):
                points.add(round(x, 2))
        except Exception:
            points.add(round(x, 2))
            continue

        if i > 0:
            prev_x = a + (i - 1) * h
            try:
                y_prev = func(prev_x)
                if math.isfinite(y_prev) and abs(y - y_prev) > 1e6:
                    mid = (x + prev_x) / 2
                    points.add(round(mid, 2))
            except Exception:
                mid = (x + prev_x) / 2
                points.add(round(mid, 2))

    # 🔍 Проверка "подозрительных" целых чисел в пределах [a, b]
    for x in range(math.floor(a), math.ceil(b) + 1):
        if a <= x <= b:
            try:
                y = func(x)
                if not math.isfinite(y):
                    points.add(round(x, 2))
            except Exception:
                points.add(round(x, 2))

    # Убираем почти дубликаты
    cleaned = []
    for x in sorted(points):
        if not cleaned or abs(x - cleaned[-1]) > delta:
            cleaned.append(x)
    return cleaned



# --- Главная функция ---
def run_main():
    f_choice, f, func_str = select_function()
    a, b = read_bounds()
    breakpoints = find_singularities(f, a, b)

    epsilon = float(input("Введите требуемую точность ε: "))

    a_adj, b_adj = check_and_handle_discontinuities(f, a, b, breakpoints)
    if a_adj is not None:
        result, n, error = adaptive_integrate(f, a_adj, b_adj, epsilon)
        print(f"\nИнтегрирование выполнено на интервале [{a_adj}, {b_adj}]")
        print(f"Значение интеграла ≈ {result:.6f}")
        print(f"Число разбиений: {n}")
        print(f"Оценка погрешности: {error:.2e}")

    wa = get_true_integral_wolfram(func_str, a, b, "UYKK3A-RH973TYRV2", breakpoints)
    print(f"Истиное значение (Wolfram Alpha): {wa}")

# --- Запуск ---
if __name__ == "__main__":
    run_main()