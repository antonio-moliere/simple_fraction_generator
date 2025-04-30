# Generador de Ejercicios de Fracciones Algebraicas

Aplicación web simple construida con Flask y SymPy para generar ejercicios de operaciones combinadas (+, -, *, /) con fracciones algebraicas.

## Características

*   Genera problemas aleatorios con fracciones.
*   Utiliza SymPy para el manejo simbólico y la simplificación.
*   Muestra el problema y la solución en formato LaTeX (renderizado con MathJax).
*   Interfaz web simple con Flask.
*   Botón para generar nuevos ejercicios.
*   Botón para mostrar/ocultar la solución.

## Requisitos

*   Python 3.7+
*   Conda (o pip y un entorno virtual)

## Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd algebraic_fractions_app
    ```

2.  **Crear y activar el entorno Conda:**
    (Asegúrate de tener Conda instalado)
    ```bash
    # Opcional: Crear un nuevo entorno (si no tienes uno ya)
    # conda create --name fraciones_env python=3.9 -y
    # conda activate fraciones_env

    # Si ya tienes un entorno activado, simplemente instala las dependencias
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    # o
    # conda install --file requirements.txt --yes
    # o
    # conda install flask sympy --yes
    ```

## Ejecución

1.  Asegúrate de que tu entorno Conda esté activado:
    ```bash
    conda create --name simple_fraction_generator
    conda activate simple_fraction_generator
    cd simple_fraction_generator(
    ```
3.  Ejecuta la aplicación Flask:
    ```bash
    python3 app.py
    ```
4.  Abre tu navegador web y ve a `http://127.0.0.1:5000` (o la dirección que indique Flask).

## Estructura del Proyecto
/algebraic_fractions_app
|-- /templates # Plantillas HTML (Jinja2)
|-- /static # Archivos estáticos (CSS, JS, imágenes)
|-- /modules # Módulos Python personalizados (lógica del generador)
|-- app.py # Aplicación principal Flask
|-- requirements.txt # Dependencias Python
|-- README.md # Este archivo
|-- .gitignore # Archivos ignorados por Git


## Posibles Mejoras

*   Añadir niveles de dificultad (controlando grado de polinomios, número de términos, tipos de operaciones).
*   Permitir al usuario introducir su respuesta y validarla.
*   Incluir factorización como parte de los ejercicios o la simplificación.
*   Mejorar la interfaz de usuario.
*   Añadir más variables simbólicas (y, z, a, b...).
*   Desplegar la aplicación en un servicio de hosting (Heroku, PythonAnywhere, etc.).

