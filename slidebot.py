#!env python3
import re
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Check if presentation_id or URL is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python get-google-slides-links.py presentation_id_or_url")
    sys.exit(1)

# Detect if input is a Google Slides URL and extract presentation_id
input_value = sys.argv[1]
presentation_id_pattern = r"([a-zA-Z0-9-_]{25,})"
match = re.search(presentation_id_pattern, input_value)
if match:
    presentation_id = match.group(1)
else:
    print("Invalid presentation_id or URL.")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

try:
    service = build("slides", "v1", credentials=creds)
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get("slides")

    # Iterate through elements of each slide and extract hyperlinks
    hyperlinks = []
    slide_number = 1
    for slide in slides:
        for element in slide.get("pageElements", []):
            shape = element.get("shape")
            if shape is not None:
                text_elements = shape.get("text", {}).get("textElements", [])

                for text_element in text_elements:
                    text_run = text_element.get("textRun")
                    if text_run:
                        link = text_run.get("style", {}).get("link", {}).get("url")
                        link_text = text_run.get("content")
                        if link:
                            hyperlinks.append((slide_number, link_text, link))
        slide_number += 1

    # Store or display the extracted hyperlinks
    for slide_number, link_text, link in hyperlinks:
        print(f"{slide_number}: [{link_text}]({link})")

except HttpError as error:
    print(f"An error occurred: {error}")
