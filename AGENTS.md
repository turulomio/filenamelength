# AGENTS.md - Developer and AI Agent Guidelines for `filenamelength`

## Project Overview

`filenamelength` is a Python command-line utility designed to inspect, measure, and filter files based on path and filename lengths across directory trees. It also provides reference information on maximum filename and full path length limits for popular filesystems.

---

## Tech Stack & Dependencies

- **Language:** Python `>=3.10, <4`
- **Package Manager & Build System:** [Poetry](https://python-poetry.org/) (`poetry-core >= 2.0.0`)
- **Task Runner:** [PoeThePoet](https://poethepoet.natn.io/) (`poethepoet >= 0.48.0`)
- **Core Dependencies:**
  - `colorama` (`>=0.4.6`): Colored terminal output formatting.
  - `pydicts` (`>=1.5.0`): Tabular formatting and list-of-dictionaries operations (`lod`).
- **Internationalization:** `gettext` (`filenamelength/locale/`)

---

## Repository Structure

```
.
├── filenamelength/
│   ├── __init__.py          # Version (__version__) and date metadata
│   ├── filenamelength.py    # Main application logic & CLI entry point
│   ├── filesystems.py       # Reference table data for popular filesystems
│   ├── poethepoet.py        # Automation tasks (poe translate, poe release)
│   └── locale/              # Gettext i18n catalogs (es, .pot, .po, .mo)
│       ├── es.po
│       ├── filenamelength.pot
│       └── es/LC_MESSAGES/filenamelength.mo
├── pyproject.toml           # Poetry project configuration & script definitions
├── poetry.lock              # Locked dependencies
├── README.md                # General user documentation
└── AGENTS.md                # Agent & contributor guidelines
```

---

## Common Development Commands

### 1. Environment Setup
```bash
poetry install
```

### 2. Running the CLI
```bash
# Run default scan in current directory
poetry run filenamelength

# View help and filesystem limits reference table
poetry run filenamelength --help

# Filter by minimum path and filename length
poetry run filenamelength --minimum_path_length 100 --minimum_filename_length 50

# Sort output (options: Path, PathLength, FilenameLength)
poetry run filenamelength --order_by PathLength
```

### 3. Internationalization (i18n)
All user-facing strings in Python files are wrapped with `_("...")`.

> **IMPORTANT:** Do NOT perform translation updates (`poe translate`, editing `.po` files, or compiling `.mo` catalogs) automatically. Only execute translation tasks when the user explicitly instructs you to do so.

When explicitly instructed to update translations:
1. Ensure translatable strings in code are wrapped in `_("...")`.
2. Run translation extraction and compilation:
   ```bash
   poetry run poe translate
   ```
3. Update translations in `filenamelength/locale/es.po`.
4. Re-run `poetry run poe translate` to compile `.mo` catalogs.

### 4. Running Tests
```bash
# Run pytest with code coverage
poetry run poe test
# or directly with pytest
poetry run pytest --cov=filenamelength --cov-report=term-missing
```

### 5. Release Checklist
To view the release steps:
```bash
poetry run poe release
```

---

## CLI Options Reference

| Flag | Description |
|---|---|
| `-h`, `--help` | Show help message with options and the filesystem limits table, and exit. |
| `--version` | Show program version. |
| `--minimum_path_length <int>` | Filter files whose full path length is `>=` specified integer. |
| `--minimum_filename_length <int>` | Filter files whose filename length is `>=` specified integer. |
| `--order_by {Path,PathLength,FilenameLength}` | Sort output by specified criterion (default: `Path`). |
| `--rename` | Rename files exceeding limits to an optimized name within the desired length. |
| `--undo [N]` | Undo the last N rename operations (default: 1). |

---

## Supported Filesystems Reference

The `--help` output includes max filename and path limits for popular filesystems:
- **Linux:** ext4, ext3, ext2, Btrfs, XFS, F2FS, tmpfs
- **Windows:** NTFS, FAT32, exFAT, FAT16, FAT12
- **macOS / Apple:** APFS, HFS+
- **Unix / BSD:** ZFS, UFS/UFS2, JFS, ReiserFS
- **Network / Distributed:** NFS (v3/v4), SMB/CIFS, CephFS, GlusterFS
- **Optical:** ISO 9660 (Rock Ridge / Joliet / Level 1-3), UDF

---

## Coding and Contribution Conventions

- **Preserve Existing Comments & Docstrings:** Retain context notes and architectural commentary in source files.
- **Gettext Wrappers:** Always wrap console output and user-facing strings in `_()`.
- **Do Not Translate Automatically:** Never run `poe translate` or modify `.po`/`.mo` translation files unless explicitly requested by the user.
- **Formatting Tables:** Use `pydicts.lod.lod_print()` for consistent tabular output.
- **Entry Points:** The main CLI entry point is defined as `filenamelength.filenamelength:main`.
