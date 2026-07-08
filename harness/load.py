from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from mimetypes import guess_extension
from pathlib import Path, PurePosixPath

from pydantic import Field

from harness.contracts import HarnessModel, path_text, utc_now


class SourcePointer(HarnessModel):
    source_id: str
    source_type: str
    uri: str
    retrieved_at: datetime
    content_type: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class LoadedArtifact(HarnessModel):
    artifact_id: str
    source: SourcePointer
    storage_uri: str
    sha256: str
    bytes: int
    loaded_at: datetime


def load_file(path: Path | str, source_type: str, storage_root: Path | str = "data/lake") -> LoadedArtifact:
    source_path = Path(path)
    payload = source_path.read_bytes()
    digest = sha256(payload).hexdigest()
    key = object_key(source_type, digest, source_path.name)
    destination = Path(storage_root) / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return LoadedArtifact(
        artifact_id=f"art_{digest[:12]}",
        source=SourcePointer(
            source_id=f"src_{sha256(path_text(source_path).encode()).hexdigest()[:12]}",
            source_type=source_type,
            uri=path_text(source_path),
            retrieved_at=utc_now(),
            metadata={"name": source_path.name},
        ),
        storage_uri=f"local://{key}",
        sha256=digest,
        bytes=len(payload),
        loaded_at=utc_now(),
    )


def load_files(paths: dict[str, Path], storage_root: Path | str) -> dict[str, LoadedArtifact]:
    return {name: load_file(path, name, storage_root) for name, path in paths.items() if path.exists()}


def append_manifest(artifacts: dict[str, LoadedArtifact], manifest_path: Path | str = "data/manifest.jsonl") -> None:
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as manifest:
        for name, artifact in artifacts.items():
            row = {"name": name, **artifact.model_dump(mode="json")}
            manifest.write(json.dumps(row, sort_keys=True) + "\n")


def object_key(source_type: str, digest: str, name: str) -> str:
    suffix = PurePosixPath(name).suffix or guess_extension("") or ".bin"
    return f"raw/{safe_segment(source_type)}/{digest[:2]}/{digest}{suffix}"


def safe_segment(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value.lower()).strip("-") or "unknown"
