import logging
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class BackupEngine:
    def __init__(self, db_url: str, storage_path: str, master_key: str):
        self.db_url = db_url
        self.storage_path = Path(storage_path)
        try:
            key_bytes = bytes.fromhex(master_key)
        except ValueError as e:
            raise ValueError(f"MASTER_BACKUP_KEY is not valid hex: {e}") from e
        if len(key_bytes) != 32:
            raise ValueError(
                f"MASTER_BACKUP_KEY must be exactly 32 bytes, got {len(key_bytes)}"
            )
        self.master_key = key_bytes
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> dict:
        pg_dump = shutil.which("pg_dump")
        if not pg_dump:
            raise RuntimeError("pg_dump not found in PATH")

        backup_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}_{backup_id[:8]}"
        raw_path = self.storage_path / f"{filename}.sql.gz.enc"

        try:
            result = subprocess.run(
                [pg_dump, "-d", self.db_url, "--no-owner", "--no-privileges"],
                capture_output=True,
                check=True,
                timeout=120,
            )

            compressed = self._gzip_compress(result.stdout)
            encrypted = self._encrypt_aes_gcm(compressed)

            with open(raw_path, "wb") as f:
                f.write(encrypted)

            file_size = raw_path.stat().st_size

            logger.info(f"Backup created: {raw_path} ({file_size} bytes)")

            return {
                "backup_id": backup_id,
                "artifact_path": str(raw_path),
                "encryption_version": "1.0-aes-256-gcm",
                "size_bytes": file_size,
            }

        except subprocess.TimeoutExpired:
            logger.error("pg_dump timed out after 120 seconds")
            raise RuntimeError("Backup timed out")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"pg_dump failed: {e.stderr.decode() if e.stderr else 'unknown'}"
            )
            raise RuntimeError("Backup failed: pg_dump error") from e
        except Exception:
            logger.exception("Backup creation failed")
            raise

    def verify_backup_integrity(self, artifact_path: str) -> bool:
        try:
            with open(artifact_path, "rb") as f:
                data = f.read()
            self._decrypt_aes_gcm(data)
            return True
        except Exception as e:
            logger.warning(f"Backup integrity check failed: {e}")
            return False

    def _gzip_compress(self, data: bytes) -> bytes:
        import gzip
        from io import BytesIO

        buf = BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as f:
            f.write(data)
        return buf.getvalue()

    def _encrypt_aes_gcm(self, data: bytes) -> bytes:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = os.urandom(12)
        aesgcm = AESGCM(self.master_key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt_aes_gcm(self, data: bytes) -> bytes:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(self.master_key)
        return aesgcm.decrypt(nonce, ciphertext, None)
