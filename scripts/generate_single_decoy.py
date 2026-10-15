import sys
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
src_dir = project_root / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from honeyguard.decoy_generation.generator import generate_decoy_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_single_decoy.py <filepath> <file_type>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    file_type = sys.argv[2].strip().upper()
    title = filepath.stem.replace("_", " ").title()
    template = {
        "title": title,
        "content": f"HoneyGuard Synthetic Canary Token: {filepath.name}\nDeployed for enterprise ransomware monitoring.\nClassification: Canary Honeytoken\n"
    }

    try:
        generate_decoy_file(filepath, file_type, template)
        
        # Calculate real size and SHA256 checksum on disk
        import hashlib
        size = filepath.stat().st_size
        sha256 = hashlib.sha256(filepath.read_bytes()).hexdigest()
        print(f"METADATA:{size}:{sha256}")
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
