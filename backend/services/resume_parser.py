import io
import re
from pypdf import PdfReader
from typing import List

# Curated academic MVP taxonomy
SKILL_TAXONOMY = [
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", 
    "SQL", "PostgreSQL", "MySQL", "HTML", "CSS", "React", 
    "Node.js", "FastAPI", "Django", "Spring Boot", "Git", 
    "Docker", "AWS", "Azure", "Machine Learning", 
    "Deep Learning", "NLP", "TensorFlow", "PyTorch", 
    "Pandas", "NumPy", "Scikit-learn"
]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        # Normalize whitespace (replace multiple spaces/newlines with single space)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")

def extract_skills(text: str) -> List[str]:
    """Extracts skills from text based on a predefined taxonomy using whole-word matching."""
    if not text:
        return []
        
    detected_skills = set()
    text_lower = text.lower()
    
    for skill in SKILL_TAXONOMY:
        escaped_skill = re.escape(skill.lower())
        # Boundary matching: 
        # Left boundary: cannot be preceded by alphanumeric.
        # Right boundary: cannot be followed by alphanumeric, +, or # (prevents "C" from matching "C++" or "C#").
        pattern = r'(?<![a-zA-Z0-9])' + escaped_skill + r'(?![a-zA-Z0-9+#])'
        
        if re.search(pattern, text_lower):
            detected_skills.add(skill)
            
    return sorted(list(detected_skills))
