import sys, os
from sqlalchemy import delete, select, func
sys.path.append(r'C:\Users\Ritik\OneDrive\Desktop\projects\HireMind\backend')
from database.connection import SessionLocal
from models.user import User
from models.resume import Resume
from models.interview import InterviewQuestion, InterviewSession, InterviewResponse

db = SessionLocal()
test_texts = ['EASY 1', 'EASY 2', 'MEDIUM 1', 'MEDIUM 2', 'MEDIUM 3', 'HARD 1', 'HARD 2', 'HARD 3']

# Find IDs of these questions
q_ids = db.execute(select(InterviewQuestion.id).where(InterviewQuestion.question_text.in_(test_texts))).scalars().all()

if q_ids:
    db.execute(delete(InterviewResponse).where(InterviewResponse.question_id.in_(q_ids)))
    db.execute(delete(InterviewSession).where(InterviewSession.current_question_id.in_(q_ids)))
    db.execute(delete(InterviewQuestion).where(InterviewQuestion.id.in_(q_ids)))

db.commit()

count = db.execute(select(func.count(InterviewQuestion.id))).scalar()
print(f'Deleted {len(q_ids)} test questions.')
print(f'Remaining questions: {count}')
db.close()
