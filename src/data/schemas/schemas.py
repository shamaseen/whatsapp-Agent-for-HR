from pydantic import BaseModel
from typing import Dict, Any, List

class WhatsAppMessage(BaseModel):
    message_type: str
    conversation: Dict[str, Any]
    sender: Dict[str, Any]
    content: str

class CVData(BaseModel):
    fileName: str
    name: str
    email: str
    phone: str
    skills: str
    experienceYears: str
    education: str
    jobTitles: str
    summary: str

class CandidateRank(BaseModel):
    rank: int
    candidate_name: str
    email: str
    phone: str
    match_score: int
    reasoning: str
