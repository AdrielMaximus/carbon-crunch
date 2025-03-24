import subprocess
import json

def analyze_code(filename, code):
    if filename.endswith(".py"):
        return analyze_python_code(code)
    elif filename.endswith(".js") or filename.endswith(".jsx"):
        return analyze_js_code(code)
    else:
        return {"error": "Formato de arquivo não suportado"}

def analyze_python_code(code):
    with open("temp.py", "w") as f:
        f.write(code)

    pylint_output = subprocess.run(["pylint", "temp.py", "--output-format=json"], capture_output=True, text=True)
    flake8_output = subprocess.run(["flake8", "temp.py"], capture_output=True, text=True)

    # Processar a saída do Pylint e Flake8
    pylint_results = json.loads(pylint_output.stdout) if pylint_output.stdout else []
    flake8_results = flake8_output.stdout.split("\n")

    score = 100 - (len(pylint_results) + len(flake8_results) * 2)  # Fórmula simples para a pontuação
    recommendations = [msg["message"] for msg in pylint_results] + flake8_results

    return {"overall_score": max(score, 0), "recommendations": recommendations[:5]}

def analyze_js_code(code):
    with open("temp.js", "w") as f:
        f.write(code)

    eslint_output = subprocess.run(["eslint", "temp.js", "--format=json"], capture_output=True, text=True)
    
    eslint_results = json.loads(eslint_output.stdout) if eslint_output.stdout else []

    score = 100 - len(eslint_results) * 2
    recommendations = [msg["message"] for msg in eslint_results]

    return {"overall_score": max(score, 0), "recommendations": recommendations[:5]}
