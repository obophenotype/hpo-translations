import os
import stat
import uuid
import zipfile
from pathlib import Path


def main() -> None:
    zip_path = Path("all_translations.zip")
    temp_zip_path = Path("tmp") / f"{zip_path.stem}-{uuid.uuid4().hex}{zip_path.suffix}"
    babelon_dir = Path("babelon")

    print(f"Packaging translation files into {zip_path}...")
    temp_zip_path.parent.mkdir(exist_ok=True)

    with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in sorted(babelon_dir.glob("hp-*.*.tsv")):
            print(f"Adding {file.name}")
            zipf.write(file, arcname=file.relative_to(babelon_dir.parent))

    try:
        if zip_path.exists():
            zip_path.chmod(stat.S_IWRITE)
        os.replace(temp_zip_path, zip_path)
        output_path = zip_path
    except PermissionError:
        output_path = temp_zip_path
        print(f"Warning: could not replace locked artifact {zip_path}; wrote fallback artifact instead.")
    print(f"Packaging complete. Created {output_path}")


if __name__ == "__main__":
    main()
