# Work in progress

This repository takes an experimental approach of hot-inspecting the live object-tree. (Something difficult/impossible to do in other languages)

By introspecting the root of the API, and collecting all of its members we can wrap an entire API SDK and instantly put it onto the graph.

python3 main.py serve --configuration config.json --port 8101 --service-token-secret secret

python3 main.py configuration serve --port 9101
