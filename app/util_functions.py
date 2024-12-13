from .models import Songs, Song_Likes, Histories
from sqlalchemy.sql import func
from .dependencies.db import SessionDep
from sqlmodel import select
from fastapi import UploadFile
from mutagen.mp3 import MP3


def calculate_song_popularity(
    session: SessionDep, song: Songs, weight_history=0.5, weight_likes=0.5
):
    """
    Calculate a song's popularity score based on history count and like count.

    Args:
        song (dict): A dictionary with song data containing `history_count` and `like_count`.
        weight_history (float): The weight assigned to history count (default: 0.5).
        weight_likes (float): The weight assigned to like count (default: 0.5).

    Returns:
        float: The popularity score of the song (between 0 and 1).
    """
    total_history = session.exec(select(func.count(Histories.id))).one()
    total_likes = session.exec(select(func.count(Song_Likes.song_id))).one()

    history_count = session.exec(
        select(func.count(Histories.song_id)).where(Histories.song_id == song.id)
    ).one()
    like_count = session.exec(
        select(func.count(Song_Likes.song_id)).where(Song_Likes.song_id == song.id)
    ).one()

    # Normalize the history count and like count
    normalized_history = history_count / total_history if total_history > 0 else 0
    normalized_likes = like_count / total_likes if total_likes > 0 else 0

    # Calculate weighted popularity
    popularity = (normalized_history * weight_history) + (
        normalized_likes * weight_likes
    )

    song.popularity = popularity
    session.add(song)
    session.commit()


def calculate_song_duration(song: UploadFile):
    # Read the file into memory
    file = song.file

    audio = MP3(file)
    duration = int(round(audio.info.length))

    return duration
