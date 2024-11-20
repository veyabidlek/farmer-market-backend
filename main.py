from fastapi import FastAPI
from routers import auth, admin, farmer, buyer, common
from database import Base, engine

# Create FastAPI instance
app = FastAPI(title="Farmer Market System")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(farmer.router, prefix="/farmer", tags=["Farmer"])
app.include_router(buyer.router, prefix="/buyer", tags=["Buyer"])
app.include_router(common.router, prefix="/common", tags=["Common"])


if __name__ == "__main__":
    import uvicorn

    Base.metadata.create_all(bind=engine)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
