# modules/exercise_generator.py

import random
import sympy
from sympy import Add, Mul, Pow, Rational, Integer, Poly, gcd, symbols, latex

# --- Símbolo(s) ---
x = symbols('x')

# --- Funciones Auxiliares ---

def _generate_polynomial(min_degree=0, max_degree=2, min_coef=-9, max_coef=9, ensure_variable=True, min_terms=1):
    """
    Genera un polinomio con control sobre grado, coeficientes y número de términos.
    """
    if max_degree < min_degree:
        max_degree = min_degree
    degree = random.randint(min_degree, max_degree)

    coeffs = [Integer(0)] * (degree + 1)
    term_indices = list(range(degree + 1))
    random.shuffle(term_indices) # Para elegir términos al azar

    non_zero_coeffs = 0

    # 1. Asegurar coeficiente principal no cero (si degree > 0)
    if degree > 0:
        coeffs[0] = Integer(random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1]))
        non_zero_coeffs += 1
        term_indices.remove(0) # Ya asignamos el coeficiente principal

    # 2. Intentar asegurar min_terms no cero
    terms_to_add = min_terms - non_zero_coeffs
    indices_available = [i for i in term_indices if coeffs[i] == 0] # Indices aún con coef 0
    random.shuffle(indices_available)

    for i in range(min(terms_to_add, len(indices_available))):
        idx = indices_available[i]
        coeffs[idx] = Integer(random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1]))
        non_zero_coeffs += 1
        term_indices.remove(idx)

    # 3. Rellenar el resto de coeficientes aleatoriamente
    for idx in term_indices:
        if coeffs[idx] == 0: # Si no fue forzado antes
            coeffs[idx] = Integer(random.randint(min_coef, max_coef))
            if coeffs[idx] != 0:
                 non_zero_coeffs += 1

    # 4. Asegurar variable si es necesario y posible
    has_variable_term = any(c != 0 for i, c in enumerate(coeffs) if i < degree)
    if ensure_variable and degree > 0 and not has_variable_term and non_zero_coeffs > 0:
        # Si solo hay término constante pero se pidió variable, forzar uno
        non_constant_indices = list(range(degree))
        random.shuffle(non_constant_indices)
        for idx in non_constant_indices:
             if coeffs[idx] == 0:
                 coeffs[idx] = Integer(random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1]))
                 non_zero_coeffs += 1
                 has_variable_term = True
                 break
        # Si todos los términos no constantes eran ya no-cero, no hacemos nada más

    # 5. Construir polinomio y verificar que no sea cero (a menos que degree=0)
    poly = sum(c * x**(degree - i) for i, c in enumerate(coeffs))

    if poly.is_zero and degree > 0:
        # Si accidentalmente todo dio cero, forzar un término no cero
        idx = random.randint(0, degree)
        coeffs[idx] = Integer(random.choice([c for c in range(min_coef, max_coef + 1) if c != 0] or [1]))
        poly = sum(c * x**(degree - i) for i, c in enumerate(coeffs))

    return poly

