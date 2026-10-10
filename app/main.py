from fastapi import FastAPI, Request
from app.routers import users, orders, auth, github, calculate, tasks
from fastapi.staticfiles import StaticFiles
import time



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"← {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(users.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(github.router)
app.include_router(calculate.router)
app.include_router(tasks.router)




