from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, admin, farmer, buyer, common, payments, deliveries, firebase
from database import Base, engine
import uvicorn

app = FastAPI(title="Farmer Market System")

origins = [
    "http://localhost:3000",
    "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(firebase.router, prefix="/firebase", tags=["Firebase"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(farmer.router, prefix="/farmer", tags=["Farmer"])
app.include_router(buyer.router, prefix="/buyer", tags=["Buyer"])
app.include_router(common.router, prefix="/common", tags=["Common"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
