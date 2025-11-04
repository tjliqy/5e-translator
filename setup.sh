find output -type f ! -name "*.json" -delete
cp -r output/* ../5etools-mirror-2.github.io/data/
cd ../5etools-mirror-2.github.io
npm run build