import os

# Caminho da Área de Trabalho do usuário
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
base_path = os.path.join(desktop, "gerenciar_faturas")

# Lista das pastas a serem criadas
folders = [
    "src",
    "src/database",
    "src/core",
    "src/utils",
    "src/app",
    "tests",
    "assets",
    "assets/icons",
    "docs",
    "config"
]

# Criação das pastas
for folder in folders:
    path = os.path.join(base_path, folder)
    os.makedirs(path, exist_ok=True)

print(f"Pastas criadas com sucesso em: {base_path}")