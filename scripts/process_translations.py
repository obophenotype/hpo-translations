import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BABELON_DIR = Path("babelon")
TMP_DIR = Path("tmp")
MAKEFILE_SORT_CLEAN_LANGUAGES = ["pt", "de", "fr", "pt", "zh"]


def subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def resolve_python() -> str:
    candidates = [
        Path(os.environ["CONDA_PREFIX"]) / "python.exe" if "CONDA_PREFIX" in os.environ else None,
        Path.cwd() / ".pixi" / "envs" / "default" / "python.exe",
        Path(os.environ["CONDA_PREFIX"]) / "bin" / "python" if "CONDA_PREFIX" in os.environ else None,
        Path.cwd() / ".pixi" / "envs" / "default" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return str(candidate)
    return sys.executable


def resolve_executable(name: str) -> str:
    scripts_dirs = [
        Path(os.environ["CONDA_PREFIX"]) / "Scripts" if "CONDA_PREFIX" in os.environ else None,
        Path.cwd() / ".pixi" / "envs" / "default" / "Scripts",
        Path(sys.executable).parent / "Scripts",
    ]
    for scripts_dir in scripts_dirs:
        if scripts_dir is None:
            continue
        for candidate in (scripts_dir / name, scripts_dir / f"{name}.exe"):
            if candidate.exists():
                return str(candidate)

    executable = shutil.which(name)
    if executable:
        return executable

    raise FileNotFoundError(f"Unable to locate required executable: {name}")


def get_languages() -> list[str]:
    files = glob.glob(str(BABELON_DIR / "hp-*.babelon.tsv"))
    languages = []
    for f in files:
        m = re.search(r"hp-([^.]+)\.babelon\.tsv", os.path.basename(f))
        if m:
            languages.append(m.group(1))
    return sorted(set(languages))


def sort_translation(lang: str) -> None:
    print(f"Sorting translation files for: {lang}")
    TMP_DIR.mkdir(exist_ok=True)

    synonyms_path = BABELON_DIR / f"hp-{lang}.synonyms.tsv"
    babelon_path = BABELON_DIR / f"hp-{lang}.babelon.tsv"

    if synonyms_path.exists():
        with open(synonyms_path, encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 2:
            header = lines[:2]
            data = lines[2:]
            data.sort()
            with open(synonyms_path, "w", encoding="utf-8", newline="") as f:
                f.writelines(header + data)

    if babelon_path.exists():
        with open(babelon_path, encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 1:
            header = lines[:1]
            data = lines[1:]
            data.sort()
            with open(babelon_path, "w", encoding="utf-8", newline="") as f:
                f.writelines(header + data)


def clean_translation(lang: str) -> None:
    print(f"Cleaning whitespace in translation files for: {lang}")
    for suffix in ["babelon.tsv", "synonyms.tsv"]:
        path = BABELON_DIR / f"hp-{lang}.{suffix}"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                content = f.read()
            # Replace '\t ' with '\t' and ' \t' with '\t'
            cleaned = re.sub(r"\t[ ]+", "\t", content)
            cleaned = re.sub(r"[ ]+\t", "\t", cleaned)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(cleaned)


def validate_translation(lang: str) -> None:
    print(f"Validating translation files for: {lang}")
    TMP_DIR.mkdir(exist_ok=True)

    synonyms_path = BABELON_DIR / f"hp-{lang}.synonyms.tsv"
    babelon_path = BABELON_DIR / f"hp-{lang}.babelon.tsv"

    missing_paths = [path for path in [synonyms_path, babelon_path] if not path.exists()]
    if missing_paths:
        missing = ", ".join(str(path) for path in missing_paths)
        raise FileNotFoundError(f"Missing required translation file(s) for {lang}: {missing}")

    # Run tsvalid
    for path in [synonyms_path, babelon_path]:
        # Normalize line endings to LF before running tsvalid to prevent CRLF errors on Windows
        if path.exists():
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            normalized = content.replace("\r\n", "\n")
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(normalized)

        cmd = [resolve_python(), "-m", "tsvalid", str(path), "--skip", "W1", "--encoding", "utf-8"]
        res = subprocess.run(cmd, capture_output=True, text=True, env=subprocess_env())
        # check for errors E[0-9]+:
        if res.returncode != 0 or re.search(r"E[0-9]+:[ ]", res.stdout) or re.search(r"E[0-9]+:[ ]", res.stderr):
            print(f"Error detected in {path}:\n{res.stdout}\n{res.stderr}")
            sys.exit(1)

    # Run LinkML validation
    try:
        import babelon

        schema_path = os.path.join(os.path.dirname(babelon.__file__), "schema", "babelon.yaml")
        if os.path.exists(schema_path):
            print(f"Running LinkML validation on {babelon_path} using schema {schema_path}")
            cmd = [
                resolve_python(),
                "-m",
                "linkml.validator.cli",
                "-s",
                schema_path,
                "-C",
                "translation",
                str(babelon_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, env=subprocess_env())
            if res.returncode != 0:
                print(f"LinkML validation failed for {babelon_path}:\n{res.stdout}\n{res.stderr}")
                sys.exit(1)
        else:
            print(f"Warning: Babelon schema not found at {schema_path}, skipping LinkML validation.")
    except ImportError:
        print("Warning: babelon Python package not found, skipping LinkML validation.")

    # Run babelon convert
    owl_out = TMP_DIR / f"{lang}-babelon.owl"
    cmd = [
        resolve_executable("babelon"),
        "convert",
        str(babelon_path),
        "--output-format",
        "owl",
        "-o",
        str(owl_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=subprocess_env())
    if res.returncode != 0:
        print(f"Babelon convert failed for {lang}:\n{res.stderr}")
        sys.exit(1)

    syn_out = TMP_DIR / f"{lang}-synonyms.owl"
    cmd = [
        resolve_python(),
        "scripts/render_synonyms_owl.py",
        "--template",
        str(synonyms_path),
        "--output",
        str(syn_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=subprocess_env())
    if res.returncode != 0:
        print(f"Synonym OWL rendering failed for {lang}:\n{res.stderr}")
        if owl_out.exists():
            owl_out.unlink()
        sys.exit(1)

    # Clean up generated files to prevent filling up disk space
    if owl_out.exists():
        owl_out.unlink()
    if syn_out.exists():
        syn_out.unlink()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python process_translations.py <action> [lang]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "list":
        print(" ".join(get_languages()))
        return

    if action == "sort-all":
        for lang in MAKEFILE_SORT_CLEAN_LANGUAGES:
            sort_translation(lang)
    elif action == "clean-all":
        for lang in MAKEFILE_SORT_CLEAN_LANGUAGES:
            clean_translation(lang)
    elif action == "validate-all":
        for lang in get_languages():
            validate_translation(lang)
    elif action == "sort":
        if len(sys.argv) < 3:
            print("Language argument missing.")
            sys.exit(1)
        sort_translation(sys.argv[2])
    elif action == "clean":
        if len(sys.argv) < 3:
            print("Language argument missing.")
            sys.exit(1)
        clean_translation(sys.argv[2])
    elif action == "validate":
        if len(sys.argv) < 3:
            print("Language argument missing.")
            sys.exit(1)
        validate_translation(sys.argv[2])
    elif action == "profile":
        import time

        print("Benchmarking validation execution times per translation profile:")
        print("-" * 50)
        print(f"{'Language':<12} | {'Time (s)':<12}")
        print("-" * 50)
        for lang in get_languages():
            start_time = time.perf_counter()
            try:
                validate_translation(lang)
                elapsed = time.perf_counter() - start_time
                print(f"{lang:<12} | {elapsed:<12.4f}")
            except (FileNotFoundError, subprocess.SubprocessError) as error:
                print(f"{lang:<12} | Failed: {error}")
        print("-" * 50)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
