# Example project

## Project Structure

project/
|--- dashboard/                                    - dir (with app instance, layout and assets).
|        |--- assets/                              - with custom stylesheets, favicon, logos and other static elements.
|        |--- layout/                              - with app components including header, tabs, callbacks, etc.
|                 |--- callbacks/
|                          |--- callbacks1.py
|                          |___ callbacks2.py
|                 |--- header.py
|                 |--- tab_1.py
|                 |___ tab_2.py
|        |--- content.py                        - which contains callbacks imports so they can be registered with Dash app instance.
|        |___ index.py                          - with Dash app definition.
|--- app.py                                     - the entry point to the app that imports everything else and initiates server (for running in Gunicorn).
|--- Procfile                                   - for running in Gunicorn.
|___requirements.txt                            - with all dependencies.

