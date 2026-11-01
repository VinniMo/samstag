#!/usr/bin/env python3
"""Stable local commands for Samstag development.

All application commands use a local absolute SQLite path, disable collection on
visits and keep fictional demo data disabled unless a developer explicitly
overrides it outside this launcher.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MIN_PYTHON = (3, 12)
MAX_PYTHON = (3, 13)


def require_python_312() -> None:
    if not (MIN_PYTHON <= sys.version_info[:2] < MAX_PYTHON):
        raise SystemExit(
            f"Python 3.12 requis; interpréteur courant: {sys.version_info.major}.{sys.version_info.minor}. "
            "Utiliser `make setup PYTHON=/chemin/vers/python3.12`."
        )


def read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SystemExit(f"{path}:{number}: ligne .env invalide")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if not key.replace("_", "").isalnum() or not key[0].isalpha():
            raise SystemExit(f"{path}:{number}: nom de variable invalide")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def local_environment() -> dict[str, str]:
    env = os.environ.copy()
    for key, value in read_dotenv(ROOT / ".env").items():
        env.setdefault(key, value)
    defaults = {
        "SAMSTAG_DB": str((ROOT / ".local" / "samstag-dev.sqlite3").resolve()),
        "HOST": "127.0.0.1",
        "PORT": "5000",
        "FLASK_DEBUG": "1",
        "DEMO_ENABLED": "0",
        "COLLECTION_ON_VISIT": "0",
        "SAMSTAG_SESSION_SECRET": "local-development-only",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    for key, value in defaults.items():
        env.setdefault(key, value)

    raw_db = env["SAMSTAG_DB"]
    if raw_db.startswith("/absolute/path/"):
        raise SystemExit("Remplacer le chemin d’exemple SAMSTAG_DB dans .env par un chemin absolu local.")
    database = Path(raw_db).expanduser()
    if not database.is_absolute():
        raise SystemExit("SAMSTAG_DB doit être un chemin absolu local.")
    forbidden = (Path("/var/lib/samstag"), Path("/opt/samstag"))
    if any(database == path or path in database.parents for path in forbidden):
        raise SystemExit("La commande locale refuse un chemin de production connu.")
    database.parent.mkdir(parents=True, exist_ok=True)

    # These safeguards are unconditional for commands launched through this file.
    env["SAMSTAG_DB"] = str(database)
    env["COLLECTION_ON_VISIT"] = "0"
    env["DEMO_ENABLED"] = "0"
    env["HOST"] = "127.0.0.1"
    return env


def run(command: list[str], *, env: dict[str, str] | None = None, cwd: Path = ROOT) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def command_setup() -> None:
    venv = Path(os.environ.get("SAMSTAG_VENV", ".venv"))
    if not venv.is_absolute():
        venv = ROOT / venv
    run([sys.executable, "-m", "venv", str(venv)])
    python = venv / "bin" / "python"
    run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements-dev.lock"])
    pnpm = shutil.which("pnpm")
    if not pnpm:
        raise SystemExit("pnpm est requis pour installer les tests E2E.")
    run([pnpm, "install", "--frozen-lockfile", "--ignore-scripts"], cwd=ROOT / "e2e")
    if os.environ.get("SAMSTAG_SKIP_BROWSER_INSTALL") != "1":
        run([pnpm, "exec", "playwright", "install"], cwd=ROOT / "e2e")
    print(f"Environnement prêt: {venv}")


def command_dev() -> None:
    run([sys.executable, "app.py"], env=local_environment())


def command_test() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], env=local_environment())


def command_e2e(arguments: list[str]) -> None:
    pnpm = shutil.which("pnpm")
    if not pnpm:
        raise SystemExit("pnpm est requis pour les tests E2E.")
    env = local_environment()
    env["SAMSTAG_PYTHON"] = sys.executable
    run([pnpm, "exec", "playwright", "test", *arguments], env=env, cwd=ROOT / "e2e")


def command_check() -> None:
    env = local_environment()
    run([sys.executable, "scripts/validate_data.py"], env=env)
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node.js est requis pour contrôler la syntaxe JavaScript.")
    run([node, "--check", "static/js/main.js"], env=env)
    command_test()


def command_report() -> None:
    run([sys.executable, "collection_cli.py", "report"], env=local_environment())


def main() -> int:
    require_python_312()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "dev", "test", "e2e", "check", "report"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command != "e2e" and args.arguments:
        parser.error("arguments supplémentaires acceptés uniquement pour e2e")
    try:
        {
            "setup": command_setup,
            "dev": command_dev,
            "test": command_test,
            "check": command_check,
            "report": command_report,
        }.get(args.command, lambda: command_e2e(args.arguments))()
    except KeyboardInterrupt:
        print("\nCommande interrompue.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
