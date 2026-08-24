# my-notes — personal workspace

Everything in this directory is mine. Everything outside it is an unmodified mirror
of [DataTalksClub/stock-markets-analytics-zoomcamp](https://github.com/DataTalksClub/stock-markets-analytics-zoomcamp).

That split is the point: upstream directories stay byte-identical, so syncing each week
is always a clean fast-forward with nothing to merge by hand.

```bash
git fetch upstream && git merge --ff-only upstream/main
```

## Layout

| Path | Contents |
|---|---|
| [`2026-prep-brief.md`](2026-prep-brief.md) | **Start here.** Schedule, deadlines, links, certification rules, gotchas. |
| [`environment.yml`](environment.yml) | Local conda env. Pins matter — see the comments in the file. |
| `01-intro/` … `05-automation/` | Per-module notes, notebooks, and data. |
| `project/` | Capstone workspace. |
| `tools/` | Small notebook utilities. |
| `archive/` | Superseded artifacts, kept on disk, gitignored. |

## What is and isn't in git

Committed: notes, notebooks, `links.md`, transcripts, small data files.

Gitignored but present on disk (see [`../.gitignore`](../.gitignore)):

- `**/slides/` — lecture screenshots (~9 MB for Module 1 alone)
- `**/pdfs/` — third-party PDFs like the ARK Big Ideas reports (~34 MB), freely
  re-downloadable from [ark-funds.com](https://www.ark-funds.com/)
- `archive/` — derived files regenerable from what is already in git

They stay local because they are large, binary, and not authored by me. Committing them
would have grown the repo ~40 MB per module.

## Tools

```bash
# strip outputs + execution counts from a notebook
python my-notes/tools/clean_notebook.py in.ipynb out.ipynb

# structural sanity check (cell counts, JSON validity)
python my-notes/tools/validate_notebook.py notebook.ipynb
```

## Environment

```bash
conda env create -f my-notes/environment.yml
conda activate stock-markets-analytics
python -m ipykernel install --user --name stock-markets-analytics
```

Colab remains primary for live sessions — see [`01-intro/COLAB_SETUP.md`](01-intro/COLAB_SETUP.md).
