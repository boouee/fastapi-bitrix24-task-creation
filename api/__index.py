from fastapi import FastAPI

# Initialize the FastAPI application instance
app = FastAPI()

# Define a root route that responds to HTTP GET requests
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
