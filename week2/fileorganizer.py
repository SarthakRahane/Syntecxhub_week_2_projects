# ============================================
#   Syntecxhub Internship - Week 2, Project 3
#   File Organizer Script
# ============================================

import os
import shutil
import logging
import argparse
from datetime import datetime
from pathlib import Path

# ---------- Extension -> Folder Mapping ----------

EXTENSION_MAP = {
    "Images"     : [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                    ".webp", ".ico", ".tiff", ".raw"],
    "Videos"     : [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
                    ".webm", ".m4v", ".3gp"],
    "Audio"      : [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma",
                    ".m4a", ".opus"],
    "Documents"  : [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt",
                    ".pptx", ".txt", ".odt", ".rtf", ".csv"],
    "Code"       : [".py", ".js", ".ts", ".html", ".css", ".java",
                    ".c", ".cpp", ".cs", ".php", ".rb", ".go",
                    ".rs", ".swift", ".kt", ".sh", ".bat", ".json",
                    ".xml", ".yaml", ".yml", ".sql"],
    "Archives"   : [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2",
                    ".xz", ".iso"],
    "Executables": [".exe", ".msi", ".apk", ".dmg", ".deb", ".rpm"],
    "Fonts"      : [".ttf", ".otf", ".woff", ".woff2"],
    "Data"       : [".db", ".sqlite", ".xlsx", ".json", ".xml"],
}

# Build reverse map: extension -> folder name
EXT_TO_FOLDER = {}
for folder, extensions in EXTENSION_MAP.items():
    for ext in extensions:
        EXT_TO_FOLDER[ext.lower()] = folder


# ---------- Logging Setup ----------
# Timestamps only go to the LOG FILE, not the console.

