import os
import sys
import glob
import re
import subprocess
import shutil

BABELON_DIR = "babelon"
TMP_DIR = "tmp"

def get_languages():
    files = glob.glob(os.path.join(BABELON_DIR, "hp-*.babelon.tsv"))
    languages = []
    for f in files:
        m = re.search(r"hp-([^.]+)\.babelon\.tsv", os.path.basename(f))
        if m:
            languages.append(m.group(1))
    return sorted(list(set(languages)))

def sort_translation(lang):
    print(f"Sorting translation files for: {lang}")
    os.makedirs(TMP_DIR, exist_ok=True)
    
    synonyms_path = os.path.join(BABELON_DIR, f"hp-{lang}.synonyms.tsv")
    babelon_path = os.path.join(BABELON_DIR, f"hp-{lang}.babelon.tsv")
    
    if os.path.exists(synonyms_path):
        with open(synonyms_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 2:
            header = lines[:2]
            data = lines[2:]
            data.sort()
            with open(synonyms_path, "w", encoding="utf-8", newline="") as f:
                f.writelines(header + data)
                
    if os.path.exists(babelon_path):
        with open(babelon_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 1:
            header = lines[:1]
            data = lines[1:]
            data.sort()
            with open(babelon_path, "w", encoding="utf-8", newline="") as f:
                f.writelines(header + data)

def clean_translation(lang):
    print(f"Cleaning whitespace in translation files for: {lang}")
    for suffix in ["babelon.tsv", "synonyms.tsv"]:
        path = os.path.join(BABELON_DIR, f"hp-{lang}.{suffix}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace '\t ' with '\t' and ' \t' with '\t'
            cleaned = re.sub(r"\t[ ]+", "\t", content)
            cleaned = re.sub(r"[ ]+\t", "\t", cleaned)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(cleaned)

def validate_translation(lang):
    print(f"Validating translation files for: {lang}")
    os.makedirs(TMP_DIR, exist_ok=True)
    
    synonyms_path = os.path.join(BABELON_DIR, f"hp-{lang}.synonyms.tsv")
    babelon_path = os.path.join(BABELON_DIR, f"hp-{lang}.babelon.tsv")
    
    # Run tsvalid
    for path in [synonyms_path, babelon_path]:
        if os.path.exists(path) and os.path.getsize(path) > 200: # skip empty/stub files
            cmd = ["tsvalid", path, "--skip", "W1"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            # check for errors E[0-9]+:
            if re.search(r"E[0-9]+:[ ]", res.stdout) or re.search(r"E[0-9]+:[ ]", res.stderr):
                print(f"Error detected in {path}:\n{res.stdout}\n{res.stderr}")
                sys.exit(1)
                
    # Run babelon convert
    if os.path.exists(babelon_path) and os.path.getsize(babelon_path) > 200:
        cmd = ["babelon", "convert", babelon_path, "--output-format", "owl", "-o", os.path.join(TMP_DIR, f"{lang}-babelon.owl")]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Babelon convert failed for {lang}:\n{res.stderr}")
            sys.exit(1)

    # Run robot template if robot is available
    if shutil.which("robot") and os.path.exists(synonyms_path) and os.path.getsize(synonyms_path) > 200:
        cmd = [
            "robot", "template", 
            "--prefix", "dcterms: http://purl.org/dc/terms/", 
            "--template", synonyms_path, 
            "--output", os.path.join(TMP_DIR, f"{lang}-synonyms.owl")
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Robot template failed for {lang}:\n{res.stderr}")
            sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_translations.py <action> [lang]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "list":
        print(" ".join(get_languages()))
        return
        
    if action == "sort-all":
        for lang in get_languages():
            sort_translation(lang)
    elif action == "clean-all":
        for lang in get_languages():
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
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
