from flask import Flask, render_template, url_for
import sys
import os
import random

# --- IMPORTAR EL NUEVO GENERADOR ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))
try:
    # Importa la nueva función
    from simple_fraction_generator import generate_simple_combined_exercise
    generator_imported = True
    generator_error_msg = None
except ImportError as e:
    print(f"ERROR: No se pudo importar el generador: {e}")
    generator_imported = False
    generator_error_msg = str(e)
    # Define una función dummy si la importación falla
    def generate_simple_combined_exercise(*args, **kwargs):
        return {
            "problem_latex": r"\text{Error al importar generador}",
            "solution_latex": r"\text{Revisar consola Flask}",
            "problem_sympy": None,
            "solution_sympy": None
        }

# ------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
    print("--- Accediendo a la ruta / ---")
    exercise_data = None
    if not generator_imported:
         exercise_data = generate_simple_combined_exercise() # Llama a la dummy
         print(f"Error de importación: {generator_error_msg}")
    else:
        try:
            # --- PARÁMETROS PARA FRACCIONES SIMPLES ---
            num_terms = random.randint(3, 5) # 3 a 5 términos
            max_power = 3                    # Exponente máximo

            print(f"Generando ejercicio simple con: num_terms={num_terms}, max_power={max_power}")
            # --- LLAMAR AL NUEVO GENERADOR ---
            exercise_data = generate_simple_combined_exercise(
                num_terms=num_terms,
                max_power=max_power
            )
            # ----------------------------------
            print(f"Datos generados (problema): {exercise_data['problem_latex']}")

        except Exception as e:
            import traceback
            print(f"¡ERROR al generar el ejercicio dentro de la ruta!: {e}")
            print(traceback.format_exc())
            exercise_data = {
                "problem_latex": r"\text{Excepción durante la generación}",
                "solution_latex": f"Error: {e}",
            }

    # Asegurar que exercise_data sea un diccionario válido para la plantilla
    if not isinstance(exercise_data, dict) or 'problem_latex' not in exercise_data:
         print("¡ALERTA! exercise_data no es un diccionario válido o está incompleto.")
         exercise_data = {
             "problem_latex": r"\text{Error interno en generación}",
             "solution_latex": r"\text{Revisar consola Flask}",
         }

    print(f"Renderizando index.html...")
    return render_template('index.html', exercise=exercise_data)

if __name__ == '__main__':
    if not generator_imported:
         print(f"\n!!! ADVERTENCIA: No se pudo importar el generador ({generator_error_msg}). La aplicación mostrará errores. !!!\n")
    # Ejecutar con debug=True para desarrollo
    # ¡NO usar debug=True en producción!
    app.run(debug=True)