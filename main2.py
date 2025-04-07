import math

# --- Функции для интегрирования ---
def func1(x): return 1 / math.sqrt(x)            # особенность в точке a=0
def func2(x): return 1 / (x - 2)                  # особенность в точке x=2
def func3(x): return 1 / ((x - 1)**2)             # особенность в точке x=1

functions = {
    1: ("1 / sqrt(x)", func1),
    2: ("1 / (x - 2)", func2),
    3: ("1 / (x - 1)^2", func3),
}

# --- Метод трапеций ---
def trapezoid_rule(func, a, b, n):
    h = (b - a) / n
    result = 0.5 * (func(a) + func(b))
    for i in range(1, n):
        result += func(a + i * h)
    return result * h

# --- Поиск особенностей ---
def get_discontinuity_points(func, a, b, n=1_000_000):
    breakpoints = set()
    h = (b - a) / n

    # Основная сетка
    for i in range(n + 1):
        x = a + i * h
        try:
            y = func(x)
            if not math.isfinite(y):
                breakpoints.add(round(x, 6))
        except (ZeroDivisionError, OverflowError, ValueError):
            breakpoints.add(round(x, 6))


    return sorted(breakpoints)


def is_convergent_split(f, a, b, eps=1e-6, test_integrate=None):
    breakpoints = get_discontinuity_points(f, a, b)
    for point in breakpoints:
        epsilons = [1e-4, 1e-6, 1e-8]
        if abs(point - a) < eps:
            print(f"Особенность на левой границе: x = {point}")
            results = []
            for e in epsilons:
                try:
                    val = test_integrate(f, a + e, b, 10000)
                    results.append(val)
                except:
                    return False
            if not all(map(math.isfinite, results)) or max(results) - min(results) > 1e3:
                print("Правосторонний интеграл не стабилен — расходимость.")
                return False

        elif abs(point - b) < eps:
            print(f"Особенность на правой границе: x = {point}")
            results = []
            for e in epsilons:
                try:
                    val = test_integrate(f, a, b - e, 10000)
                    results.append(val)
                except:
                    return False
            if not all(map(math.isfinite, results)) or max(results) - min(results) > 1e3:
                print("Левосторонний интеграл не стабилен — расходимость.")
                return False

        elif a < point < b:
            print(f"Особенность внутри интервала: x = {point}")
            left_results = []
            right_results = []
            for e in epsilons:
                try:
                    left = test_integrate(f, a, point - e, 10000)
                    right = test_integrate(f, point + e, b, 10000)
                    left_results.append(left)
                    right_results.append(right)
                except:
                    return False
            if not all(map(math.isfinite, left_results + right_results)):
                return False
            if (max(left_results) - min(left_results) > 1e3 or
                max(right_results) - min(right_results) > 1e3):
                print("Односторонние интегралы не стабилизируются — расходимость.")
                return False

    return True


# --- Адаптивное интегрирование ---
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

# --- Выбор функции ---
def select_function():
    print("Выберите функцию:")
    for i, (name, _) in functions.items():
        print(f"{i}. {name}")
    while True:
        try:
            f_choice = int(input("Введите номер функции: "))
            if f_choice in functions:
                return f_choice, functions[f_choice][1]
        except:
            pass
        print("Неверный ввод. Попробуйте снова.\\n")

# --- Ввод границ ---
def read_bounds():
    while True:
        try:
            a = float(input("Введите нижний предел интегрирования a: "))
            b = float(input("Введите верхний предел интегрирования b: "))
            if a < b:
                return a, b
            else:
                print("Ошибка: a должно быть меньше b.")
        except:
            print("Ошибка ввода. Повторите.\\n")

# --- Проверка особенностей и обработка ---
def check_and_handle_discontinuities(f, a, b, eps=1e-5):
    breakpoints = get_discontinuity_points(f, a, b)

    if breakpoints:
        print(f"Обнаружены особые точки: {breakpoints}")
        if not is_convergent_split(f, a, b, eps=eps, test_integrate=trapezoid_rule):
            print("Интеграл не существует (расходится).")
            return None, None
        print("Интеграл является несобственным, но сходится.")
        if any(abs(bp - a) < eps for bp in breakpoints):
            a += eps
        if any(abs(bp - b) < eps for bp in breakpoints):
            b -= eps
    return a, b


# --- Главный запуск ---
def run_main():
    f_choice, f = select_function()
    a, b = read_bounds()
    epsilon = float(input("Введите требуемую точность ε: "))
    a_adj, b_adj = check_and_handle_discontinuities(f, a, b)
    if a_adj is None:
        return
    result, n, error = adaptive_integrate(f, a_adj, b_adj, epsilon)
    print(f"\nИнтегрирование выполнено на интервале [{a_adj}, {b_adj}]")
    print(f"Значение интеграла ≈ {result:.6f}")
    print(f"Число разбиений: {n}")
    print(f"Оценка погрешности: {error:.2e}")

# --- Точка входа ---
if __name__ == "__main__":
    run_main()