def setup_logging(log_dir):
    """Set up file logger (with timestamps) and clean console output."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = os.path.join(log_dir, "organizer_" + timestamp + ".log")

    logger = logging.getLogger("organizer")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # File handler — includes timestamps
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  [%(levelname)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(fh)
    return logger, log_file


# ---------- Core Functions ----------

def get_destination_folder(extension):
    return EXT_TO_FOLDER.get(extension.lower(), "Others")


def resolve_collision(destination_path):
    """Append counter suffix if file already exists at destination."""
    if not destination_path.exists():
        return destination_path

    stem    = destination_path.stem
    suffix  = destination_path.suffix
    parent  = destination_path.parent
    counter = 1

    while True:
        new_name = stem + "_" + str(counter) + suffix
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def scan_files(source_dir):
    """Return list of top-level files in source_dir."""
    source_path = Path(source_dir)
    return [
        f for f in source_path.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]


def organize_files(source_dir, dry_run=False, logger=None):
    """
    Scan source_dir and move each file into a subfolder by extension.
    Prints clean output to console; full details go to log file.
    """
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        print("  [ERROR] Source folder not found: " + str(source_path))
        return {}

    if not source_path.is_dir():
        print("  [ERROR] Path is not a directory: " + str(source_path))
        return {}

    mode_label = "DRY RUN" if dry_run else "LIVE RUN"

    print("")
    print("=" * 55)
    print("  File Organizer - " + mode_label)
    print("  Source  : " + str(source_path))
    print("  Started : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 55)

    if logger:
        logger.info("File Organizer - " + mode_label)
        logger.info("Source : " + str(source_path))

    files = scan_files(source_path)

    if not files:
        print("  No files found to organize.")
        return {"total": 0, "moved": 0, "skipped": 0, "errors": 0}

    print("  Found " + str(len(files)) + " file(s) to process.")
    print("")

    stats = {
        "total"    : len(files),
        "moved"    : 0,
        "skipped"  : 0,
        "errors"   : 0,
        "by_folder": {},
    }

    for file_path in sorted(files):
        ext         = file_path.suffix.lower()
        folder_name = get_destination_folder(ext)
        dest_folder = source_path / folder_name
        dest_path   = dest_folder / file_path.name

        dest_path = resolve_collision(dest_path)

        collision_note = ""
        if dest_path.name != file_path.name:
            collision_note = " (renamed: " + dest_path.name + ")"

        try:
            if dry_run:
                msg = "  [DRY RUN]  " + file_path.name + "  ->  " + folder_name + "/" + dest_path.name + collision_note
                print(msg)
                if logger:
                    logger.info(msg.strip())
            else:
                os.makedirs(dest_folder, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                msg = "  [MOVED]    " + file_path.name + "  ->  " + folder_name + "/" + dest_path.name + collision_note
                print(msg)
                if logger:
                    logger.info(msg.strip())

            stats["moved"] += 1
            stats["by_folder"][folder_name] = \
                stats["by_folder"].get(folder_name, 0) + 1

        except PermissionError:
            msg = "  [SKIPPED]  Permission denied: " + file_path.name
            print(msg)
            if logger:
                logger.warning(msg.strip())
            stats["skipped"] += 1

        except Exception as e:
            msg = "  [ERROR]    Could not move '" + file_path.name + "': " + str(e)
            print(msg)
            if logger:
                logger.error(msg.strip())
            stats["errors"] += 1

    return stats


def print_summary(stats, dry_run, logger=None):
    """Print a clean summary to console and log file."""
    mode = "DRY RUN - no files were actually moved" if dry_run else "LIVE RUN - files have been moved"

    print("")
    print("=" * 55)
    print("  DONE - " + mode)
    print("-" * 55)
    print("  Total files found  : " + str(stats.get("total",   0)))
    print("  Moved/Simulated    : " + str(stats.get("moved",   0)))
    print("  Skipped            : " + str(stats.get("skipped", 0)))
    print("  Errors             : " + str(stats.get("errors",  0)))

    if stats.get("by_folder"):
        print("")
        print("  Files by Folder:")
        for folder, count in sorted(stats["by_folder"].items()):
            bar = "#" * count
            print("    " + folder.ljust(15) + ": " + bar + " (" + str(count) + ")")

    print("=" * 55)
    print("")

    if logger:
        logger.info("DONE - " + mode)
        logger.info("Total: " + str(stats.get("total", 0)) +
                    "  Moved: " + str(stats.get("moved", 0)) +
                    "  Skipped: " + str(stats.get("skipped", 0)) +
                    "  Errors: " + str(stats.get("errors", 0)))


# ---------- Interactive Menu ----------

def interactive_menu():
    print("")
    print("=" * 50)
    print("       FILE ORGANIZER SCRIPT")
    print("=" * 50)
    print("  Supported Categories:")
    for folder in EXTENSION_MAP:
        exts = ", ".join(EXTENSION_MAP[folder][:4])
        more = " ..." if len(EXTENSION_MAP[folder]) > 4 else ""
        print("    - " + folder.ljust(14) + ": " + exts + more)
    print("=" * 50)

    source = input(
        "\n  Enter folder path to organize\n"
        "  (or press Enter for current directory): "
    ).strip()

    if not source:
        source = os.getcwd()

    source = os.path.expanduser(source)

    print("")
    print("  Mode:")
    print("  [1] Dry Run  - Preview only, no files moved")
    print("  [2] Live Run - Actually move files")
    mode_choice = input("\n  Choose (1/2): ").strip()

    dry_run = mode_choice != "2"

    log_dir        = os.path.join(source, "_organizer_logs")
    logger, log_file = setup_logging(log_dir)

    print("\n  Log saved to: " + log_file)

    stats = organize_files(source, dry_run=dry_run, logger=logger)

    if stats:
        print_summary(stats, dry_run, logger=logger)

    if dry_run and stats.get("moved", 0) > 0:
        proceed = input("  Run LIVE now to actually move files? (yes/no): ").strip().lower()
        if proceed in ("yes", "y"):
            print("\n  Running LIVE...\n")
            stats = organize_files(source, dry_run=False, logger=logger)
            print_summary(stats, dry_run=False, logger=logger)


# ---------- CLI via argparse ----------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Syntecxhub File Organizer - sorts files into subfolders by extension."
    )
    parser.add_argument(
        "source",
        nargs   = "?",
        default = None,
        help    = "Path to the folder to organize (default: interactive menu)"
    )
    parser.add_argument(
        "--dry-run",
        action  = "store_true",
        help    = "Simulate organization without moving files"
    )
    parser.add_argument(
        "--log-dir",
        default = None,
        help    = "Custom directory for log files"
    )
    return parser.parse_args()


# ---------- Main ----------

def main():
    args = parse_args()

    if args.source:
        source         = os.path.expanduser(args.source)
        log_dir        = args.log_dir or os.path.join(source, "_organizer_logs")
        logger, log_file = setup_logging(log_dir)
        print("  Log saved to: " + log_file + "\n")
        stats = organize_files(source, dry_run=args.dry_run, logger=logger)
        if stats:
            print_summary(stats, args.dry_run, logger=logger)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()