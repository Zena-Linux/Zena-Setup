#! /usr/bin/env bash

npm install
npm run build

rm -f dist/zena-setup.zip
rm -f dist/zena-setup-daemon.zip

python -m zipapp "src/gui" \
    --output "dist/zena-setup" \
    --python "/usr/bin/env python3"

python -m zipapp "src/daemon" \
    --output "dist/zena-setup-daemon" \
    --python "/usr/bin/env python3"
