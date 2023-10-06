import sys

sys.path.append(".")

import os

import sqltap
import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from routers import admin, auth, todos, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


# models.Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
profiler = sqltap.start()
statistics = []


@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@app.get(
    "/sqltap_write_stats",
    include_in_schema=False,
    response_class=HTMLResponse,
)
def sqltap_write_stats(request: Request):
    global statistics
    global profiler
    templates = Jinja2Templates(directory="debug_folder")
    os.makedirs("debug_folder", exist_ok=True)
    statistics.extend(profiler.collect())
    sqltap.report(
        statistics, "debug_folder" + "/sqltap_report.html", report_format="html"
    )
    return templates.TemplateResponse("sqltap_report.html", {"request": request})


@app.get(
    "/sqltap_clear_stats",
    include_in_schema=False,
    response_class=HTMLResponse,
)
def sqltap_clear_stats():
    global statistics
    statistics = []
    return """
<html>
    <head>
        <title>SqlAlchemy stats</title>

    </head>
    <body>
        <h2>Cleared!</h2>
    </body>
</html>
"""


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0")
