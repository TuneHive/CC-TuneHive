from fastapi import APIRouter, HTTPException
from sqlmodel import select
import os

from ..models import Songs, Histories
from ..dependencies.auth import CurrentUser
from ..dependencies.db import SessionDep
from ..response_models import SongPublic
from ..ml.ml_models.models import load_model, load_encoder, predict

router = APIRouter(prefix="/songs", tags=["songs"])


# Get the path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the ml folder
ml_folder = os.path.join(current_dir, "..", "ml")


genre_encoder = load_encoder(
    os.path.join(ml_folder, "exported_models", "genre_encoder.pkl")
)
song_encoder = load_encoder(
    os.path.join(ml_folder, "exported_models", "song_encoder.pkl")
)

model = load_model(os.path.join(ml_folder, "exported_models", "gru4rec_model.keras"))


@router.get("/recommendations", response_model=list[SongPublic])
async def get_recommendations(current_user: CurrentUser, session: SessionDep):
    histories = session.exec(
        select(Histories).where(Histories.user_id == current_user.id).limit(10)
    ).all()

    # List of song IDs based on histories
    song_id_sequence = [
        history.song.ml_id for history in histories if history.song.ml_id is not None
    ]

    # List of genres based on histories
    genre_id_sequence = [history.song.genre.split(", ") for history in histories]

    # Encode the song ID sequence
    try:
        encoded_song_id_sequence = song_encoder.transform(song_id_sequence)
    except Exception as e:
        return HTTPException(
            status_code=400, detail=f"Failed to encode song ID sequence: {str(e)}"
        )

    encoded_genre_sequence = []
    try:
        for genre in genre_id_sequence:
            # print(genre)
            encoded_genre_sequence.append(genre_encoder.transform(genre))
    except Exception as e:
        return HTTPException(
            status_code=400,
            detail=f"Failed to encode genre sequence: {str(e)}",
        )

    # Predict
    try:
        predicted_sequence = predict(
            model, encoded_song_id_sequence, encoded_genre_sequence, 10
        )

        # inverse transform the sequence
        predicted_sequence = song_encoder.inverse_transform(predicted_sequence)
        print("predicted", predicted_sequence)
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )

    # Return results
    songs: list[Songs] = []

    for ml_id in predicted_sequence:
        song = session.exec(select(Songs).where(Songs.ml_id == ml_id)).one()
        songs.append(song)

    return songs
