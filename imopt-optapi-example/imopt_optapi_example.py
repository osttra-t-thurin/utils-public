# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests-toolbelt",
#     "tri-api",
# ]
# [[tool.uv.index]]
# name = "artifactory"
# url = "https://artifactory.trioptima.net/artifactory/api/pypi/opt-python-virtual/simple"
# default = true
# ///

# Simple example client to test imopt on OptAPI DEV.
#
# Requirements:
# uv run imopt_optapi_example.py
# or
# pip install tri.api requests-toolbelt
import os
import time
from pathlib import Path
from requests_toolbelt.multipart import decoder
from tri_api import AuthenticatedSession


def write_csv_stream(delimiter: str, parts: dict[str, str | bytes]) -> str:
    """Format multiple CSV parts into a single CSV stream matching C++ writeCSVStream.

    Format:
    <delimiter>
    <delimiter>:<part_name_1>
    <content_1>
    <delimiter>:<part_name_2>
    <content_2>
    ...
    """
    lines = [delimiter]
    for name, content in parts.items():
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        lines.append(f"{delimiter}:{name}")
        cleaned = content.rstrip("\r\n")
        if cleaned:
            lines.append(cleaned)
    lines.append("")
    return "\n".join(lines)


def read_csv_stream(stream_content: str | bytes) -> tuple[str, dict[str, str]]:
    """Parse a CSV stream formatted with writeCSVStream into (delimiter, parts_by_name)."""
    if isinstance(stream_content, bytes):
        stream_content = stream_content.decode("utf-8")
    lines = stream_content.splitlines()
    if not lines:
        return "", {}
    delimiter = lines[0].strip()
    prefix = f"{delimiter}:"
    parts: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    for line in lines[1:]:
        if line.startswith(prefix):
            if current_name is not None:
                parts[current_name] = "\n".join(current_lines)
            current_name = line[len(prefix):].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        parts[current_name] = "\n".join(current_lines)
    return delimiter, parts


def main():
    script_dir = Path(__file__).resolve().parent
    inputs_dir = script_dir / "data"

    sensitivities_path = inputs_dir / "minimal-fx-im-sensitivities.csv"
    trades_path = inputs_dir / "minimal-fx-im-trades.csv"

    if not sensitivities_path.exists() or not trades_path.exists():
        raise FileNotFoundError(f"Missing input files in {inputs_dir}")

    files = {
        "sensitivities": (
            "sensitivities",
            open(sensitivities_path, "rb"),
            "text/csv",
        ),
        "trades": (
            "trades",
            open(trades_path, "rb"),
            "text/csv",
        ),
    }

    OPT_API_CLIENT_ID = "f817cb52-c003-11e9-acd3-54bf649d1d8a"
    OPT_USER_SCOPE = OPT_API_CLIENT_ID + ":optapi_user"
    AUTH_CLIENT_ID = "a2caed62-e28d-11e4-86da-b39459ee2d75"
    AUTH_CLIENT_SECRET = "password"

    # Use auth application to log in since the client id and client secret is fixed for a scratch installation
    session = AuthenticatedSession(
        client_id=AUTH_CLIENT_ID,
        client_secret=AUTH_CLIENT_SECRET,
        username="optapi_example",  # Default test user in DEV
        password="Passw0rd!",
        scope=f"global {OPT_USER_SCOPE}",
        base_url="https://dev.trioptima.net/",
    )

    # Parameters from MinimalFXIMTestOptapi
    params = {
        "minimum-notional": "10000.0",
        "iterations": "100",
        "optimizer": "CMA",
    }

    print("Submitting request to /opt/api/imopt on DEV...")
    t0 = time.time()
    response = session.post("/opt/api/imopt", files=files, params=params, verify=False)
    duration = time.time() - t0
    print(f"Status Code: {response.status_code}")
    print(f"Duration: {duration:.2f}s")
    print(f"Headers: {dict(response.headers)}")

    if response.status_code != 200:
        print("Response Error Body:")
        print(response.text)
        return

    print("\nParsing response multipart parts:")
    multipart_data = decoder.MultipartDecoder.from_response(response)
    for part in multipart_data.parts:
        content_disposition = part.headers.get(b"Content-Disposition", b"").decode("utf-8")
        print(f"\n--- Part: {content_disposition} ---")
        text = part.text
        # Print preview of part text
        lines = text.splitlines()
        if len(lines) > 10:
            print("\n".join(lines[:10]))
            print(f"... [{len(lines) - 10} more lines omitted] ...")
        else:
            print(text)

if __name__ == "__main__":
    main()
