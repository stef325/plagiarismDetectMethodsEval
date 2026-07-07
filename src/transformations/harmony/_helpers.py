"""Utilitários internos para transformações harmônicas."""

from __future__ import annotations

import re
from typing import Final


NOTE_TO_SEMITONE: Final[dict[str, int]] = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

SEMITONE_TO_NOTE: Final[tuple[str, ...]] = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)

ROOT_TOKEN_PATTERN = re.compile(
    r"^(?P<note>[A-G](?:#|b)?)(?P<octave>-?\d+)?(?P<suffix>.*)$"
)


def transpose_chord_label(chord: str, semitones: int) -> str:
    """Transpõe um acorde textual preservando sua estrutura básica."""

    if "-" in chord:
        return "-".join(transpose_note_token(token, semitones) for token in chord.split("-"))
    return transpose_note_token(chord, semitones)


def transpose_note_token(token: str, semitones: int) -> str:
    """Transpõe um token textual de nota ou acorde."""

    match = ROOT_TOKEN_PATTERN.match(token)
    if match is None:
        return token

    note = match.group("note")
    octave = match.group("octave")
    suffix = match.group("suffix")

    if note not in NOTE_TO_SEMITONE:
        return token

    if octave is None:
        transposed_note = _transpose_pitch_class(note, semitones)
        return f"{transposed_note}{suffix}"

    pitch = NOTE_TO_SEMITONE[note] + (int(octave) + 1) * 12
    transposed_pitch = pitch + semitones
    transposed_note = SEMITONE_TO_NOTE[transposed_pitch % 12]
    transposed_octave = (transposed_pitch // 12) - 1
    return f"{transposed_note}{transposed_octave}{suffix}"


def simplify_chord_label(chord: str) -> str:
    """Simplifica um acorde textual removendo extensões e tensões."""

    if "-" in chord:
        return chord.split("-")[0]

    match = ROOT_TOKEN_PATTERN.match(chord)
    if match is None:
        return chord

    note = match.group("note")
    octave = match.group("octave") or ""
    suffix = match.group("suffix").lower()

    if "dim" in suffix:
        return f"{note}{octave}dim"
    if "aug" in suffix:
        return f"{note}{octave}aug"
    if suffix.startswith("m") and not suffix.startswith("maj"):
        return f"{note}{octave}m"
    return f"{note}{octave}"


def _transpose_pitch_class(note: str, semitones: int) -> str:
    """Transpõe uma classe de altura sem alterar a oitava."""

    semitone = NOTE_TO_SEMITONE[note]
    return SEMITONE_TO_NOTE[(semitone + semitones) % 12]