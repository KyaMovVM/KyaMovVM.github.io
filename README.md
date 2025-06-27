# KyaMovVM.github.io

This repository hosts a simple demo site with a rotating 3D car and Material Design colors.
Additional pages provide an API log viewer and basic documentation. A small Python
script (`backend_tools.py`) demonstrates how backend interactions over SSH and
HTTP requests could be performed.

## Pages
- **index.html** – main demo with the 3D car animation.
- **api.html** – placeholder interface for viewing backend logs.
- **fail2ban.html** – interface for viewing Fail2Ban logs.
- **docs.html** – minimal API documentation.
- **jsdoc/index.html** – generated interface reference using JSDoc.

Each page includes a menu entry to show a transparent UML overlay with a simple architecture diagram (`uml-diagram.svg`). The Fail2Ban page uses <code>fail2ban-uml.svg</code>.

## Backend script
`backend_tools.py` connects to a host via SSH and performs HTTP GET requests.
It is only an example, credentials must be updated before use. GPU tasks can
be prototyped using the [cuda-python](https://github.com/NVIDIA/cuda-python)
library.

## Interface documentation
JavaScript functions are commented in the JSDoc format. Run `npx jsdoc -c jsdoc.json`
to generate HTML docs inside the `jsdoc/` folder.

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

## Manual Tests

Open each HTML page in a browser and ensure the UML overlay appears when clicking the menu entry. Check that the Fail2Ban page shows placeholder logs and that CUDA device listing runs without errors.
## Development Plan
Detailed steps for designing and maintaining the project are described in [development_plan.md](development_plan.md).
