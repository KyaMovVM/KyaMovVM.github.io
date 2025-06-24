# KyaMovVM.github.io

This repository hosts a simple demo site with a rotating 3D car and Material Design colors.
Additional pages provide an API log viewer and basic documentation. A small Python
script (`backend_tools.py`) demonstrates how backend interactions over SSH and
HTTP requests could be performed.

## Pages
- **index.html** – main demo with the 3D car animation.
- **api.html** – placeholder interface for viewing backend logs.
- **docs.html** – minimal API documentation.

All pages include a menu entry to show a transparent UML overlay with a placeholder diagram.
## Backend script
`backend_tools.py` connects to a host via SSH and performs HTTP GET requests. It
is only an example, credentials must be updated before use.
