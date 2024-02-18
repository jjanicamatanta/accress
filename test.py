from fastapi import FastAPI

from reactpy import component, html
from reactpy.backend.fastapi import configure


@component
def HelloWorld():
    return html.h1("Hello, world2!")


app = FastAPI()
configure(app, HelloWorld)