import logging
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlalchemy import text

from auth import get_current_user, require_admin
from db import get_engine
from schemas import DocumentOut
from src.vector_tool import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["documents"])


def _document_out(row) -> DocumentOut:
    return DocumentOut(**dict(row))


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(_: dict = Depends(get_current_user)) -> list[DocumentOut]:
    with get_engine().connect() as connection:
        rows = connection.execute(
            text("SELECT * FROM documents ORDER BY uploaded_at DESC")
        ).mappings().all()
    return [_document_out(row) for row in rows]


@router.post("/documents/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin),
) -> DocumentOut:
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf") or file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF uploads are allowed")

    temp_path: str | None = None
    document_status = "processing"
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
            temp_path = temporary_file.name
            shutil.copyfileobj(file.file, temporary_file)

        reader = PdfReader(temp_path)
        content = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if not content:
            raise ValueError("The PDF does not contain extractable text")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_text(content)
        if not chunks:
            raise ValueError("No text chunks were created from the PDF")
        get_vector_store().add_documents(
            [Document(page_content=chunk, metadata={"source": filename}) for chunk in chunks]
        )
        document_status = "processed"
    except Exception:
        document_status = "failed"
        logger.exception("Document ingestion failed for %s", filename)
    finally:
        file.file.close()
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)

    with get_engine().begin() as connection:
        row = connection.execute(
            text("""
                INSERT INTO documents (filename, uploaded_by, status)
                VALUES (:filename, :uploaded_by, :status)
                RETURNING *
            """),
            {"filename": filename, "uploaded_by": current_user["username"], "status": document_status},
        ).mappings().one()
    return _document_out(row)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, current_user: dict = Depends(require_admin)) -> None:
    with get_engine().begin() as connection:
        row = connection.execute(
            text("SELECT filename FROM documents WHERE id = :id"), {"id": document_id}
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        get_vector_store().delete(filter={"source": row["filename"]})
        connection.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document_id})
    logger.info(
        "Document deleted: filename=%s document_id=%s deleted_by=%s",
        row["filename"],
        document_id,
        current_user["username"],
    )
