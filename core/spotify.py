from __future__ import annotations

from html import escape

import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth


SPOTIFY_SCOPE = (
    "user-read-currently-playing "
    "user-read-recently-played "
    "user-read-playback-state "
    "user-modify-playback-state "
    "playlist-read-private "
    "user-top-read"
)


def get_auth_manager():
    if "spotify" not in st.secrets:
        return None

    creds = st.secrets["spotify"]
    return SpotifyOAuth(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        redirect_uri=creds["redirect_uri"],
        scope=SPOTIFY_SCOPE,
        open_browser=False,
    )


def get_spotify_client():
    auth_manager = get_auth_manager()
    if not auth_manager:
        return None, None

    if "spotify_token_info" in st.session_state:
        token_info = st.session_state.spotify_token_info
        if auth_manager.is_token_expired(token_info):
            try:
                token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
                st.session_state.spotify_token_info = token_info
            except Exception:
                del st.session_state.spotify_token_info
                return None, auth_manager.get_authorize_url()
        return spotipy.Spotify(auth=token_info["access_token"]), None

    try:
        code = st.query_params.get("code")
        if code and st.session_state.get("last_processed_code") != code:
            st.session_state.last_processed_code = code
            token_info = auth_manager.get_access_token(code)
            st.session_state.spotify_token_info = token_info
            st.query_params.clear()
            st.rerun()
    except Exception:
        st.query_params.clear()
        st.sidebar.warning("Spotify login needs a fresh retry.")

    return None, auth_manager.get_authorize_url()


def render_spotify_widget():
    st.sidebar.markdown("### Spotify")
    sp, auth_url = get_spotify_client()

    if not sp and not auth_url:
        st.sidebar.caption("Add Spotify secrets to enable music controls.")
        st.sidebar.divider()
        return

    if not sp and auth_url:
        render_login(auth_url)
        st.sidebar.divider()
        return

    try:
        playback = sp.current_playback()
        render_now_playing(sp, playback)
        render_training_music_insights(sp, playback)
    except Exception as exc:
        if "403" in str(exc):
            st.sidebar.warning("Spotify permissions changed. Reconnect to refresh access.")
            if st.sidebar.button("Reconnect Spotify", key="spotify_reconnect"):
                st.session_state.pop("spotify_token_info", None)
                st.rerun()
        else:
            st.sidebar.caption("Spotify is connected, but playback is currently unavailable.")

    st.sidebar.divider()


def render_login(auth_url: str):
    st.sidebar.markdown(
        f"""
        <a href="{auth_url}" target="_self" style="text-decoration:none;">
            <div style="
                background:linear-gradient(135deg,#1DB954,#34d399);
                color:#06111c;
                padding:12px 14px;
                border-radius:12px;
                text-align:center;
                font-weight:800;
                margin-bottom:10px;">
                Connect Spotify
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Connect once to see playback, recent tracks, and workout music cues.")


def render_now_playing(sp, playback):
    if not playback or not playback.get("item"):
        st.sidebar.info("Spotify is idle.")
        if st.sidebar.button("Refresh Spotify", key="spotify_refresh_idle"):
            st.rerun()
        return

    item = playback["item"]
    track_name = escape(item.get("name", "Unknown track"))
    artist_name = escape(item.get("artists", [{}])[0].get("name", "Unknown artist"))
    album_art = item.get("album", {}).get("images", [{}])[0].get("url", "")
    device_name = escape(playback.get("device", {}).get("name", "Unknown device"))
    is_playing = playback.get("is_playing", False)

    st.sidebar.markdown(
        f"""
        <div style="
            background:rgba(21,29,44,.95);
            border:1px solid rgba(148,163,184,.18);
            border-radius:14px;
            padding:12px;
            margin-bottom:10px;">
            <div style="display:flex; gap:10px; align-items:center;">
                <img src="{album_art}" width="54" height="54" style="border-radius:10px; object-fit:cover;">
                <div style="min-width:0;">
                    <div style="font-size:12px; color:#9aa7b8; font-weight:700;">Now playing</div>
                    <div style="font-size:13px; color:#f8fafc; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{track_name}</div>
                    <div style="font-size:11px; color:#34d399; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{artist_name}</div>
                    <div style="font-size:10px; color:#9aa7b8;">{device_name}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.sidebar.columns(3)
    if c1.button("Prev", key="spotify_prev", width="stretch"):
        sp.previous_track()
        st.rerun()
    if c2.button("Pause" if is_playing else "Play", key="spotify_play", width="stretch"):
        if is_playing:
            sp.pause_playback()
        else:
            sp.start_playback()
        st.rerun()
    if c3.button("Next", key="spotify_next", width="stretch"):
        sp.next_track()
        st.rerun()


def render_training_music_insights(sp, playback):
    st.sidebar.markdown("#### Training music")
    render_mood_recommendation(playback)
    render_top_artists(sp)
    render_recent_tracks(sp)


def render_mood_recommendation(playback):
    if playback and playback.get("is_playing"):
        st.sidebar.caption("Current cue: keep this track for steady training intensity.")
    else:
        st.sidebar.caption("Current cue: start an upbeat playlist before your first working set.")


def render_top_artists(sp):
    try:
        top_artists = sp.current_user_top_artists(limit=3, time_range="short_term")
    except spotipy.SpotifyException as exc:
        st.sidebar.caption(f"Top artists unavailable: {exc}")
        return

    artists = top_artists.get("items", []) if top_artists else []
    if not artists:
        return

    st.sidebar.markdown("Top artists")
    for artist in artists:
        name = escape(artist.get("name", "Unknown artist"))
        image = artist.get("images", [{}])[-1].get("url", "")
        st.sidebar.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:8px; margin:6px 0;">
                <img src="{image}" width="28" height="28" style="border-radius:50%; object-fit:cover;">
                <span style="font-size:12px; color:#e5e7eb;">{name}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_recent_tracks(sp):
    try:
        recent = sp.current_user_recently_played(limit=4)
    except spotipy.SpotifyException as exc:
        st.sidebar.caption(f"Recent tracks unavailable: {exc}")
        return

    tracks = recent.get("items", []) if recent else []
    if not tracks:
        return

    st.sidebar.markdown("Recently played")
    for item in tracks:
        track = item.get("track", {})
        name = escape(track.get("name", "Unknown track"))
        artist = escape(track.get("artists", [{}])[0].get("name", "Unknown artist"))
        st.sidebar.markdown(
            f"<div style='font-size:11px; color:#9aa7b8; margin-bottom:4px;'>{name} · {artist}</div>",
            unsafe_allow_html=True,
        )


def search_and_play(query):
    sp, _ = get_spotify_client()
    if not sp or not query:
        return []
    try:
        results = sp.search(q=query, type="track", limit=10)
        return results.get("tracks", {}).get("items", [])
    except spotipy.SpotifyException as exc:
        st.error(f"Search error: {exc}")
        return []


def trigger_playback(track_uri):
    sp, _ = get_spotify_client()
    if not sp:
        return
    try:
        devices = sp.devices().get("devices", [])
        if devices:
            sp.start_playback(device_id=devices[0]["id"], uris=[track_uri])
        else:
            sp.start_playback(uris=[track_uri])
    except spotipy.SpotifyException as exc:
        st.error(f"Playback failed. Open Spotify on your phone first. ({exc})")
