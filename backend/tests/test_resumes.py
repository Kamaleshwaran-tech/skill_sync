import io
from docx import Document
from app.database.session import SessionLocal


def create_user_and_get_token(client, email="resume_user@example.com"):
    payload = {"email": email, "password": "ResuMeP@ss123", "full_name": "Resume User"}
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 200
    r2 = client.post("/api/v1/auth/login", json={"email": email, "password": "ResuMeP@ss123"})
    assert r2.status_code == 200
    tokens = r2.json()
    return tokens["access_token"]


def test_upload_and_manage_resumes(client):
    token = create_user_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # upload pdf
    pdf_bytes = b"%PDF-1.4 sample pdf content"
    files = {"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    r = client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert r.status_code == 200
    resume = r.json()
    assert resume["file_type"] == "pdf"
    resume_id = resume["id"]

    # upload docx
    document = Document()
    document.add_paragraph("Resume candidate with Python and FastAPI experience")
    docx_buffer = io.BytesIO()
    document.save(docx_buffer)
    files = {"file": ("resume.docx", io.BytesIO(docx_buffer.getvalue()), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    r2 = client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert r2.status_code == 200

    # invalid type
    txt_bytes = b"just text"
    files = {"file": ("resume.txt", io.BytesIO(txt_bytes), "text/plain")}
    r3 = client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert r3.status_code == 400

    invalid_pdf = {"file": ("invalid.pdf", io.BytesIO(b"not a PDF"), "application/pdf")}
    r4 = client.post("/api/v1/resumes/upload", files=invalid_pdf, headers=headers)
    assert r4.status_code == 400

    # list resumes
    rlist = client.get("/api/v1/resumes/", headers=headers)
    assert rlist.status_code == 200
    assert len(rlist.json()) >= 2

    # get resume
    rget = client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert rget.status_code == 200

    # analyze resume
    ran = client.post(f"/api/v1/resumes/{resume_id}/analyze", headers=headers)
    assert ran.status_code == 200
    assert ran.json()["status"] == "COMPLETED"

    # delete resume
    rdel = client.delete(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert rdel.status_code == 200


def test_too_large_file(client):
    token = create_user_and_get_token(client, email="bigfile@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    # create bytes larger than allowed (settings default 5MB)
    big = b"0" * (6 * 1024 * 1024)
    files = {"file": ("big.pdf", io.BytesIO(big), "application/pdf")}
    r = client.post("/api/v1/resumes/upload", files=files, headers=headers)
    assert r.status_code == 400