def _generate_fraction(max_degree_num=2, max_degree_den=2, prevent_trivial_cancel=True):
    """
    Genera una fracción algebraica, intentando evitar cancelación obvia.
    El denominador siempre tendrá la variable 'x'.
    """
    num, den = None, None
    attempts = 0
    max_attempts = 30 # Aumentar intentos si es necesario

    while attempts < max_attempts:
        attempts += 1
        # Generar numerador (puede ser constante)
        num = _generate_polynomial(min_degree=0, max_degree=max_degree_num, min_terms=1, ensure_variable=False)
        # Generar denominador (debe tener variable y no ser constante)
        den = _generate_polynomial(min_degree=1, max_degree=max_degree_den, min_terms=1, ensure_variable=True)

        # Comprobación 1: Denominador válido (no debería ser cero o constante por cómo se genera, pero por si acaso)
        if den.is_zero or den.is_constant():
            # print(f"Advertencia: Denominador inválido generado ({den}), reintentando...")
            continue

        # Comprobación 2: Evitar cancelación trivial si se solicita
        if prevent_trivial_cancel:
            try:
                # Usar as_poly para obtener objetos Poly y calcular gcd
                num_poly = num.as_poly(x)
                den_poly = den.as_poly(x)

                if num_poly is not None and den_poly is not None:
                    common_divisor = gcd(num_poly, den_poly)
                    # Verificar si el gcd (que es un Poly) contiene 'x'
                    if common_divisor is not None and common_divisor.has(x):
                        # print(f"Advertencia: Cancelación trivial detectada (gcd={common_divisor.as_expr()}), reintentando...")
                        continue # Hay factor común con x, no queremos esta fracción
                else:
                    # Si as_poly falla para uno, no podemos comprobar gcd fácilmente
                    # print(f"Advertencia: No se pudo convertir a Poly para verificar gcd ({num}, {den})")
                    pass # Continuar y aceptar la fracción por ahora

            except Exception as e:
                # Capturar otros errores inesperados durante la comprobación de gcd
                print(f"Error inesperado al verificar gcd: {e}")
                pass # Continuar y aceptar la fracción por ahora

        # Si pasó todas las comprobaciones, la fracción es válida
        fraction = num / den
        # print(f"Fracción generada: {fraction}") # Debug
        return fraction

    # Si se superaron los intentos, generar una fracción simple como fallback
    print(f"Advertencia: Se superaron {max_attempts} intentos. Generando fracción simple.")
    num = _generate_polynomial(max_degree=1, ensure_variable=False)
    den = _generate_polynomial(min_degree=1, max_degree=1, ensure_variable=True)
    if den.is_zero or den.is_constant(): # Asegurarse de que el fallback sea válido
        den = x + random.randint(1, 5)
    return num / den

# --- Función Principal ---

def generate_combined_exercise(num_terms=3, max_degree=2, include_integers=True):
    """
    Genera un ejercicio de operaciones combinadas (+, -, *, /) con fracciones
    algebraicas y opcionalmente enteros, adecuado para 15+.
    Devuelve un diccionario con LaTeX para problema y solución (sin delimitadores $).
    """
    if num_terms < 2:
        num_terms = 2 # Necesitamos al menos dos términos

    operations_pool = [Add, Add, Mul, Pow] # Mayor probabilidad de Suma/Resta. Pow -> División

    terms = []
    ops = []

    # 1. Generar los términos (fracciones o enteros)
    for _ in range(num_terms):
        use_integer = include_integers and random.random() < 0.2 # ~20% prob de entero
        if use_integer:
            term = Integer(random.randint(-9, 9))
            # Evitar añadir el entero 0 como término si no es el único término
            if term.is_zero and num_terms > 1:
                term = Integer(random.choice([c for c in range(-9, 9) if c != 0] or [1]))
        else:
            term = _generate_fraction(max_degree_num=max_degree, max_degree_den=max_degree)
        terms.append(term)

    # 2. Generar las operaciones entre términos (num_terms - 1 operaciones)
    for _ in range(num_terms - 1):
        ops.append(random.choice(operations_pool))

    # 3. Construir la expresión SymPy y la representación LaTeX simultáneamente
    exercise_expr = terms[0]
    # Generar LaTeX del primer término (sin $) y añadir paréntesis si es negativo
    term1_latex = latex(terms[0], mode='plain')
    if isinstance(terms[0], (sympy.Number, Mul)) and terms[0].could_extract_minus_sign():
         problem_latex = f"\\left( {term1_latex} \\right)"
    else:
         problem_latex = term1_latex

    # Bucle para añadir el resto de términos y operaciones
    for i in range(num_terms - 1): # Itera desde 0 hasta num_terms - 2
        op_class = ops[i]          # Operación actual
        next_term = terms[i+1]     # Siguiente término a operar
        op_symbol_latex = "?"      # Símbolo LaTeX para la operación

        original_next_term_for_latex = next_term # Guardar antes de modificar por doble negación

        # --- Aplicar operación a la expresión SymPy ---
        if op_class == Add:
            if random.choice([True, False]): # Suma
                exercise_expr += next_term
                op_symbol_latex = "+"
            else: # Resta
                exercise_expr -= next_term
                op_symbol_latex = "-"
                # Simplificación visual de doble negación para LaTeX más adelante
                if next_term.could_extract_minus_sign():
                    op_symbol_latex = "+" # Cambia el símbolo
                    next_term = -next_term # Opera con el término positivo para LaTeX

        elif op_class == Mul:
            exercise_expr *= next_term
            op_symbol_latex = r"\cdot"

        elif op_class == Pow: # División
            # Comprobar si el término a dividir es cero o una fracción con denominador cero
            is_zero_division = False
            if next_term.is_zero:
                is_zero_division = True
            elif isinstance(next_term, (sympy.Rational, sympy.Number)) and not next_term.is_zero:
                 pass # Dividir por número distinto de cero está bien
            elif not isinstance(next_term, Integer): # Si no es entero, puede ser fracción
                num, den = next_term.as_numer_denom()
                if den.is_zero:
                    is_zero_division = True

            if is_zero_division:
                # Acción segura: multiplicar por 1 (o añadir 0 si prefieres)
                print("Advertencia: Se evitó división por cero cambiando a Mul por 1.")
                exercise_expr *= Integer(1)
                op_symbol_latex = r"\cdot"
                next_term = Integer(1) # Para el LaTeX
            else:
                exercise_expr /= next_term
                op_symbol_latex = ":"

        # --- Generar LaTeX para el término actual ---
        term_latex = latex(next_term, mode='plain')

        # --- Determinar si se necesitan paréntesis en LaTeX ---
        needs_paren = False
        # Caso 1: Operando de Mul o Div que es una Suma/Resta explícita
        if (op_class == Mul or op_class == Pow) and isinstance(next_term, Add):
            needs_paren = True
        # Caso 2: Operando negativo (Numérico o Fracción) en Mul, Div o Resta
        elif (op_class == Mul or op_class == Pow or op_symbol_latex == "-") and \
             (isinstance(next_term, (sympy.Number, Mul)) and next_term.could_extract_minus_sign()):
              needs_paren = True

        if needs_paren:
            term_latex = f"\\left( {term_latex} \\right)"

        # --- Añadir a la cadena LaTeX del problema ---
        problem_latex += f" {op_symbol_latex} {term_latex}"

    # 4. Añadir "=" al final del problema LaTeX
    problem_latex += " ="

    # 5. Simplificar la expresión SymPy para obtener la solución
    solution_expr = exercise_expr
    try:
        # Intentar simplificaciones robustas
        solution_expr = sympy.together(solution_expr) # Combinar sobre denominador común
        solution_expr = sympy.cancel(solution_expr)   # Cancelar factores comunes
        # Opcional: solution_expr = sympy.factor(solution_expr)
    except Exception as e:
        print(f"Error durante la simplificación: {e}. Usando expresión parcialmente simplificada.")
        # En caso de error, usar la expresión hasta donde llegó la simplificación

    # 6. Generar LaTeX para la solución (sin $)
    solution_latex = latex(solution_expr, mode='plain')

    # 7. Devolver resultados
    return {
        "problem_latex": problem_latex,
        "solution_latex": solution_latex,
        "problem_sympy": exercise_expr,  # Objeto SymPy original (para posible evaluación)
        "solution_sympy": solution_expr # Objeto SymPy simplificado
    }

