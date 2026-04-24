"""
# --------------------------------------------------------------------------------
# MODULE: core/spotify.py (ELITE AUTH & INSIGHTS)
# --------------------------------------------------------------------------------
# // WHAT IT DOES: 
# Handles Spotify OAuth2, playback controls, and allowed user insights 
# (Top Artists & Device Info) after the Nov 2024 policy changes.
# --------------------------------------------------------------------------------
"""
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time

def get_auth_manager():
    """Builds the OAuth manager using your stored secrets."""
    if "spotify" not in st.secrets:
        return None
    creds = st.secrets["spotify"]
    # We include 'user-top-read' to show the user's favorite artists
    return SpotifyOAuth(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        redirect_uri=creds["redirect_uri"],
        scope="user-read-currently-playing,user-read-recently-played,user-read-playback-state,user-modify-playback-state,playlist-read-private,user-top-read",
        open_browser=False
    )

def get_spotify_client():
    """Returns a valid spotipy.Spotify client if authenticated, else (None, auth_url)."""
    if "spotify_token_info" in st.session_state:
        token_info = st.session_state.spotify_token_info
        auth_manager = get_auth_manager()
        if auth_manager.is_token_expired(token_info):
            try:
                token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                st.session_state.spotify_token_info = token_info
            except:
                del st.session_state.spotify_token_info
                return None, auth_manager.get_authorize_url()
        return spotipy.Spotify(auth=token_info['access_token']), None

    auth_manager = get_auth_manager()
    if not auth_manager: return None, None

    # --- TOKEN EXCHANGE LOGIC ---
    try:
        # Check if we have a 'code' in the URL (the return from Spotify)
        code = st.query_params.get("code")
        
        # ELITE TIP: Streamlit often runs scripts twice. We use a session 'lock'
        # to ensure we only try to exchange a code ONCE.
        if code and st.session_state.get("last_processed_code") != code:
            st.session_state.last_processed_code = code # Lock it
            
            with st.sidebar.status("Establishing Secure Handshake...", expanded=False) as status:
                token_info = auth_manager.get_access_token(code)
                st.session_state.spotify_token_info = token_info
                status.update(label="Sync Established!", state="complete")
            
            # Clear params so refreshing the browser doesn't try to reuse the code
            st.query_params.clear()
            st.rerun()
    except Exception as e:
        # If the code was already used or failed, we must clear it to stop the loop
        st.query_params.clear()
        if "already used" in str(e).lower():
            st.sidebar.warning("Auth sync overlapped. Trying again...")
            st.rerun()
        else:
            st.sidebar.error("Handshake Link Failed. Please try again.")
            st.sidebar.caption(f"Error Code: {type(e).__name__}")
        
    return None, auth_manager.get_authorize_url()

