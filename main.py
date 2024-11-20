from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, admin, farmer, buyer, common, payments, deliveries
from database import Base, engine

# Create FastAPI instance
app = FastAPI(title="Farmer Market System")

# Define allowed origins (list of domains you want to allow)
origins = [
    "http://localhost:3000",  # Example: React or Vue app running locally
    "https://yourdomain.com", # Replace with your actual domain
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(farmer.router, prefix="/farmer", tags=["Farmer"])
app.include_router(buyer.router, prefix="/buyer", tags=["Buyer"])
app.include_router(common.router, prefix="/common", tags=["Common"])
app.include_router(payments.router, prefix="", tags=["Payments"])
app.include_router(deliveries.router, prefix="", tags=["Deliveries"])

if __name__ == "__main__":
    import uvicorn

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Run the application with uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
