import json
import os
import random
import textwrap


# Path to the data file (../data/presentations.json relative to this script)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "presentations.json")


def load_speakers(path: str = DATA_PATH):
    """Load speaker data from JSON file."""
    if not os.path.exists(path):
        print(f"[ERROR] Could not find data file at: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Allow either a list or {"speakers": [...]} style
    if isinstance(data, dict):
        data = data.get("speakers", [])

    if not isinstance(data, list):
        print("[ERROR] Data format not recognized. Expected a list of speaker records.")
        return []

    return data


def build_indexes(speakers):
    """Build lookup dictionaries for names and themes."""
    by_name = {}
    by_theme = {}

    for sp in speakers:
        name = (sp.get("name") or "").strip()
        theme = (sp.get("theme") or "").strip()

        if name:
            by_name[name.lower()] = sp

        # Index by primary theme
        if theme:
            by_theme.setdefault(theme.lower(), []).append(sp)

        # Also index by tags if available
        tags = sp.get("tags") or []
        for tag in tags:
            tag_key = (tag or "").strip().lower()
            if tag_key:
                by_theme.setdefault(tag_key, []).append(sp)

    return by_name, by_theme


def print_header():
    print("=" * 70)
    print(" TED-Style Presentation Chatbot ".center(70, "="))
    print("=" * 70)
    print("Ask about student speakers, themes, or get a motivational summary.\n")


def print_menu():
    print("\nPlease choose an option:")
    print("  1. List all speakers")
    print("  2. List all themes/tags")
    print("  3. Get information about a specific speaker")
    print("  4. Find speakers by theme or tag")
    print("  5. Get a random motivational summary")
    print("  6. Exit")


def wrap(text, width=80, indent=""):
    wrapped = textwrap.fill(text, width=width)
    if indent:
        wrapped = textwrap.indent(wrapped, indent)
    return wrapped


def show_speaker(sp):
    """Nicely print a single speaker record."""
    name = sp.get("name", "Unknown speaker")
    title = sp.get("title", "Untitled talk")
    theme = sp.get("theme", "Unknown theme")
    summary = sp.get("summary", "No summary available.")
    tags = sp.get("tags") or []

    print("\n" + "-" * 70)
    print(f"Speaker : {name}")
    print(f"Title   : {title}")
    print(f"Theme   : {theme}")
    if tags:
        print(f"Tags    : {', '.join(tags)}")
    print("-" * 70)
    print(wrap(summary))
    print("-" * 70 + "\n")


def list_speakers(speakers):
    if not speakers:
        print("No speakers found.")
        return
    print("\nAvailable speakers:")
    for sp in speakers:
        name = sp.get("name", "Unknown")
        title = sp.get("title", "Untitled talk")
        print(f"  - {name} — \"{title}\"")


def list_themes(by_theme):
    if not by_theme:
        print("No themes/tags found.")
        return
    print("\nAvailable themes/tags:")
    for theme in sorted(by_theme.keys()):
        print(f"  - {theme}")


def search_speaker(by_name):
    query = input("\nEnter the speaker's name: ").strip().lower()
    if not query:
        print("No name entered.")
        return

    # Exact lookup first
    sp = by_name.get(query)
    if not sp:
        # Try partial match
        matches = [
            v for k, v in by_name.items()
            if query in k
        ]
        if not matches:
            print("No matching speaker found.")
            return
        elif len(matches) == 1:
            sp = matches[0]
        else:
            print("Multiple matches found:")
            for i, m in enumerate(matches, start=1):
                print(f"  {i}. {m.get('name', 'Unknown')}")
            choice = input("Select a number (or press Enter to cancel): ").strip()
            if not choice.isdigit():
                print("Cancelled.")
                return
            idx = int(choice) - 1
            if idx < 0 or idx >= len(matches):
                print("Invalid choice.")
                return
            sp = matches[idx]

    show_speaker(sp)


def search_by_theme(by_theme):
    query = input("\nEnter a theme or tag (e.g., growth, courage, AI): ").strip().lower()
    if not query:
        print("No theme entered.")
        return

    matches = by_theme.get(query)
    if not matches:
        # Try partial match over keys
        keys = [k for k in by_theme.keys() if query in k]
        if not keys:
            print("No speakers found for that theme/tag.")
            return
        matches = []
        for k in keys:
            matches.extend(by_theme[k])

    print(f"\nSpeakers related to '{query}':")
    unique = []
    seen = set()
    for sp in matches:
        name = sp.get("name", "Unknown")
        if name not in seen:
            unique.append(sp)
            seen.add(name)

    for sp in unique:
        name = sp.get("name", "Unknown")
        title = sp.get("title", "Untitled talk")
        print(f"  - {name} — \"{title}\"")

    # Optionally show one in detail
    choice = input("\nWould you like to see one speaker's summary? (y/n): ").strip().lower()
    if choice == "y" and unique:
        sp = random.choice(unique)
        show_speaker(sp)


def random_motivation(speakers):
    if not speakers:
        print("No speakers available.")
        return
    sp = random.choice(speakers)
    print("\nHere's a random motivational insight for you:")
    show_speaker(sp)


def main():
    speakers = load_speakers()
    if not speakers:
        return

    by_name, by_theme = build_indexes(speakers)
    print_header()

    while True:
        try:
            print_menu()
            choice = input("\nEnter your choice (1–6): ").strip()

            if choice == "1":
                list_speakers(speakers)
            elif choice == "2":
                list_themes(by_theme)
            elif choice == "3":
                search_speaker(by_name)
            elif choice == "4":
                search_by_theme(by_theme)
            elif choice == "5":
                random_motivation(speakers)
            elif choice == "6":
                print("\nThank you for using the TED-Style Presentation Chatbot. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
