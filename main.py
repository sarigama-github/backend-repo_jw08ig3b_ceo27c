import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Build

app = FastAPI(title="Lamrrari API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Public brand and models data (static for now) ----
class Model(BaseModel):
    id: str
    name: str
    tagline: str
    base_price: float
    range_km: int
    power_kw: int

MODELS: List[Model] = [
    Model(id="vento", name="Lamrrari Vento", tagline="Ultra Luxury Electric SUV", base_price=240000, range_km=720, power_kw=560),
    Model(id="tempesta", name="Lamrrari Tempesta", tagline="Track-Bred, Road-Ready SUV", base_price=290000, range_km=680, power_kw=640),
    Model(id="serenissima", name="Lamrrari Serenissima", tagline="Effortless Grand Touring EV", base_price=210000, range_km=780, power_kw=520),
]

COLORS = [
    {"id": "nero-shade", "name": "Nero Shade", "hex": "#0f1115", "price": 0},
    {"id": "rosso-uae", "name": "Rosso Emirates", "hex": "#b10020", "price": 2500},
    {"id": "bianco-alpi", "name": "Bianco Alpi", "hex": "#f3f4f6", "price": 1500},
    {"id": "grigio-tempesta", "name": "Grigio Tempesta", "hex": "#4b5563", "price": 1500},
]

WHEELS = [
    {"id": "aero-22", "name": "Aero 22\"", "price": 0},
    {"id": "forged-23", "name": "Forged 23\"", "price": 3500},
    {"id": "carbon-23", "name": "Carbon 23\"", "price": 9000},
]

INTERIORS = [
    {"id": "nero-rosso", "name": "Nero / Rosso", "price": 0},
    {"id": "sabbia", "name": "Sabbia", "price": 1200},
    {"id": "bianco-perla", "name": "Bianco Perla", "price": 1800},
]

ADDONS = [
    {"id": "pilota-pack", "name": "Pilota Performance Pack", "price": 12000},
    {"id": "autonomia-max", "name": "Autonomia Max Range", "price": 8000},
    {"id": "suite-ammiraglia", "name": "Suite Ammiraglia (Rear Luxury)", "price": 15000},
]

@app.get("/")
def read_root():
    return {"brand": "Lamrrari", "message": "Welcome to Lamrrari API"}

@app.get("/api/models")
def get_models():
    return {"models": [m.model_dump() for m in MODELS]}

@app.get("/api/config-options")
def get_config_options():
    return {
        "colors": COLORS,
        "wheels": WHEELS,
        "interiors": INTERIORS,
        "addons": ADDONS,
    }

class PriceRequest(BaseModel):
    model_id: str
    color_id: str
    wheels_id: str
    interior_id: str
    addons: List[str] = []

@app.post("/api/price")
def calculate_price(body: PriceRequest):
    # Base
    model = next((m for m in MODELS if m.id == body.model_id), None)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    price = model.base_price

    # Options
    def p(list_, id_):
        item = next((i for i in list_ if i["id"] == id_), None)
        if item is None:
            raise HTTPException(status_code=400, detail=f"Invalid option: {id_}")
        return item["price"]

    price += p(COLORS, body.color_id)
    price += p(WHEELS, body.wheels_id)
    price += p(INTERIORS, body.interior_id)
    for add in body.addons:
        price += p(ADDONS, add)

    # Regional pricing logic (example: UAE premium market +5%)
    region_multiplier = 1.05
    final_price = round(price * region_multiplier, 2)
    return {"currency": "USD", "price": final_price}

class SaveBuildRequest(Build):
    pass

@app.post("/api/builds")
def save_build(build: SaveBuildRequest):
    try:
        build_id = create_document("build", build)
        return {"ok": True, "id": build_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/builds")
def list_builds(limit: Optional[int] = 25):
    try:
        docs = get_documents("build", {}, limit)
        # Convert ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d["_id"])
                del d["_id"]
        return {"builds": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
