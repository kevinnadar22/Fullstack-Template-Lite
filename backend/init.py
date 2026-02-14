import os
import subprocess

folders = [
    "app/utils",
    "app/repository",
    "app/models",
    "app/enums",
    "app/schemas",
    "app/utils",
    "app/service",
    "app/workers",
]
for folder in folders:
    if not os.path.exists(folder):
        continue
    subprocess.run(["mkinit", folder, "-w", "--recursive", "--relative", "--nomods"])


subprocess.run(["ruff", "format", "."])