def render_spotify_widget():
    """Renders the Spotify 'Elite' widget in the sidebar."""
    st.sidebar.markdown("### 🎧 Spotify Elite Sync")
    
    sp, auth_url = get_spotify_client()
    
    if not sp and auth_url:
        st.sidebar.markdown(
            f'<a href="{auth_url}" target="_self">'
            f'<button class="stButton" style="background-color:#1DB954; color:white; border:none; padding:12px 20px; border-radius:30px; cursor:pointer; font-weight:bold; width:100%;">'
            f'Establish Secure Sync</button></a>', 
            unsafe_allow_html=True
        )
        return

    try:
        # 1. GET CURRENT PLAYBACK & DEVICE
        playback = sp.current_playback()
        device_name = playback['device']['name'] if playback and 'device' in playback else None
        is_playing = playback['is_playing'] if playback else False
        
        if playback and playback.get("item"):
            item = playback["item"]
            track_name = item["name"]
            artist_name = item["artists"][0]["name"]
            album_art = item["album"]["images"][0]["url"] if item["album"]["images"] else ""
            
            # --- Now Playing Card ---
            st.sidebar.markdown(f"""
            <div class="glass-card" style="padding: 15px; display: flex; align-items: center; gap: 12px; margin-bottom: 5px;">
                <img src="{album_art}" width="50" style="border-radius: 8px;">
                <div style="overflow: hidden; flex: 1;">
                    <p style="margin: 0; font-size: 13px; font-weight: 700; color: white; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{track_name}</p>
                    <p style="margin: 0; font-size: 11px; color: #1DB954; font-weight: 600;">{artist_name}</p>
                    <p style="margin: 0; font-size: 9px; color: #9ca3af;">📱 {device_name if device_name else 'Unknown Device'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Controls ---
            c1, c2, c3 = st.sidebar.columns(3)
            if c1.button("⏮️", key="elite_prev"): sp.previous_track(); st.rerun()
            if c2.button("⏸️" if is_playing else "▶️", key="elite_play"): 
                if is_playing: sp.pause_playback()
                else: sp.start_playback()
                st.rerun()
            if c3.button("⏭️", key="elite_next"): sp.next_track(); st.rerun()

            # --- Elite Insights: Top Artists ---
            st.sidebar.markdown("---")
            render_top_artists(sp)
            render_recent_tracks(sp)
        else:
            st.sidebar.info("⏸️ Spotify is idle.")
            if st.sidebar.button("↻ Refresh Sync"): st.rerun()
            render_top_artists(sp)

    except Exception as e:
        if "403" in str(e):
            st.sidebar.error("⚠️ Scope Change detected. Re-login required for Elite Features.")
            if st.sidebar.button("Delete Cache & Re-auth"):
                if "spotify_token_info" in st.session_state: del st.session_state.spotify_token_info
                st.rerun()
        else:
            st.sidebar.caption("Syncing with satellite...")

def render_top_artists(sp):
    """Renders the user's top 3 training artists."""
    try:
        top_artists = sp.current_user_top_artists(limit=3, time_range='short_term')
        if top_artists and "items" in top_artists:
            st.sidebar.markdown("#### 🏆 Top Workout Artists")
            for artist in top_artists["items"]:
                name = artist["name"]
                img = artist["images"][-1]["url"] if artist["images"] else ""
                st.sidebar.markdown(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <img src="{img}" width="24" style="border-radius: 50%;">
                    <span style="font-size: 11px; color: #f3f4f6;">{name}</span>
                </div>
                """, unsafe_allow_html=True)
    except spotipy.SpotifyException as e:
        st.sidebar.caption(f"Spotify error loading artists: {e}")

def render_recent_tracks(sp):
    """Renders the last 3 tracks played."""
    try:
        recent = sp.current_user_recently_played(limit=3)
        if recent and "items" in recent:
            st.sidebar.markdown("---")
            st.sidebar.markdown("#### 🕒 Recently Crushed")
            for item in recent["items"]:
                track = item["track"]
                st.sidebar.markdown(f"""<div style="font-size: 10px; color: #9ca3af; margin-bottom: 2px;">• {track['name']}</div>""", unsafe_allow_html=True)
    except spotipy.SpotifyException as e:
        st.sidebar.caption(f"Spotify error loading tracks: {e}")

def search_and_play(query):
    """Searches Spotify for tracks."""
    sp, _ = get_spotify_client()
    if not sp or not query: return []
    try:
        results = sp.search(q=query, type="track", limit=10)
        return results.get("tracks", {}).get("items", [])
    except spotipy.SpotifyException as e:
        st.error(f"Search error: {e}")
        return []

def trigger_playback(track_uri):
    """Fires a track URI to the active device."""
    sp, _ = get_spotify_client()
    if not sp: return
    try:
        devices = sp.devices().get("devices", [])
        if devices: sp.start_playback(device_id=devices[0]["id"], uris=[track_uri])
        else: sp.start_playback(uris=[track_uri])
    except spotipy.SpotifyException as e:
        st.error(f"❌ Link failed. Open Spotify on your phone first! ({e})")
