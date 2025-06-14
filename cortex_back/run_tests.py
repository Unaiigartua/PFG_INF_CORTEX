import sys
import subprocess
from pathlib import Path
import os

def run_tests():
    """Ejecutar tests con servicios reales"""

    print("Ejecutando tests...")

    if not Path("app").exists():
        print("No se encuentra el directorio 'app'")
        print("Ejecuta este script desde cortex_back/")
        sys.exit(1)

    current_dir = str(Path.cwd())
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir + ':' + env.get('PYTHONPATH', '')

    print(f"Directorio: {current_dir}")

    test_commands = [
        {
            "name": "Test básico de configuración",
            "cmd": ["python", "-m", "pytest", "tests/test_auth.py::test_register_user", "-v", "--tb=short", "-q"],
            "timeout": 30
        },
        {
            "name": "Tests de autenticación completos",
            "cmd": ["python", "-m", "pytest", "tests/test_auth.py", "-v", "--tb=short"],
            "timeout": 60
        },
        {
            "name": "Tests de NER médico",
            "cmd": ["python", "-m", "pytest", "tests/test_medical_ner.py", "-v", "--tb=short"],
            "timeout": 60
        },
        {
            "name": "Tests de similitud médica",
            "cmd": ["python", "-m", "pytest", "tests/test_medical_similarity.py", "-v", "--tb=short"],
            "timeout": 90
        },
        {
            "name": "Tests de generación SQL",
            "cmd": ["python", "-m", "pytest", "tests/test_sql_generation.py", "-v", "--tb=short"],
            "timeout": 60
        },
        {
            "name": "Tests de historial",
            "cmd": ["python", "-m", "pytest", "tests/test_query_history.py", "-v", "--tb=short"],
            "timeout": 60
        },
        {
            "name": "Tests de integración",
            "cmd": ["python", "-m", "pytest", "tests/test_integration_simple.py", "-v", "--tb=short"],
            "timeout": 120
        }
    ]

    results = []

    for i, test_config in enumerate(test_commands, 1):
        print(f"\n{'='*60}")
        print(f"{i}/{len(test_commands)}: {test_config['name']}")
        print(f"{'='*60}")

        try:
            result = subprocess.run(
                test_config['cmd'],
                cwd=current_dir,
                env=env,
                timeout=test_config['timeout']
            )

            status = "EXITOSO" if result.returncode == 0 else "FALLÓ"
            results.append((test_config['name'], status))

            print(f"{test_config['name']}: {status}")

        except subprocess.TimeoutExpired:
            results.append((test_config['name'], "TIMEOUT"))
            print(f"{test_config['name']}: TIMEOUT")
        except Exception as e:
            results.append((test_config['name'], "ERROR"))
            print(f"{test_config['name']}: ERROR - {e}")

    print(f"\n{'='*60}")
    print("RESUMEN FINAL")
    print(f"{'='*60}")

    exitosos = sum(1 for _, status in results if status == "EXITOSO")

    for name, status in results:
        print(f"{name}: {status}")

    print(f"\n{exitosos}/{len(results)} tests exitosos")

    if exitosos == len(results):
        print("Todos los tests pasaron correctamente.")
        sys.exit(0)
    else:
        print("Algunos tests fallaron.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
