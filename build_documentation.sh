#!/bin/bash
# build_and_deploy_docs.sh
# Automatisches Bauen der Sphinx-Doku und Push auf gh-pages

set -e  # Abbruch bei Fehler

echo "🚀 Building Sphinx documentation..."

cd docs
make clean
make html
cd ..

echo "📦 Switching to gh-pages branch..."
git checkout gh-pages

echo "🗑 Removing old HTML files..."
git rm -rf .

echo "📂 Copying new HTML files..."
cp -r docs/build/html/_static .
cp -r docs/build/html/_sources .
cp docs/build/html/*.html .

# Optional: alte source-Ordner entfernen
rm -rf docs/ src/

echo "💾 Adding and committing changes..."
git add -A
git commit -m "Update of Documentation"

echo "📤 Pushing to gh-pages..."
git push origin gh-pages

echo "🔙 Switching back to master..."
git checkout master

echo "✅ Documentation deployed!"

