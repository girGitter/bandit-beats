"""
spotify.py — Spotify Web API helper using Client Credentials flow.

This module handles:
  1. Authentication (Client Credentials — no user login required)
  2. Track search by query string
  3. Extracting useful metadata (track ID, preview URL, album art, etc.)

Docs: https://developer.spotify.com/documentation/web-api
"""

import os
import base64
import json
import time
import urllib.request
import urllib.parse
from typing import Optional


# ---------------------------------------------------------------------------
# Credentials — set via environment variables or .env file
# ---------------------------------------------------------------------------
SPOTIFY_CLIENT_ID: str = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET: str = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

# Cache the access token so we don't re-auth on every request
_token_cache: dict = {"access_token": "", "expires_at": 0}

# ---------------------------------------------------------------------------
# Auth — Client Credentials Flow
# ---------------------------------------------------------------------------
# How it works:
#   - We send our Client ID + Secret to Spotify's /api/token endpoint
#   - Spotify returns an access token valid for 1 hour
#   - We use this token in the Authorization header for all API calls
#   - No user login needed — this gives access to public Spotify data
# ---------------------------------------------------------------------------

def _get_access_token() -> str:
    """
    Get a valid Spotify access token using Client Credentials flow.
    
    The Client Credentials flow is the simplest OAuth flow — it's used when
    you need to access public Spotify data (search, track info, etc.) without
    acting on behalf of a specific user.
    
    Steps:
      1. Base64-encode "client_id:client_secret"
      2. POST to https://accounts.spotify.com/api/token with grant_type=client_credentials
      3. Spotify returns { access_token, token_type, expires_in }
    """
    global _token_cache

    # Return cached token if still valid (with 60s buffer)
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise ValueError(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set. "
            "Get them from https://developer.spotify.com/dashboard"
        )

    # Step 1: Encode credentials as Base64 (required by Spotify's token endpoint)
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    # Step 2: Request an access token
    token_url = "https://accounts.spotify.com/api/token"
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()

    req = urllib.request.Request(
        token_url,
        data=data,
        headers={
            "Authorization": f"Basic {b64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())

    # Step 3: Cache the token
    _token_cache = {
        "access_token": result["access_token"],
        "expires_at": time.time() + result["expires_in"],
    }

    print(f"[Spotify] Authenticated successfully, token expires in {result['expires_in']}s")
    return _token_cache["access_token"]


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _spotify_get(endpoint: str, params: Optional[dict] = None) -> dict:
    """Make an authenticated GET request to the Spotify Web API."""
    token = _get_access_token()
    base_url = "https://api.spotify.com/v1"

    url = f"{base_url}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


# ---------------------------------------------------------------------------
# Search for a track
# ---------------------------------------------------------------------------

def search_track(query: str, limit: int = 1) -> Optional[dict]:
    """
    Search Spotify for a track and return structured metadata.
    
    Args:
        query: Search string, e.g. "Blinding Lights The Weeknd"
        limit: Max results (default 1)
    
    Returns:
        Dict with track metadata, or None if not found.
        
    Example return:
        {
            "spotify_id": "0VjIjW4GlUZAMYd2vXMi4e",
            "spotify_uri": "spotify:track:0VjIjW4GlUZAMYd2vXMi4e",
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "album": "After Hours",
            "album_art": "https://i.scdn.co/image/...",
            "preview_url": "https://p.scdn.co/mp3-preview/...",
            "duration_ms": 200040,
            "external_url": "https://open.spotify.com/track/..."
        }
    """
    try:
        result = _spotify_get("search", {"q": query, "type": "track", "limit": limit})
        tracks = result.get("tracks", {}).get("items", [])

        if not tracks:
            print(f"[Spotify] No results for: {query}")
            return None

        track = tracks[0]

        # Extract the largest album art image
        images = track.get("album", {}).get("images", [])
        album_art = images[0]["url"] if images else ""

        return {
            "spotify_id": track["id"],
            "spotify_uri": track["uri"],
            "title": track["name"],
            "artist": ", ".join(a["name"] for a in track.get("artists", [])),
            "album": track.get("album", {}).get("name", ""),
            "album_art": album_art,
            "preview_url": track.get("preview_url", ""),
            "duration_ms": track.get("duration_ms", 0),
            "external_url": track.get("external_urls", {}).get("spotify", ""),
        }

    except Exception as e:
        print(f"[Spotify] Error searching '{query}': {e}")
        return None


def get_track(track_id: str) -> Optional[dict]:
    """
    Get metadata for a specific Spotify track by ID.
    
    Args:
        track_id: Spotify track ID (e.g. "0VjIjW4GlUZAMYd2vXMi4e")
    """
    try:
        track = _spotify_get(f"tracks/{track_id}")

        images = track.get("album", {}).get("images", [])
        album_art = images[0]["url"] if images else ""

        return {
            "spotify_id": track["id"],
            "spotify_uri": track["uri"],
            "title": track["name"],
            "artist": ", ".join(a["name"] for a in track.get("artists", [])),
            "album": track.get("album", {}).get("name", ""),
            "album_art": album_art,
            "preview_url": track.get("preview_url", ""),
            "duration_ms": track.get("duration_ms", 0),
            "external_url": track.get("external_urls", {}).get("spotify", ""),
        }
    except Exception as e:
        print(f"[Spotify] Error getting track {track_id}: {e}")
        return None


# ---------------------------------------------------------------------------
# Embed URL builder
# ---------------------------------------------------------------------------

def get_embed_url(spotify_id: str) -> str:
    """
    Build the Spotify Embed (iframe) URL for a track.
    
    This URL can be loaded in an <iframe> to show Spotify's built-in player.
    Users logged into Spotify can play the full song; others get a 30s preview.
    
    Args:
        spotify_id: Spotify track ID
        
    Returns:
        Embed URL like "https://open.spotify.com/embed/track/0VjIjW4GlUZAMYd2vXMi4e"
    """
    return f"https://open.spotify.com/embed/track/{spotify_id}?utm_source=generator&theme=0"
