import time
import requests
import json
import asyncio
from ollama import chat
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from webless import search_sync


MODEL = "qwen3:1.7b"

def verify_finding(source: str, finding: str, evidence: str) -> dict:
    """
    Verifies if the evidence actually supports the finding.
    """
    print(f"\n[Verifier] Checking: '{finding}'")
    system_prompt = (
        "You are an evidence verification assistant. "
        "Determine whether the supplied evidence supports the supplied finding. "
        "Return JSON with exactly two fields: 'supported' (boolean) and 'explanation' (string)."
    )
    
    user_prompt = f"""
    Source: {source}
    Finding: {finding}
    Evidence: {evidence}
    """

    response = chat(
        model="qwen3:4b", # Aapka model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        format="json" # force ollama give me output in JSON format
    )
    try:
        # JSON string to convert in dictionary
        result = json.loads(response.message.content)
    except json.JSONDecodeError:
        result = {"supported": False, "explanation": "Failed to parse JSON"}
    if result.get("supported") is True:
        print(f"✅ Supported. Marking as verified.")
        mark_note_verified(source, finding)
    else:
        print(f"❌Not supported: {result.get('explanation')}")
        
    return result


research_notes = []
def add_research_note(source: str, finding: str, evidence: str) -> dict:
    """
    Adds a structured research finding to the notes.
    Use this tool to save important information you find on the web.
    
    Args:
        source: The URL or name of the website.
        finding: The key important point (summary).
        evidence: The exact quote or supporting text from the page.
        
    Returns:
        A confirmation dictionary.
    """
    note = {
        "source": source,
        "finding": finding,
        "evidence": evidence,
        "verified": False
    }
    
    research_notes.append(note)
    print(f"\n[Note Saved] {finding}")
    
    return {
        "status": "stored",
        "verified": False,
        "finding": finding
    }

def mark_note_verified(source: str, finding: str) -> dict:
    """
    Marks a matching research note as verified.
    """
    for note in research_notes:
        if note["source"] == source and note["finding"] == finding:
            note["verified"] = True
            print(f"\n[Note Verified] {finding}")
            return {"status": "verified", "finding": finding}
            
    return {"status": "not found", "finding": finding}

def get_verified_research_notes() -> list:
    """
    Returns ONLY the verified research notes for final report generation.
    """
    verified_notes = []
    for note in research_notes:
        if note["verified"] == True:
            verified_notes.append(note.copy())
    return verified_notes


def get_research_notes() -> list:
    """
    Returns all research notes collected so far in this session.
    Use this tool to review all findings before writing the final report.
    """
    notes = []
    for note in research_notes:
        notes.append(note.copy())
    return notes

async def search_web(query, max_results=5):
        # YEH LINE SABSE ZAROORI HAI
    try:
        max_results = int(max_results)
    except:
        max_results = 5
    
    try:
        # webless ka search function
        result = await asyncio.to_thread(search_sync, query, limit=max_results)
        
        results = []
        for hit in result:
            results.append({
                "title": hit.title,
                "url": hit.url,
                "snippet": hit.snippet
            })
        return results
    except Exception as e:
        print(f"[webless error] {e}")
        return []

def read_webpage(url):
    """
    Download a webpage and extract its text.

    Args:
        url: Webpage URL.

    Returns:
        Extracted webpage text.
    """


    if url.startswith("//"):
        url = "https:" + url

    # Extract the real URL from 
    #  DuckDuckGo redirect URL
    parsed_url = urlparse(url)

    if "duckduckgo.com" in parsed_url.netloc:
        params = parse_qs(parsed_url.query)

        if "uddg" in params:
            url = params["uddg"][0]
    response = requests.get(
        url,
        headers = {
                # Real browser jaisa user-agent
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for element in soup(
        ["script", "style", "noscript"]
    ):
        element.decompose()

    text = soup.get_text(
        "\n",
        strip=True
    )

    return text[:12000]
