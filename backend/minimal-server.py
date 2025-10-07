from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MCP Server is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    return {"message": "File uploaded successfully", "filename": file.filename}

if __name__ == "__main__":
    print("Starting MCP Server...")
    print("Server: http://localhost:8000")
    print("Health: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
