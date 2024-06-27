py -m nuitka --standalone --show-progress main.py  --output-dir=nuitka_build --include-plugin-directory=libs --include-package=src

rm -rf addons/gdscript2all/converter/*
mv nuitka_build/main.dist/* addons/gdscript2all/converter
cp -r src addons/gdscript2all/converter/src

cp LICENSE addons/gdscript2all/
cp README.md addons/gdscript2all/
