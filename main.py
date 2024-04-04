from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


app = FastAPI()


@app.get("/")
async def read_root():
    return FileResponse("page.html", media_type="text/html")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calories_per_100g = Column(Float)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/ingredient/")
async def create_ingredient(
    name: str, calories_per_100g: float, db: Session = Depends(get_db)
):
    db_ingredient = Ingredient(name=name, calories_per_100g=calories_per_100g)
    db.add(db_ingredient)
    db.commit()
    return db_ingredient


@app.get("/calculate/")
async def calculate_calories(
    name: str, weight: float, db: Session = Depends(get_db)
):
    db_ingredient = db.query(Ingredient).filter(
        Ingredient.name == name
    ).first()
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")

    total_calories = db_ingredient.calories_per_100g / 100 * weight
    return {"name": name, "calories": total_calories}
