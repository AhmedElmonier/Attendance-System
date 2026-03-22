import hashlib
import hmac
import logging
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BackupEngine:
    def __init__(self, db_url: str, storage_path: str, master_key: str):
        self.db_url = db_url
        self.storage_path = Path(storage_path)
        self.master_key = bytes.fromhex(master_key)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> dict:
        backup_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}_{backup_id[:8]}"
        raw_path = self.storage_path / f"{filename}.sql.gz.enc"

        try:
            result = subprocess.run(
                [
                    "pg_dump",
                    self.db_url,
                    "--no-owner",
                    "--no-privileges",
                ],
                capture_output=True,
                check=True,
            )

            compressed = self._gzip_compress(result.stdout)
            encrypted = self._encrypt_aes_gcm(compressed)

            with open(raw_path, "wb") as f:
                f.write(encrypted)

            checksum = hashlib.sha256(encrypted).hexdigest()
            file_size = raw_path.stat().st_size

            logger.info(
                f"Backup created: {raw_path} ({file_size} bytes, sha256={checksum})"
            )

            return {
                "backup_id": backup_id,
                "artifact_path": str(raw_path),
                "checksum": checksum,
                "encryption_version": "1.0-aes-256-gcm",
                "size_bytes": file_size,
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e.stderr.decode()}")
            raise RuntimeError(f"Backup failed: pg_dump error") from e
        except Exception as e:
            logger.exception("Backup creation failed")
            raise

    def verify_backup_integrity(
        self, artifact_path: str, expected_checksum: str
    ) -> bool:
        with open(artifact_path, "rb") as f:
            data = f.read()

        actual = hashlib.sha256(data).hexdigest()
        return hmac.compare_digest(actual, expected_checksum)

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
        aesgcm = AESGCM(self.master_key[:32])
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt_aes_gcm(self, data: bytes) -> bytes:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(self.master_key[:32])
        return aesgcm.decrypt(nonce, ciphertext, None)
