#! /usr/bin/env bash

npm install
npm run build

rm -f dist/zena-setup.zip

python -m zipapp "src" \
    --output "dist/zena-setup" \
    --python "/usr/bin/env python3"
