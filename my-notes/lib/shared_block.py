"""Slice the sentinel-delimited block out of a source file.

`corrections.py` is the only hand-maintained copy of the drawdown algorithm, but two
consumers cannot import it — the notebook because Colab fetches a single `.ipynb`,
and the Databricks cross-check because bundle `src/*.py` upload as notebook objects.
Both therefore carry the text. This is how it gets sliced out: once by
`tools/build_homework1.py` at build time, and once by `tests/test_no_drift.py` to
prove the carried copies have not drifted.
"""

BEGIN = "# --- BEGIN SHARED:"
END = "# --- END SHARED ---"


def extract_shared_block(text: str, name: str) -> str:
    """Return the lines between `BEGIN SHARED: <name>` and `END SHARED`, exclusive.

    Raises rather than returning empty if the sentinels are missing or out of order —
    a silent empty string here would produce a notebook whose Q3 cell has no function
    in it, and the failure would surface much later as a NameError.
    """
    marker = f"{BEGIN} {name} ---"
    lines = text.splitlines()

    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == marker)
    except StopIteration:
        raise ValueError(f"missing sentinel {marker!r}") from None
    try:
        stop = next(i for i, ln in enumerate(lines[start + 1:], start + 1)
                    if ln.strip() == END)
    except StopIteration:
        raise ValueError(f"{marker!r} is never closed by {END!r}") from None

    block = "\n".join(lines[start + 1:stop]).strip("\n")
    if not block.strip():
        raise ValueError(f"block {name!r} is empty")
    return block


def wrap_shared_block(block: str, name: str, origin: str) -> str:
    """Re-attach the sentinels, so a carried copy is extractable in its turn.

    `origin` becomes a provenance comment placed *outside* the sentinels, where it
    cannot affect an exact comparison of the block itself.
    """
    return (f"# Spliced from {origin} — edit there, not here.\n"
            f"{BEGIN} {name} ---\n{block}\n{END}")
