from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

app = FastAPI(title="Global Leaderboard of Despair")

@app.get("/", response_class=HTMLResponse)
def get_leaderboard_page():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>Leaderboard UI not found</h1>"

@app.get("/bg1.png", response_class=FileResponse)
def get_background():
    img_path = Path(__file__).parent.parent / "bg1.png"
    return str(img_path)

Base = declarative_base()

class ScoreRecord(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    despair_score = Column(Float)
    commit_message = Column(String)

engine = create_engine("sqlite:///./despair.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

class ScoreCreate(BaseModel):
    username: str
    despair_score: float
    commit_message: str

class LeaderboardEntry(BaseModel):
    username: str
    total_despair: float
    commits: int
    latest_message: str

@app.post("/score")
def submit_score(score: ScoreCreate):
    db = SessionLocal()
    db_score = ScoreRecord(
        username=score.username,
        despair_score=score.despair_score,
        commit_message=score.commit_message
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    db.close()
    return {"status": "success"}

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard():
    db = SessionLocal()
    records = db.query(ScoreRecord).all()
    db.close()
    
    # Aggregate scores
    users = {}
    for r in records:
        if r.username not in users:
            users[r.username] = {
                "total_despair": 0.0,
                "commits": 0,
                "latest_message": r.commit_message
            }
        users[r.username]["total_despair"] += r.despair_score
        users[r.username]["commits"] += 1
        # Just use the last one encountered as latest
        users[r.username]["latest_message"] = r.commit_message
        
    leaderboard = []
    for uname, data in users.items():
        leaderboard.append(LeaderboardEntry(
            username=uname,
            total_despair=data["total_despair"],
            commits=data["commits"],
            latest_message=data["latest_message"]
        ))
        
    # Sort by total_despair descending (highest despair first)
    leaderboard.sort(key=lambda x: x.total_despair, reverse=True)
    
    # Return top 10
    return leaderboard[:10]
