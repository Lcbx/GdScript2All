python -m nuitka --standalone --show-progress addons/gdscript2all/converter/main.py --output-dir=nuitka_build --include-plugin-directory=addons/gdscript2all/converter/libs --include-package=src

mv -f nuitka_build/main.dist/* addons/gdscript2all/converter/build

cp LICENSE addons/gdscript2all/
cp README.md addons/gdscript2all/
