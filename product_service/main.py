from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/drop")
def get_drop():
    return {
        "shoe_name": "Limited Edition SB Dunk",
        "price": 120.00,
        "drop_time": "2026-05-01T10:00:00Z"
    }
