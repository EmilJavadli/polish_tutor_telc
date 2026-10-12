"""Reusable clickable Polish-character keyboard for Streamlit text widgets."""
from __future__ import annotations
import streamlit as st

LOWER = ("ą", "ć", "ę", "ł", "ń", "ó", "ś", "ź", "ż")
UPPER = tuple(letter.upper() for letter in LOWER)


def _append_character(target_key: str, character: str) -> None:
    """Append a character before the target widget is instantiated on the rerun."""
    current = st.session_state.get(target_key, "")
    st.session_state[target_key] = f"{current}{character}"


def render_polish_keyboard(
    target_key: str,
    *,
    keyboard_key: str | None = None,
    show_uppercase: bool = False,
    compact: bool = True,
) -> None:
    """Render clickable Polish letters that append to a Streamlit text widget.

    Place this function BEFORE the text_input/text_area/chat_input using target_key.
    The target value survives the fragment rerun and the clicked character appears
    immediately in the input.
    """
    keyboard_key = keyboard_key or f"plkbd_{target_key}"
    rows = [("", LOWER)]
    if show_uppercase:
        rows.append(("Uppercase", UPPER))

    if not compact:
        st.caption("🇵🇱 Polish keyboard")

    for row_number, (_, letters) in enumerate(rows):
        columns = st.columns(len(letters), gap="small")
        for index, (column, letter) in enumerate(zip(columns, letters)):
            with column:
                st.button(
                    letter,
                    key=f"{keyboard_key}_{row_number}_{index}",
                    on_click=_append_character,
                    args=(target_key, letter),
                    use_container_width=True,
                )
