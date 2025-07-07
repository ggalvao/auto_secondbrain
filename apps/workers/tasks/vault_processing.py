import os
import zipfile
from typing import Dict, Any
from uuid import UUID

import structlog

from libs.database.connection import get_db
from libs.models.vault import VaultDB, VaultStatus
from libs.models.processing import ProcessingJobDB, ProcessingStatus
from ..main import celery_app


logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3)
def process_vault(self, vault_id: str) -> Dict[str, Any]:
    """Main task to process a vault."""

    logger.info("Starting vault processing", vault_id=vault_id, task_id=self.request.id)

    try:
        # Update vault status
        with get_db() as db:
            vault = db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()
            if not vault:
                raise ValueError(f"Vault {vault_id} not found")

            vault.status = VaultStatus.PROCESSING  # type: ignore
            db.commit()

            # Create processing job
            job = ProcessingJobDB(
                vault_id=vault.id,
                job_type="vault_processing",
                status=ProcessingStatus.RUNNING,
            )
            db.add(job)
            db.commit()
            job_id = job.id

        # Step 1: Extract files
        self.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": 3, "status": "Extracting files..."},
        )

        file_info = extract_vault_files.delay(vault_id).get()

        # Step 2: Analyze content
        self.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": 3, "status": "Analyzing content..."},
        )

        analysis = analyze_vault_content.delay(vault_id, file_info).get()

        # Step 3: Complete processing
        self.update_state(
            state="PROGRESS", meta={"current": 3, "total": 3, "status": "Finalizing..."}
        )

        # Update vault with results
        with get_db() as db:
            vault = db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()
            vault.status = VaultStatus.COMPLETED  # type: ignore
            vault.file_count = file_info.get("file_count", 0)  # type: ignore
            vault.processed_files = file_info.get("file_count", 0)  # type: ignore

            # Update processing job
            job = db.query(ProcessingJobDB).filter(ProcessingJobDB.id == job_id).first()
            job.status = ProcessingStatus.COMPLETED  # type: ignore
            job.progress = "100%"  # type: ignore
            job.result_data = {  # type: ignore
                "file_info": file_info,
                "analysis": analysis,
            }

            db.commit()

        logger.info("Vault processing completed", vault_id=vault_id)

        return {
            "status": "completed",
            "file_info": file_info,
            "analysis": analysis,
        }

    except Exception as e:
        logger.error("Vault processing failed", vault_id=vault_id, error=str(e))

        # Update vault status to failed
        with get_db() as db:
            vault = db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()
            if vault:
                vault.status = VaultStatus.FAILED
                vault.error_message = str(e)
                db.commit()

        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True)
def extract_vault_files(self, vault_id: str) -> Dict[str, Any]:
    """Extract files from vault ZIP."""

    logger.info("Extracting vault files", vault_id=vault_id)

    try:
        with get_db() as db:
            vault_db = db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()
            if not vault_db:
                raise ValueError(f"Vault {vault_id} not found")

            storage_path = vault_db.storage_path

        # Create extraction directory
        extract_dir = os.path.join(os.path.dirname(storage_path), "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        # Extract ZIP file
        with zipfile.ZipFile(storage_path, "r") as zip_file:
            zip_file.extractall(extract_dir)

            # Get file information
            file_list = zip_file.namelist()

        # Analyze extracted files
        markdown_files = []
        attachment_files = []
        config_files = []

        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extract_dir)

                if file.endswith(".md"):
                    markdown_files.append(relative_path)
                elif file.startswith(".") or ".obsidian" in relative_path:
                    config_files.append(relative_path)
                else:
                    attachment_files.append(relative_path)

        result = {
            "file_count": len(file_list),
            "markdown_files": markdown_files,
            "attachment_files": attachment_files,
            "config_files": config_files,
            "extraction_path": extract_dir,
        }

        logger.info(
            "Vault extraction completed",
            vault_id=vault_id,
            file_count=len(file_list),
            markdown_count=len(markdown_files),
        )

        return result

    except Exception as e:
        logger.error("Vault extraction failed", vault_id=vault_id, error=str(e))
        raise


@celery_app.task(bind=True)
def analyze_vault_content(
    self, vault_id: str, file_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze vault content for insights."""

    logger.info("Analyzing vault content", vault_id=vault_id)

    try:
        extraction_path = file_info["extraction_path"]
        markdown_files = file_info["markdown_files"]

        # Basic analysis
        total_content_length = 0
        note_titles = []

        for md_file in markdown_files:
            file_path = os.path.join(extraction_path, md_file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    total_content_length += len(content)

                    # Extract title (first line or filename)
                    lines = content.split("\n")
                    title = None
                    for line in lines:
                        if line.strip().startswith("# "):
                            title = line.strip()[2:]
                            break

                    if not title:
                        title = os.path.splitext(os.path.basename(md_file))[0]

                    note_titles.append(title)

            except Exception as e:
                logger.warning(
                    "Failed to read markdown file", file_path=file_path, error=str(e)
                )

        # TODO: Add more sophisticated analysis
        # - Extract tags
        # - Analyze links between notes
        # - Generate embeddings
        # - Identify key topics

        result = {
            "total_content_length": total_content_length,
            "note_titles": note_titles,
            "average_note_length": (
                total_content_length / len(markdown_files) if markdown_files else 0
            ),
            "analysis_timestamp": self.request.id,
        }

        logger.info(
            "Vault analysis completed",
            vault_id=vault_id,
            total_length=total_content_length,
            note_count=len(note_titles),
        )

        return result

    except Exception as e:
        logger.error("Vault analysis failed", vault_id=vault_id, error=str(e))
        raise
