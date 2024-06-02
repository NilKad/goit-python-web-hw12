from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import contacts as contacts_routes

app = FastAPI()

app.include_router(contacts_routes.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Contact aplication goit-python-web-hw12"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {
            "message": "Welcome to FastAPI! HealthChecker goit-python-web-hw12 - OK"
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
