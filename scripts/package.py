from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[1]
    target = root / "dist" / "lambda.zip"
    target.parent.mkdir(exist_ok=True)
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for filename in ["lambda_function.py", "index.html"]:
            archive.write(root / filename, filename)
    print(f"Created {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

