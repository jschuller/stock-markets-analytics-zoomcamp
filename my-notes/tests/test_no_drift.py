"""The carried copies of `find_corrections` must match the canonical one.

`my-notes/lib/corrections.py` is the only hand-maintained copy, but two consumers
cannot import it — the notebook because Colab fetches a single `.ipynb` and nothing
else, the Databricks cross-check because bundle `src/*.py` upload as notebook objects
with the extension stripped. Both therefore carry the text verbatim.

That is fine as long as something notices when they diverge. Before these tests, they
already had: the cross-check's copy had quietly lost the `peak` and `trough` columns
and returned `Timestamp` where the notebook returned `date`. Nothing caught it,
because nothing compared them.

If one of these fails: edit `my-notes/lib/corrections.py`, run
`python my-notes/tools/build_homework1.py` to refresh the notebook, and paste the
block into `06_crosscheck_bronze.py`.
"""

import json

import pytest

from shared_block import extract_shared_block

NAME = "find_corrections"

CROSSCHECK = "my-notes/databricks/bundle/src/06_crosscheck_bronze.py"
NOTEBOOK = "my-notes/01-intro/homework1.ipynb"


@pytest.fixture(scope="module")
def canonical(repo_root):
    return extract_shared_block(
        (repo_root / "my-notes" / "lib" / "corrections.py").read_text(), NAME)


def test_crosscheck_copy_matches_canonical(repo_root, canonical):
    """The Databricks cross-check must run the same algorithm it is checking.

    This is what makes crosscheck_bronze meaningful: it re-answers Q3 from Delta
    rather than from live yfinance, which validates the *data*. It can only do that
    honestly if its algorithm is the one under test here.
    """
    carried = extract_shared_block((repo_root / CROSSCHECK).read_text(), NAME)
    assert carried == canonical


def test_notebook_copy_matches_canonical(repo_root, canonical):
    """The generated notebook must carry the current block.

    Fails when someone edits corrections.py and forgets to re-run the builder, which
    would otherwise ship a notebook running last week's algorithm.
    """
    nb = json.loads((repo_root / NOTEBOOK).read_text())
    sources = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    holding = [s for s in sources if NAME in s and "BEGIN SHARED" in s]

    assert len(holding) == 1, f"expected exactly one cell carrying {NAME}, got {len(holding)}"
    assert extract_shared_block(holding[0], NAME) == canonical


def test_extractor_rejects_a_missing_or_unclosed_block():
    """The extractor must fail loudly; a silent empty string would ship a broken cell."""
    with pytest.raises(ValueError, match="missing sentinel"):
        extract_shared_block("nothing here\n", NAME)

    with pytest.raises(ValueError, match="never closed"):
        extract_shared_block(f"# --- BEGIN SHARED: {NAME} ---\nx = 1\n", NAME)

    with pytest.raises(ValueError, match="empty"):
        extract_shared_block(
            f"# --- BEGIN SHARED: {NAME} ---\n# --- END SHARED ---\n", NAME)
