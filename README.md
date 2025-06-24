# KyaMovVM.github.io

This repository hosts a simple demo site with a rotating 3D car and Material Design colors.
Additional pages provide an API log viewer and basic documentation. A small Python
script (`backend_tools.py`) demonstrates how backend interactions over SSH and
HTTP requests could be performed.

## Pages
- **index.html** – main demo with the 3D car animation.
- **api.html** – placeholder interface for viewing backend logs.
- **docs.html** – minimal API documentation.

Each page includes a menu entry to show a transparent UML overlay with a simple architecture diagram (`uml-diagram.svg`).

## Backend script
`backend_tools.py` connects to a host via SSH and performs HTTP GET requests. It
is only an example, credentials must be updated before use.

## Tests
Unit tests for the backend script are located in `test_backend_tools.py`.
To run them, first install the required dependencies:

```bash
pip install -r requirements.txt
```

Then execute the tests with:

```bash
python -m unittest
```
## Development Plan
Detailed steps for designing and maintaining the project are described in [development_plan.md](development_plan.md).
