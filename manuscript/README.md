# OmniFaceRig Manuscript

This directory contains the LaTeX sources for the OmniFaceRig research paper submitted to SIGGRAPH Asia 2026.

OmniFaceRig is a fully automatic, end-to-end system for creating inner-mouth-aware facial rigs across diverse 3D character topologies. Starting from a static surface-only character mesh, the system produces FACS-based facial blendshapes together with procedurally generated teeth, gums, and tongue geometry. The manuscript also introduces Omni-Bench, a benchmark of rigged human, humanoid, and animal characters.

## Documents

- `sample-sigconf.tex`: main paper manuscript
- `supplemental.tex`: supplemental material
- `references.bib`: bibliography shared by the paper materials
- `acmart.cls` and related ACM files: local SIGGRAPH/ACM LaTeX template dependencies
- `figures/`: figures used by the manuscript and supplemental material

Both documents use the ACM `acmart` class and are currently configured for anonymous review.

## Overleaf

To use this manuscript in Overleaf, upload the contents of this directory as the root of an Overleaf project. Keep the main `.tex` files, `acmart.cls`, bibliography style files, and other ACM template dependencies at the project root. The `figures/` subdirectory is supported by Overleaf and is referenced through portable relative paths.

Select `sample-sigconf.tex` as the main document for the paper. To compile the supplemental material separately, select `supplemental.tex` as the main document.

## Installing the LaTeX Compiler

The recommended local compiler is [Tectonic](https://tectonic-typesetting.github.io/). Tectonic is a lightweight, self-contained TeX engine that automatically downloads required support files and runs the necessary TeX and BibTeX passes.

On macOS with [Homebrew](https://brew.sh/) installed, run:

```bash
brew install tectonic
```

Verify the installation with:

```bash
tectonic --version
```

## Compiling the Manuscript

From this directory, compile the main paper with:

```bash
tectonic sample-sigconf.tex
```

This generates `sample-sigconf.pdf` in the current directory.

Compile the supplemental material with:

```bash
tectonic supplemental.tex
```

This generates `supplemental.pdf` in the current directory.

Tectonic may take longer on the first run while it downloads and caches LaTeX packages and fonts. Subsequent builds reuse the local cache.

## Editing Workflow

1. Edit `sample-sigconf.tex` or `supplemental.tex` and the corresponding bibliography or figure files.
2. Run the relevant Tectonic command.
3. Review the generated PDF for layout warnings, missing references, and figure placement.

Generated PDFs are build artifacts and do not need to be committed unless the project explicitly chooses to version them.
