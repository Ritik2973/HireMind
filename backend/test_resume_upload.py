import os
from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.user import User
from models.resume import Resume
from fpdf import FPDF

client = TestClient(app)

def setup_users():
    db = SessionLocal()
    # Clean up old data
    db.execute(Resume.__table__.delete())
    db.execute(User.__table__.delete().where(User.email.in_(["resume_user1@example.com", "resume_user2@example.com"])))
    db.commit()
    
    client.post("/auth/register", json={
        "name": "User One", "email": "resume_user1@example.com", "password": "password123"
    })
    client.post("/auth/register", json={
        "name": "User Two", "email": "resume_user2@example.com", "password": "password123"
    })
    db.close()

def get_token(email):
    res = client.post("/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]

def create_test_pdf(filename, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)
    return filename

def run_tests():
    print("--- Running tests for Resume Upload API ---")
    setup_users()
    
    token1 = get_token("resume_user1@example.com")
    token2 = get_token("resume_user2@example.com")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Generate test PDF
    pdf_path = create_test_pdf("test_resume.pdf", "Experienced Python and React developer with SQL skills. Familiar with Docker and AWS.")
    
    try:
        # TEST 1: Unauthenticated upload
        print("\nTEST 1: Unauthenticated upload")
        with open(pdf_path, "rb") as f:
            res1 = client.post("/resumes/upload", files={"file": ("test.pdf", f, "application/pdf")})
        assert res1.status_code == 401

        # TEST 2: Valid authenticated upload
        print("\nTEST 2: Valid authenticated upload")
        with open(pdf_path, "rb") as f:
            res2 = client.post("/resumes/upload", headers=headers1, files={"file": ("test_resume.pdf", f, "application/pdf")})
        assert res2.status_code == 201
        data2 = res2.json()
        assert "id" in data2
        assert "Python" in data2["skills"]
        assert "React" in data2["skills"]
        assert "SQL" in data2["skills"]
        assert "Docker" in data2["skills"]
        assert "AWS" in data2["skills"]
        resume_id = data2["id"]

        # TEST 3: Retrieve resumes
        print("\nTEST 3: GET /resumes")
        res3 = client.get("/resumes", headers=headers1)
        assert res3.status_code == 200
        assert len(res3.json()) == 1

        # TEST 4: Get specific resume
        print("\nTEST 4: GET /resumes/{id}")
        res4 = client.get(f"/resumes/{resume_id}", headers=headers1)
        assert res4.status_code == 200
        assert "extracted_text" in res4.json()

        # TEST 5: Access denied for other user
        print("\nTEST 5: Prevent cross-user access")
        res5 = client.get(f"/resumes/{resume_id}", headers=headers2)
        assert res5.status_code == 403

        # TEST 6: Non-PDF upload
        print("\nTEST 6: Non-PDF upload")
        res6 = client.post("/resumes/upload", headers=headers1, files={"file": ("test.txt", b"Hello", "text/plain")})
        assert res6.status_code == 422

        # TEST 7: Empty PDF upload
        print("\nTEST 7: Empty PDF upload")
        res7 = client.post("/resumes/upload", headers=headers1, files={"file": ("empty.pdf", b"", "application/pdf")})
        assert res7.status_code == 400

        # TEST 8: File larger than 5 MB
        print("\nTEST 8: File larger than 5 MB")
        large_payload = b"0" * (5 * 1024 * 1024 + 10)
        res8 = client.post("/resumes/upload", headers=headers1, files={"file": ("large.pdf", large_payload, "application/pdf")})
        assert res8.status_code == 413

        # TEST 9: Malformed PDF
        print("\nTEST 9: Malformed PDF")
        res9 = client.post("/resumes/upload", headers=headers1, files={"file": ("malformed.pdf", b"This is not a PDF", "application/pdf")})
        assert res9.status_code == 422

        # TEST 10: Valid PDF with no extractable text
        print("\nTEST 10: Valid PDF with no extractable text")
        empty_pdf_path = "no_text.pdf"
        pdf_empty = FPDF()
        pdf_empty.add_page()
        pdf_empty.output(empty_pdf_path)
        with open(empty_pdf_path, "rb") as f:
            res10 = client.post("/resumes/upload", headers=headers1, files={"file": ("no_text.pdf", f, "application/pdf")})
        assert res10.status_code == 422
        if os.path.exists(empty_pdf_path):
            os.remove(empty_pdf_path)

        print("\nAll tests passed successfully!")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    run_tests()
