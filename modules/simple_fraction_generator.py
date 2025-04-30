# modules/simple_fraction_generator.py

import random
import sympy
# Importaciones esenciales de SymPy
from sympy import Add, Mul, Pow, Rational, Integer, symbols, latex, simplify

# --- Funciones Auxiliares ---

def _generate_sympy_term(allow_integer=True, max_val=15, avoid_zero=False, avoid_one=False):
    """
    Genera un término numérico: una fracción Rational de SymPy o un Integer.
    Asegura la generación de tipos Integer o Rational de SymPy.
    """
    if allow_integer and random.random() < 0.3: # ~30% probabilidad de ser entero
        val = Integer(random.randint(-max_val, max_val))
        if avoid_zero and val.is_zero:
            val = Integer(random.choice([i for i in range(-max_val, max_val+1) if i != 0] or [1]))
        if avoid_one and abs(val) == 1:
            val = Integer(random.choice([i for i in range(-max_val, max_val+1) if abs(i) > 1 and i != 0] or [2]))
        return val
    else: # Generar fracción
        den = Integer(random.choice([i for i in range(-max_val, max_val + 1) if abs(i) >= 2] or [2]))
        num = Integer(random.randint(-max_val * abs(den)//2, max_val * abs(den)//2))

        if avoid_zero and num.is_zero:
            num = Integer(random.choice([i for i in range(-max_val, max_val+1) if i != 0] or [1]))

        frac = Rational(num, den)

        if avoid_one and abs(frac) == 1:
            return Integer(random.choice([i for i in range(-max_val, max_val+1) if abs(i) > 1 and i != 0] or [2]))

        return frac

# --- Función Principal ---

def generate_simple_combined_exercise(num_terms=10, max_power=3, difficulty_level=1):
    """
    Genera un ejercicio de operaciones combinadas (+, -, *, /, ^) con fracciones numéricas.
    Devuelve un diccionario con LaTeX para problema y solución (sin delimitadores $).
    """
    if num_terms < 2:
        num_terms = 10

    operations_pool = [Add, Add, Add, Mul, Mul, Pow, Pow]

    # 1. Generar lista de términos base
    #    *** MOVIDO AQUÍ ARRIBA PARA QUE EXISTA ANTES DE CUALQUIER USO ***
    terms = [_generate_sympy_term(allow_integer=True) for _ in range(num_terms)]

    # Guarda de seguridad por si la generación falla (muy improbable)
    if not terms:
         return {"problem_latex": "Error: No terms generated", "solution_latex": "", "problem_sympy": None, "solution_sympy": None}

    # Filtrar ceros iniciales si son problemáticos
    if terms[0].is_zero and num_terms > 1:
        terms[0] = _generate_sympy_term(allow_integer=True, avoid_zero=True)
        if terms[0].is_zero: terms[0] = Integer(1) # Doble seguridad

    ops_config = []

    # 2. Generar secuencia de operaciones
    for i in range(num_terms - 1):
        op_type = random.choice(operations_pool)
        exponent = None
        if op_type == Pow:
            if random.random() < 0.6:
                exponent = Integer(-1)
            else:
                exponent = Integer(random.randint(2, max_power))
        ops_config.append({"type": op_type, "exponent": exponent})

    # 3. Construir la expresión SymPy y la representación LaTeX
    exercise_expr = terms[0]
    term1_latex = latex(terms[0], mode='plain')
    if isinstance(terms[0], (Integer, Rational)) and terms[0].is_negative:
         problem_latex = f"\\left( {term1_latex} \\right)"
    else:
         problem_latex = term1_latex

    # Bucle para añadir el resto de términos y operaciones
    for i in range(num_terms - 1):
        op_info = ops_config[i]
        op_class = op_info["type"]
        next_term_orig = terms[i+1]
        next_term_sympy = next_term_orig
        next_term_latex = next_term_orig
        op_symbol_latex = "?"
        exponent_for_latex = None

        # --- Lógica de operación específica ---
        if op_class == Add:
            if random.choice([True, False]): # Suma
                exercise_expr += next_term_sympy
                op_symbol_latex = "+"
            else: # Resta
                exercise_expr -= next_term_sympy
                op_symbol_latex = "-"
                if next_term_sympy.is_negative:
                    op_symbol_latex = "+"
                    next_term_latex = -next_term_sympy

            # === LaTeX para Add/Sub ===
            term_latex = latex(next_term_latex, mode='plain')
            needs_paren = isinstance(next_term_latex, (Integer, Rational)) and next_term_latex.is_negative and op_symbol_latex == "-"
            # Corrección: También añadir paréntesis si se suma un negativo explícitamente
            if op_symbol_latex == "+" and isinstance(next_term_latex, (Integer, Rational)) and next_term_latex.is_negative:
                needs_paren = True
            if needs_paren: term_latex = f"\\left( {term_latex} \\right)"
            problem_latex += f" {op_symbol_latex} {term_latex}"
            # =========================

        elif op_class == Mul:
            if next_term_sympy.is_zero:
                print("Nota: Se reemplazó un 0 en multiplicación por 1.")
                next_term_sympy = Integer(1)
                next_term_latex = Integer(1)
            exercise_expr *= next_term_sympy
            op_symbol_latex = r"\cdot"

            # === LaTeX para Mul ===
            term_latex = latex(next_term_latex, mode='plain')
            needs_paren = isinstance(next_term_latex, (Integer, Rational)) and next_term_latex.is_negative
            if needs_paren: term_latex = f"\\left( {term_latex} \\right)"
            problem_latex += f" {op_symbol_latex} {term_latex}"
            # ======================

        elif op_class == Pow:
            exponent = op_info["exponent"]

            if not isinstance(exponent, Integer): # Fallback
                 print(f"ERROR INTERNO: Exponente no es Integer en bloque Pow: {exponent}")
                 op_symbol_latex = r"\cdot"
                 exercise_expr *= 1
                 next_term_latex = 1
                 # === LaTeX para Fallback Pow ===
                 term_latex = latex(next_term_latex, mode='plain')
                 problem_latex += f" {op_symbol_latex} {term_latex}"
                 # =============================

            elif exponent == -1: # División
                op_symbol_latex = ":"
                if next_term_sympy.is_zero:
                    print("Advertencia: División por cero detectada. Reemplazando divisor por 1.")
                    next_term_sympy = Integer(1)
                    next_term_latex = Integer(1)
                exercise_expr /= next_term_sympy

                # === LaTeX para División ===
                term_latex = latex(next_term_latex, mode='plain')
                needs_paren = isinstance(next_term_latex, (Integer, Rational)) and next_term_latex.is_negative
                if needs_paren: term_latex = f"\\left( {term_latex} \\right)"
                problem_latex += f" {op_symbol_latex} {term_latex}"
                # ==========================

            else: # Potencia (exponent >= 2)
                op_symbol_latex = "^" # Guardamos para lógica, pero no se añade directamente
                exponent_for_latex = exponent
                base_sympy = exercise_expr # Guardar base antes de operar
                try:
                    # Aplicar potencia
                    exercise_expr **= exponent

                    # === LaTeX para Potencia ===
                    # Envolver toda la expresión anterior en paréntesis
                    problem_latex = f"\\left( {problem_latex} \\right)"
                    # Añadir SÓLO el símbolo de potencia y el exponente
                    problem_latex += f"^{{{exponent_for_latex}}}"
                    # ==========================

                except Exception as e:
                    print(f"Error aplicando potencia entera: Base={base_sympy}, Exp={exponent}, Error={e}")
                    # Fallback: añadir multiplicación por 1 (revierte la potencia fallida implícitamente)
                    exercise_expr = base_sympy * 1
                    op_symbol_latex = r"\cdot" # Cambiar símbolo mostrado
                    next_term_latex = 1        # Término a mostrar
                    # === LaTeX para Fallback Potencia ===
                    term_latex = latex(next_term_latex, mode='plain')
                    problem_latex += f" {op_symbol_latex} {term_latex}"
                    # ====================================


    # 4. Añadir "=" al final
    problem_latex += " ="

    # 5. Calcular/Simplificar la expresión SymPy para obtener la solución
    solution_expr = exercise_expr
    try:
        solution_expr = simplify(solution_expr)
    except Exception as e:
        print(f"Error durante la simplificación de la solución: {e}.")
        solution_expr = exercise_expr

    # 6. Generar LaTeX para la solución (sin $)
    solution_latex = latex(solution_expr, mode='plain')

    # 7. Devolver resultados
    return {
        "problem_latex": problem_latex,
        "solution_latex": solution_latex,
        "problem_sympy": exercise_expr,
        "solution_sympy": solution_expr
    }

# --- Bloque de Prueba ---
if __name__ == "__main__":
    print("Generando ejercicios de fracciones numéricas combinadas:")
    for i in range(5): # Generar 5 ejemplos
        print(f"\n--- Ejercicio {i+1} ---")
        try:
            exercise = generate_simple_combined_exercise(
                num_terms=random.randint(3, 5),
                max_power=3
            )
            print(f"Problema LaTeX: {exercise['problem_latex']}")
            print(f"Solución LaTeX: {exercise['solution_latex']}")
        except Exception as e:
            import traceback
            print("\n!!! ERROR DURANTE LA GENERACIÓN DEL EJERCICIO DE PRUEBA !!!")
            print(traceback.format_exc())
