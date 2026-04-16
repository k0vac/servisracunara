from fastapi import FastAPI, Response


app = FastAPI()

def entryFactory(id, name, timestamp, description):
    return {
        "id": id,
        "name": name,
        "timestamp": timestamp,
        "description": description
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/login")
def login(response: Response):
    response.set_cookie(key="session", value="abc123", httponly=True)
    return {"message": "Login successful"}

fake_entries = [
    entryFactory(1, "Entry 1", "2024-01-01T12:00:00Z", "Description for Entry 1"),
    entryFactory(2, "Entry 2", "2024-01-02T12:00:00Z", "Description for Entry 2"),
    entryFactory(3, "Entry 3", "2024-01-03T12:00:00Z", "Description for Entry 3")
]

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


