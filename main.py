import argparse
import sys
import os
import subprocess
import shutil
from config import get_config

def compile_latex(project_dir, latex_dir, main_tex):
    print("Compiling LaTeX skeleton...")
    build_dir = os.path.join(project_dir, "build")
    
    # Add MiKTeX to PATH if on Windows and lualatex is not found
    if os.name == 'nt' and not shutil.which("lualatex"):
        miktex_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64")
        if os.path.exists(miktex_path):
            os.environ["PATH"] = miktex_path + os.pathsep + os.environ.get("PATH", "")
    
    # Just run lualatex once for M0 test
    result = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", f"-output-directory={build_dir}", main_tex],
        cwd=latex_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Compilation failed!")
        print(result.stdout)
        sys.exit(result.returncode)
    print("Compilation successful.")
    
def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Article/Book Generation")
    parser.add_argument("--topic", required=True, help="Topic of the document")
    parser.add_argument("--language", required=True, help="Language of the document (e.g., English, Hebrew)")
    
    args = parser.parse_args()
    config = get_config()
    
    print(f"Starting generation for topic: '{args.topic}' in '{args.language}'")
    print(f"Using Model: {config['model']}")
    
    project_dir = os.path.dirname(__file__)
    latex_dir = os.path.join(project_dir, "latex")
    compile_latex(project_dir, latex_dir, "main.tex")

if __name__ == "__main__":
    main()
