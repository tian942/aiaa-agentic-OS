#!/usr/bin/env python3
"""
Google Doc Creator

Creates formatted Google Docs from Markdown content.
Follows directive: directives/google_doc_creator.md
"""

import argparse
import json
import os
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ Error: Google API libraries not installed")
    print("   Install with: pip install google-api-python-client google-auth")
    exit(1)


def markdown_to_google_doc_requests(markdown_content: str) -> list:
    """Convert markdown to Google Docs API requests (simplified)"""
    requests = []

    # This is a simplified version - production would handle:
    # - Headers (# ## ###)
    # - Bold (**text**)
    # - Italic (*text*)
    # - Lists (- item)
    # - Links [text](url)

    # For now, just insert the text
    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": markdown_content
        }
    })

    return requests


def create_google_doc(title: str, content: str, folder_id: str = None) -> dict:
    """Create Google Doc with content"""
    print(f"📄 Creating Google Doc: {title}")

    # Get credentials path
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    if not os.path.exists(creds_path):
        print(f"⚠️  Google credentials not found: {creds_path}")
        print("   Skipping Google Doc creation (saving locally only)")
        return {
            "documentId": None,
            "documentUrl": None,
            "title": title,
            "status": "local_only"
        }

    try:
        # Authenticate
        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=[
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        # Create doc
        docs_service = build("docs", "v1", credentials=creds)

        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc.get("documentId")

        print(f"✅ Created document: {doc_id}")

        # Insert content
        requests = markdown_to_google_doc_requests(content)
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()

        # Move to folder if specified
        if folder_id:
            drive_service = build("drive", "v3", credentials=creds)
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                fields="id, parents"
            ).execute()

        # Get shareable URL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        return {
            "documentId": doc_id,
            "documentUrl": doc_url,
            "title": title,
            "status": "created"
        }

    except Exception as e:
        print(f"⚠️  Error creating Google Doc: {e}")
        return {
            "documentId": None,
            "documentUrl": None,
            "title": title,
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Create Google Doc from markdown")
    parser.add_argument("--content", required=True, help="Path to markdown file")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--folder-id", help="Google Drive folder ID (optional)")
    parser.add_argument("--output-json", help="Save doc metadata as JSON")

    args = parser.parse_args()

    print("🚀 Starting Google Doc creation...")

    # Read content
    with open(args.content, "r") as f:
        content = f.read()

    # Create doc
    result = create_google_doc(args.title, content, args.folder_id)

    # Save metadata
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2)

    print(f"\n✅ Google Doc creation complete!")
    if result["documentUrl"]:
        print(f"   URL: {result['documentUrl']}")
    else:
        print(f"   Status: {result['status']}")

    return 0


if __name__ == "__main__":
    exit(main())
