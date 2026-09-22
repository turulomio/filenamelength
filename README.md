# filenamelength

A Python command-line utility to inspect, measure, filter, and optimize files based on path and filename lengths across directory trees. It also provides reference limits for popular filesystems, automated collision-safe renaming, and multi-step undo capabilities.

---

## Motivation

Different operating systems and filesystems enforce drastically different constraints on filename and path lengths:

- **Windows & Legacy Systems:** Standard Windows Win32 APIs impose a `MAX_PATH` limit of **260 characters** for the full path. Once drive letters (`C:\`), directory separators, and multi-character file extensions (e.g., `.docx`, `.tar.gz`) are accounted for, the realistic safe filename length drops to **247–252 characters**—or significantly less when files reside inside nested folders.
- **Linux/Unix vs. Windows Architecture:** On Linux/Unix filesystems (ext4, Btrfs, XFS), individual filenames can reach up to **255 bytes** while the total path can extend up to **4,096 bytes** (`PATH_MAX`). In contrast, Windows historical path handling treats directory paths and filenames within the same tight boundary.
- **Cross-Platform Headaches:** When transferring files across platforms (such as backing up Linux data to Windows shares, external FAT32/exFAT drives, optical media, or cloud storage), long names or deeply nested paths frequently trigger cryptic `"File name too long"` errors or silent copy failures. Users are often puzzled because a filename looks short, yet the full directory path breaches destination filesystem limits.

`filenamelength` was created to solve this problem:
1. **Audit:** Quickly discover files and paths that exceed target filesystem constraints.
2. **Reference:** Consult built-in limits for common Linux, Windows, macOS, Unix, optical, and network filesystems (`filenamelength --help`).
3. **Remediate:** Automatically rename files to safe, optimized lengths (`--rename`) while preserving file extensions and preventing collisions.
4. **Safety Net:** Revert any renaming operations seamlessly (`--undo`).

---

## Features

- **Inspect & Filter:** Scan directory trees and list files exceeding minimum path or filename length thresholds.
- **Filesystem Reference Limits:** Displays built-in reference tables of maximum filename and path lengths for common filesystems (Linux, Windows, macOS, BSD, optical, and network filesystems).
- **Optimized Renaming (`--rename`):** Shortens names of files exceeding limits to fit the desired size without modifying directory paths, preserving file extensions.
- **Collision Avoidance:** Automatically prevents overwriting existing files by appending numerical suffixes (`_1`, `_2`, ...) while adjusting stem lengths so the total length never exceeds the target limit.
- **Multi-Step Undo (`--undo [N]`):** Rolls back rename operations safely, with support for undoing single or multiple sessions (`N` times).
- **User Configuration & History:** Stores configuration (`config.json`) and rename history (`history.json`) in the user config directory (`~/.config/filenamelength/` or `$XDG_CONFIG_HOME/filenamelength`).

---

## Installation

Using Poetry:
```bash
poetry install
```

Or run directly with Poetry:
```bash
poetry run filenamelength --help
```

---

## Usage

### 1. Basic Listing
Scan the current directory tree and list all files:
```bash
poetry run filenamelength
```

### 2. Filtering by Length Limits
List files whose filename length is at least 50 characters:
```bash
poetry run filenamelength --minimum_filename_length 50
```

List files whose full path length is at least 100 characters:
```bash
poetry run filenamelength --minimum_path_length 100
```

Combine filters:
```bash
poetry run filenamelength --minimum_path_length 100 --minimum_filename_length 50
```

### 3. Sorting Output
Sort output by `Path`, `PathLength`, or `FilenameLength` (default is `Path`):
```bash
poetry run filenamelength --minimum_filename_length 50 --order_by FilenameLength
```

### 4. Renaming Files (`--rename`)
Rename files exceeding the specified threshold so they fit the desired length:
```bash
poetry run filenamelength --minimum_filename_length 50 --rename
```
- File extensions are preserved.
- The directory tree remains untouched.
- If a target filename already exists, an incremental numerical suffix (e.g. `_1`) is added while keeping the total length within the target limit.

### 5. Undoing Renames (`--undo`)
Undo the last rename operation:
```bash
poetry run filenamelength --undo
```

Undo the last `N` rename operations:
```bash
poetry run filenamelength --undo 3
```

---

## Demonstration Videos

### 1. Help and Filesystem Limits Reference (`command.gif`)
Running `filenamelength --help` displays all available CLI options along with the reference table showing maximum filename and full path limits for popular filesystems:

![CLI Help and Filesystem Limits](doc/command.gif)

### 2. Filtering, Renaming, and Undoing (`howto.gif`)
Demonstrates the complete workflow:
1. **Filtering & Sorting:** Inspects files whose filename length is at least 25 characters, ordered by filename length (`--minimum_filename_length 25 --order_by FilenameLength`).
2. **Safe Renaming (`--rename`):** Shortens names exceeding the threshold to fit the desired size without altering directories and with automatic collision avoidance.
3. **Undoing Changes (`--undo`):** Reverts the rename operation, restoring all original filenames.

![Filtering, Renaming, and Undoing](doc/howto.gif)

---


## User Configuration

Configuration files are located in `~/.config/filenamelength/` (or `$XDG_CONFIG_HOME/filenamelength`):
- `config.json`: General preferences such as `max_history_entries`.
- `history.json`: Log of rename sessions and file mappings used for undo operations.

---

## Running Tests

Run the test suite with code coverage:
```bash
poetry run poe test
# or directly with pytest
poetry run pytest --cov=filenamelength --cov-report=term-missing
```

---

## CLI Reference

| Option | Description |
|---|---|
| `-h`, `--help` | Show help message and filesystem limits table, then exit. |
| `--version` | Show program version. |
| `--minimum_path_length <int>` | List files whose path length is `>=` this value. |
| `--minimum_filename_length <int>` | List files whose filename length is `>=` this value. |
| `--order_by {Path,PathLength,FilenameLength}` | Sort output by specified criterion (default: `Path`). |
| `--rename` | Rename files exceeding limits to an optimized name within the desired length. |
| `--undo [N]` | Undo the last N rename operations (default: 1). |

---

## License

GPL-3.0-only
