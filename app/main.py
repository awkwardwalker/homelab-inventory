from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .models import HomeLabItem

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# For a starter project, auto-create tables. Later: use Alembic migrations.
Base.metadata.create_all(bind=engine)

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, q: str | None = None):
    with SessionLocal() as db:
        stmt = select(HomeLabItem).order_by(HomeLabItem.name.asc())
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (HomeLabItem.name.ilike(like)) |
                (HomeLabItem.vlan_name.ilike(like)) |
                (HomeLabItem.description.ilike(like)) |
                (HomeLabItem.public_url.ilike(like))
            )
        items = db.execute(stmt).scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "items": items, "q": q or ""})

@app.get("/new", response_class=HTMLResponse)
def new_item(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "item": None})

@app.post("/new")
def create_item(
    name: str = Form(...),
    ip_address: str | None = Form(None),
    vlan_id: int | None = Form(None),
    vlan_name: str | None = Form(None),
    description: str | None = Form(None),
    is_public: bool = Form(False),
    public_url: str | None = Form(None),
):
    with SessionLocal() as db:
        item = HomeLabItem(
            name=name.strip(),
            ip_address=ip_address.strip() if ip_address else None,
            vlan_id=vlan_id,
            vlan_name=vlan_name.strip() if vlan_name else None,
            description=description.strip() if description else None,
            is_public=is_public,
            public_url=public_url.strip() if public_url else None,
        )
        db.add(item)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit/{item_id}", response_class=HTMLResponse)
def edit_item(request: Request, item_id: int):
    with SessionLocal() as db:
        item = db.get(HomeLabItem, item_id)
        if not item:
            return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse("form.html", {"request": request, "item": item})

@app.post("/edit/{item_id}")
def update_item(
    item_id: int,
    name: str = Form(...),
    ip_address: str | None = Form(None),
    vlan_id: int | None = Form(None),
    vlan_name: str | None = Form(None),
    description: str | None = Form(None),
    is_public: bool = Form(False),
    public_url: str | None = Form(None),
):
    with SessionLocal() as db:
        item = db.get(HomeLabItem, item_id)
        if not item:
            return HTMLResponse("Not found", status_code=404)

        item.name = name.strip()
        item.ip_address = ip_address.strip() if ip_address else None
        item.vlan_id = vlan_id
        item.vlan_name = vlan_name.strip() if vlan_name else None
        item.description = description.strip() if description else None
        item.is_public = is_public
        item.public_url = public_url.strip() if public_url else None

        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{item_id}")
def delete_item(item_id: int):
    with SessionLocal() as db:
        item = db.get(HomeLabItem, item_id)
        if item:
            db.delete(item)
            db.commit()
    return RedirectResponse(url="/", status_code=303)
