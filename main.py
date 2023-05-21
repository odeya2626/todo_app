import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import models
from db import engine
from routers import auth, todos, admin, users
from fastapi import status
from starlette.responses import RedirectResponse

app = FastAPI()
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)


# models.Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0")
