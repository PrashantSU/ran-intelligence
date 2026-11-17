
"""Download public telecom PDF specifications."""

import hashlib
import json
import urllib.request
from pathlib import Path

ETSI_SOURCES = [
    {
        "document_id": "3gpp-ts-38-211",
        "title": "NR Physical Channels and Modulation",
        "specification": "3GPP TS 38.211",
        "version": "18.8.0",
        "release": "18",
        "url": (
            "https://www.etsi.org/deliver/etsi_TS/"
            "138200_138299/138211/18.08.00_60/"
            "ts_138211v180800p.pdf"
        ),
    },
    {
        "document_id": "3gpp-ts-38-300",
        "title": "NR and NG-RAN Overall Description",
        "specification": "3GPP TS 38.300",
        "version": "17.16.0",
        "release": "17",
        "url": (
            "https://www.etsi.org/deliver/etsi_ts/"
            "138300_138399/138300/17.16.00_60/"
            "ts_138300v171600p.pdf"
        ),
    },
    {
        "document_id": "3gpp-ts-38-331",
        "title": "NR Radio Resource Control Protocol",
        "specification": "3GPP TS 38.331",
        "version": "15.30.0",
        "release": "15",
        "url": (
            "https://www.etsi.org/deliver/etsi_ts/"
            "138300_138399/138331/15.30.00_60/"
            "ts_138331v153000p.pdf"
        ),
    },
]

def download_etsi_documents(
    output_dir: str | Path,
    sources: list[dict] | None = None,
    timeout: int = 60,
    max_size_mb: int = 30,
) -> list[dict]:
    """Download and verify ETSI PDFs, recording their provenance."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sources = sources or ETSI_SOURCES
    manifest = []

    for source in sources:
        filename = f"{source['document_id']}_v{source['version']}.pdf"
        destination = output_dir / filename
        temporary = destination.with_suffix(".pdf.part")

        try:
            request = urllib.request.Request(
                source["url"],
                headers={"User-Agent": "RAN-Intelligence-Research/1.0"},
            )

            with urllib.request.urlopen(
                request, timeout=timeout
            ) as response:
                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                content_length = response.headers.get(
                    "Content-Length"
                )

                if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                    raise ValueError("PDF exceeds configured size limit")

                digest = hashlib.sha256()
                total_size = 0

                with temporary.open("wb") as file:
                    while True:
                        block = response.read(1024 * 1024)

                        if not block:
                            break

                        total_size += len(block)

                        if total_size > max_size_mb * 1024 * 1024:
                            raise ValueError("PDF exceeds configured size limit")

                        if total_size <= 5 and not block.startswith(b"%PDF-"):
                            # PDF signature is checked after download.
                            pass

                        digest.update(block)
                        file.write(block)

            with temporary.open("rb") as file:
                if file.read(5) != b"%PDF-":
                    raise ValueError(
                        f"Response is not a valid PDF (content type: {content_type})"
                    )

            temporary.replace(destination)

            record = {
                **source,
                "filename": filename,
                "local_path": str(destination),
                "size_bytes": total_size,
                "sha256": digest.hexdigest(),
                "status": "downloaded",
            }

            print(
                f"Downloaded: {filename} "
                f"({total_size / 1024 / 1024:.2f} MB)"
            )

        except Exception as exc:
            temporary.unlink(missing_ok=True)

            record = {
                **source,
                "filename": filename,
                "status": "failed",
                "error": str(exc),
            }

            print(f"Failed: {filename} — {exc}")

        manifest.append(record)

    manifest_path = output_dir / "document_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print(f"\nManifest saved: {manifest_path}")
    return manifest
