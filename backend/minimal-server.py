from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

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

@app.get("/api/tools")
def get_tools():
    return {"tools": [
        {"name": "read_file", "description": "Read file contents"},
        {"name": "write_file", "description": "Write file contents"},
        {"name": "list_directory", "description": "List directory contents"},
        {"name": "search_files", "description": "Search for files"}
    ]}

@app.get("/mcp/api/v1/context")
def get_context():
    return {"context": "MCP Server Context"}

@app.get("/mcp/api/v1/files")
def get_files():
    return {"files": []}

@app.get("/mcp/api/v1/monitoring/health")
def monitoring_health():
    return {"status": "healthy", "monitoring": "active"}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    # Create uploads directory
    upload_dir = Path("data/files")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return {"message": "File uploaded successfully", "filename": file.filename, "size": len(content)}

if __name__ == "__main__":
    print("Starting MCP Server...")
    print("Server: http://localhost:8000")
    print("Health: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
