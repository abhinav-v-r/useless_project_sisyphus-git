from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import os

# Resolve paths relative to the project root (one level up from backend/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Sisyphus-Git Leaderboard of Despair")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow file:// and local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(ROOT_DIR, "despair.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS developer_despair (
            username TEXT PRIMARY KEY,
            total_despair REAL DEFAULT 0,
            commits INTEGER DEFAULT 0,
            latest_message TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Serve bg1.png as a static asset
    bg_path = os.path.join(ROOT_DIR, "bg1.png")
    if os.path.exists(bg_path):
        app.mount("/bg1.png", StaticFiles(directory=ROOT_DIR, html=False), name="static")

class ScorePayload(BaseModel):
    username: str
    despair_score: float
    commit_message: str

@app.post("/score")
def submit_score(payload: ScorePayload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT total_despair, commits FROM developer_despair WHERE username = ?", (payload.username,))
        row = cursor.fetchone()
        
        if row:
            # We treat the despair score as negative impact
            new_despair = row[0] - payload.despair_score
            new_commits = row[1] + 1
            cursor.execute("""
                UPDATE developer_despair 
                SET total_despair = ?, commits = ?, latest_message = ?
                WHERE username = ?
            """, (new_despair, new_commits, payload.commit_message, payload.username))
        else:
            # First time user
            initial_despair = -payload.despair_score
            cursor.execute("""
                INSERT INTO developer_despair (username, total_despair, commits, latest_message)
                VALUES (?, ?, ?, ?)
            """, (payload.username, initial_despair, 1, payload.commit_message))
            
        conn.commit()
        conn.close()
        return {"status": "success", "message": "The void has acknowledged your suffering."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leaderboard")
def get_leaderboard():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Sort by most negative score first, limited to top 10
        cursor.execute("""
            SELECT username, total_despair, commits, latest_message 
            FROM developer_despair 
            ORDER BY total_despair ASC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the frontend — index.html at the root URL
@app.get("/")
def serve_frontend():
    index_path = os.path.join(ROOT_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/bg1.png")
def serve_background():
    bg_path = os.path.join(ROOT_DIR, "bg1.png")
    return FileResponse(bg_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
