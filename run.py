import sys
import os

# Garante que a raiz do projeto está no PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core import gerenciador_faturas

if __name__ == "__main__":
    gerenciador_faturas.main()