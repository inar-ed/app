from fastapi import FastAPI, HTTPException, status, Path, Query, Header, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

from models import User, UserCreate, UserUpdate

app = FastAPI(
    title="FastAPI Users API",
    description="Пример API по первым 5 статьям Metanit + CRUD пользователей",
    version="1.0.0",
    swagger_ui_parameters={
        "syntaxHighlight": {"theme": "obsidian"},
        "deepLinking": True,
        "displayRequestDuration": True,
        "defaultModelsExpandDepth": 1,
    },
)

users_db: dict[int, User] = {}
next_id: int = 1


@app.get("/", summary="Главная страница", tags=["Основы"])
async def root():
    return {"message": "Привет, FastAPI!", "docs": "/docs"}


@app.get("/hello/{name}", summary="Приветствие по имени", tags=["Основы"])
async def hello_name(name: str = Path(..., min_length=1, max_length=30)):
    return {"message": f"Привет, {name}!"}


@app.get("/search", summary="Поиск с query-параметрами", tags=["Основы"])
async def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Максимум результатов"),
):
    results = [u for u in users_db.values() if q.lower() in u.name.lower()][:limit]
    return {"query": q, "limit": limit, "count": len(results), "results": results}


@app.get("/status-demo/{code}", summary="Демонстрация статус-кодов", tags=["Основы"])
async def status_demo(code: int = Path(..., ge=100, le=599)):
    if 200 <= code < 300:
        return JSONResponse(status_code=code, content={"status": code, "type": "success"})
    return JSONResponse(status_code=code, content={"status": code, "type": "error"})


@app.get("/old-page", summary="Редирект на новую страницу", tags=["Основы"])
async def old_page():
    return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/headers-cookies", summary="Чтение заголовков и кук", tags=["Основы"])
async def headers_cookies(
    user_agent: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None),
):
    return {"user_agent": user_agent, "session_id": session_id}


@app.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    tags=["Users CRUD"],
)
async def create_user(payload: UserCreate):
    global next_id
    if any(u.email == payload.email for u in users_db.values()):
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    user = User(id=next_id, **payload.model_dump())
    users_db[next_id] = user
    next_id += 1
    return user


@app.get(
    "/users",
    response_model=list[User],
    summary="Список всех пользователей",
    tags=["Users CRUD"],
)
async def list_users():
    return list(users_db.values())


@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Получить пользователя по ID",
    tags=["Users CRUD"],
)
async def get_user(user_id: int = Path(..., ge=1)):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f"Пользователь {user_id} не найден")
    return users_db[user_id]


@app.put(
    "/users/{user_id}",
    response_model=User,
    summary="Полностью обновить пользователя",
    tags=["Users CRUD"],
)
async def update_user(user_id: int, payload: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if any(u.email == payload.email and u.id != user_id for u in users_db.values()):
        raise HTTPException(status_code=409, detail="Email уже занят")
    users_db[user_id] = User(id=user_id, **payload.model_dump())
    return users_db[user_id]


@app.patch(
    "/users/{user_id}",
    response_model=User,
    summary="Частично обновить пользователя",
    tags=["Users CRUD"],
)
async def patch_user(user_id: int, payload: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    current = users_db[user_id]
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and any(
        u.email == data["email"] and u.id != user_id for u in users_db.values()
    ):
        raise HTTPException(status_code=409, detail="Email уже занят")
    updated = current.model_copy(update=data)
    users_db[user_id] = updated
    return updated


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    tags=["Users CRUD"],
)
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    del users_db[user_id]
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)