# --- Bloque de Prueba ---
if __name__ == "__main__":
    print("Generando ejercicios de mayor dificultad (15+):")
    for i in range(5): # Generar 5 ejemplos
        print(f"\n--- Ejercicio {i+1} ---")
        try:
            # Generar con parámetros aleatorios dentro del rango deseado
            exercise = generate_combined_exercise(
                num_terms=random.randint(3, 4),
                max_degree=random.randint(1, 2),
                include_integers=random.choice([True, False])
            )
            print(f"Problema LaTeX: {exercise['problem_latex']}")
            # Descomentar para ver la expresión SymPy antes de simplificar
            # print(f"Expr Sympy: {exercise['problem_sympy']}")
            print(f"Solución LaTeX: {exercise['solution_latex']}")
            # Descomentar para ver la expresión SymPy simplificada
            # print(f"Sol Sympy: {exercise['solution_sympy']}")

        except Exception as e:
            import traceback
            print("\n!!! ERROR DURANTE LA GENERACIÓN DEL EJERCICIO DE PRUEBA !!!")
            print(traceback.format_exc())

    print("\n--- Prueba con grado potencialmente 3 ---")
    try:
        exercise_deg3 = generate_combined_exercise(num_terms=3, max_degree=3, include_integers=False)
        print(f"Problema LaTeX: {exercise_deg3['problem_latex']}")
        print(f"Solución LaTeX: {exercise_deg3['solution_latex']}")
    except Exception as e:
        import traceback
        print("\n!!! ERROR DURANTE LA GENERACIÓN DEL EJERCICIO DE PRUEBA (Grado 3) !!!")
        print(traceback.format_exc())
