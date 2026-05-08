# ============================================
#   Syntecxhub Internship - Week 2, Project 2
#   Library Book Inventory Manager
# ============================================

import json
import os
from datetime import datetime

# ---------- File Config ----------

DATA_FILE = "library.json"

# ---------- Book Class ----------

class Book:
    """Represents a single book in the library."""

    def __init__(self, book_id, title, author, genre, quantity):
        self.book_id      = str(book_id).strip().upper()
        self.title        = title.strip().title()
        self.author       = author.strip().title()
        self.genre        = genre.strip().title()
        self.quantity     = int(quantity)       # total copies
        self.available    = int(quantity)       # copies available to issue
        self.issued_to    = {}                  # member_name -> issue_date
        self.added_on     = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "book_id"   : self.book_id,
            "title"     : self.title,
            "author"    : self.author,
            "genre"     : self.genre,
            "quantity"  : self.quantity,
            "available" : self.available,
            "issued_to" : self.issued_to,
            "added_on"  : self.added_on,
        }

    @classmethod
    def from_dict(cls, data):
        b = cls(
            book_id  = data["book_id"],
            title    = data["title"],
            author   = data["author"],
            genre    = data["genre"],
            quantity = data["quantity"],
        )
        b.available = data.get("available", b.quantity)
        b.issued_to = data.get("issued_to", {})
        b.added_on  = data.get("added_on", "N/A")
        return b

    def is_available(self):
        return self.available > 0

    def issued_count(self):
        return self.quantity - self.available

    def __str__(self):
        status = f"✅ Available ({self.available}/{self.quantity})" if self.is_available() \
                 else f"❌ All Issued ({self.issued_count()} out)"
        return (
            f"  ID       : {self.book_id}\n"
            f"  Title    : {self.title}\n"
            f"  Author   : {self.author}\n"
            f"  Genre    : {self.genre}\n"
            f"  Status   : {status}\n"
            f"  Added On : {self.added_on}"
        )


# ---------- Library Class ----------

class Library:
    """Manages the entire book inventory with HashMap-style dict lookup."""

    def __init__(self, filepath=DATA_FILE):
        self.filepath  = filepath
        self.books     = {}   # book_id  -> Book  (fast lookup by ID)
        self.by_title  = {}   # title    -> [book_ids]
        self.by_author = {}   # author   -> [book_ids]
        self._load()

    # ---- File I/O ----

    def _load(self):
        """Load books from JSON into memory and rebuild indexes."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                records = json.load(f)
            for r in records:
                book = Book.from_dict(r)
                self.books[book.book_id] = book
            self._rebuild_indexes()
        except (json.JSONDecodeError, KeyError, IOError):
            print("  ⚠  Could not load library data. Starting fresh.")

    def _save(self):
        """Persist all books to JSON file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump([b.to_dict() for b in self.books.values()], f, indent=4)
        except IOError:
            print("  ❌ Error: Could not save library data.")

    def _rebuild_indexes(self):
        """Rebuild title and author lookup indexes."""
        self.by_title  = {}
        self.by_author = {}
        for book in self.books.values():
            self.by_title.setdefault(book.title.lower(), []).append(book.book_id)
            self.by_author.setdefault(book.author.lower(), []).append(book.book_id)

    def _add_to_index(self, book):
        self.by_title.setdefault(book.title.lower(), []).append(book.book_id)
        self.by_author.setdefault(book.author.lower(), []).append(book.book_id)

    # ---- Add Book ----

    def add_book(self):
        """Add a new book or increase quantity of existing one."""
        print("\n  --- Add Book ---")
        book_id = input("  Book ID      : ").strip().upper()
        if not book_id:
            print("  ⚠  Book ID cannot be empty.")
            return

        # If book already exists, increase quantity
        if book_id in self.books:
            book = self.books[book_id]
            try:
                qty = int(input(f"  Book '{book.title}' exists. Add how many copies? : "))
                if qty <= 0:
                    raise ValueError
                book.quantity  += qty
                book.available += qty
                self._save()
                print(f"  ✅ Added {qty} copies. Total now: {book.quantity}")
            except ValueError:
                print("  ⚠  Invalid quantity.")
            return

        title    = input("  Title        : ").strip()
        author   = input("  Author       : ").strip()
        genre    = input("  Genre        : ").strip() or "General"

        try:
            quantity = int(input("  Quantity     : "))
            if quantity <= 0:
                raise ValueError
        except ValueError:
            print("  ⚠  Quantity must be a positive integer.")
            return

        if not title or not author:
            print("  ⚠  Title and Author cannot be empty.")
            return

        book = Book(book_id, title, author, genre, quantity)
        self.books[book.book_id] = book
        self._add_to_index(book)
        self._save()
        print(f"\n  ✅ Book '{book.title}' added successfully!")

    # ---- List Books ----

    def list_books(self):
        """Display all books in a formatted table."""
        print("\n  --- Book Inventory ---")
        if not self.books:
            print("  📭 No books in the library.")
            return

        print("\n  " + "─" * 80)
        print(f"  {'ID':<10} {'Title':<26} {'Author':<20} {'Genre':<12} {'Avail':<7} {'Total'}")
        print("  " + "─" * 80)

        for book in sorted(self.books.values(), key=lambda b: b.title):
            avail_str = f"{book.available}/{book.quantity}"
            print(f"  {book.book_id:<10} {book.title:<26} {book.author:<20} {book.genre:<12} {avail_str:<7}")

        print("  " + "─" * 80)
        total_books  = sum(b.quantity for b in self.books.values())
        total_issued = sum(b.issued_count() for b in self.books.values())
        print(f"  Titles: {len(self.books)} | Total Copies: {total_books} | Issued: {total_issued}")

    # ---- View Book Detail ----

    def view_book(self):
        """Show full detail of a single book including who has it."""
        book_id = input("\n  Enter Book ID to view: ").strip().upper()
        book = self.books.get(book_id)
        if not book:
            print(f"  ⚠  No book found with ID '{book_id}'.")
            return

        print(f"\n  {'─'*44}")
        print(book)
        if book.issued_to:
            print(f"\n  Issued To:")
            for member, date in book.issued_to.items():
                print(f"    • {member}  (issued: {date})")
        print(f"  {'─'*44}")

    # ---- Issue Book ----

    def issue_book(self):
        """Issue a book to a library member."""
        print("\n  --- Issue Book ---")
        book_id = input("  Book ID       : ").strip().upper()
        book = self.books.get(book_id)
        if not book:
            print(f"  ⚠  Book ID '{book_id}' not found.")
            return
        if not book.is_available():
            print(f"  ❌ '{book.title}' has no available copies.")
            return

        member = input("  Member Name   : ").strip().title()
        if not member:
            print("  ⚠  Member name cannot be empty.")
            return

        # One copy per member per book
        if member in book.issued_to:
            print(f"  ⚠  '{member}' already has a copy of '{book.title}'.")
            return

        issue_date = datetime.now().strftime("%Y-%m-%d")
        book.issued_to[member] = issue_date
        book.available -= 1
        self._save()
        print(f"\n  ✅ '{book.title}' issued to '{member}' on {issue_date}.")
        print(f"     Remaining copies: {book.available}/{book.quantity}")

    # ---- Return Book ----

    def return_book(self):
        """Return an issued book from a member."""
        print("\n  --- Return Book ---")
        book_id = input("  Book ID       : ").strip().upper()
        book = self.books.get(book_id)
        if not book:
            print(f"  ⚠  Book ID '{book_id}' not found.")
            return

        if not book.issued_to:
            print(f"  ℹ  No copies of '{book.title}' are currently issued.")
            return

        print(f"\n  Currently issued to: {', '.join(book.issued_to.keys())}")
        member = input("  Member Name   : ").strip().title()

        if member not in book.issued_to:
            print(f"  ⚠  '{member}' does not have a copy of '{book.title}'.")
            return

        issued_date = book.issued_to.pop(member)
        book.available += 1
        self._save()
        print(f"\n  ✅ '{book.title}' returned by '{member}'.")
        print(f"     (Was issued on {issued_date})")
        print(f"     Available copies: {book.available}/{book.quantity}")

    # ---- Delete Book ----

    def delete_book(self):
        """Remove a book from inventory."""
        print("\n  --- Delete Book ---")
        book_id = input("  Enter Book ID to delete: ").strip().upper()
        book = self.books.get(book_id)
        if not book:
            print(f"  ⚠  Book ID '{book_id}' not found.")
            return
        if book.issued_count() > 0:
            print(f"  ⚠  Cannot delete '{book.title}' — {book.issued_count()} copy(ies) still issued.")
            return

        confirm = input(f"  Delete '{book.title}'? (yes/no): ").strip().lower()
        if confirm in ('yes', 'y'):
            del self.books[book_id]
            self._rebuild_indexes()
            self._save()
            print(f"  🗑  '{book.title}' removed from inventory.")
        else:
            print("  ❌ Deletion cancelled.")

    # ---- Search ----

    def search_books(self):
        """Search books by title, author, genre, or ID."""
        print("\n  --- Search Books ---")
        print("  [1] By Title  [2] By Author  [3] By Genre  [4] By ID")
        option  = input("  Choose (1-4): ").strip()
        keyword = input("  Keyword      : ").strip().lower()

        results = []
        for book in self.books.values():
            if option == '1' and keyword in book.title.lower():
                results.append(book)
            elif option == '2' and keyword in book.author.lower():
                results.append(book)
            elif option == '3' and keyword in book.genre.lower():
                results.append(book)
            elif option == '4' and keyword in book.book_id.lower():
                results.append(book)

        if not results:
            print(f"  🔍 No books found matching '{keyword}'.")
            return

        print(f"\n  Found {len(results)} result(s):\n")
        print("  " + "─" * 80)
        print(f"  {'ID':<10} {'Title':<26} {'Author':<20} {'Genre':<12} {'Avail'}")
        print("  " + "─" * 80)
        for book in results:
            avail = f"{book.available}/{book.quantity}"
            print(f"  {book.book_id:<10} {book.title:<26} {book.author:<20} {book.genre:<12} {avail}")
        print("  " + "─" * 80)

    # ---- Reports ----

    def show_report(self):
        """Display inventory summary report."""
        print("\n  --- Library Report ---")
        if not self.books:
            print("  📭 No books in library.")
            return

        total_titles  = len(self.books)
        total_copies  = sum(b.quantity  for b in self.books.values())
        total_avail   = sum(b.available for b in self.books.values())
        total_issued  = total_copies - total_avail

        print(f"\n  📚 Total Titles   : {total_titles}")
        print(f"  📦 Total Copies   : {total_copies}")
        print(f"  ✅ Available      : {total_avail}")
        print(f"  📤 Issued Out     : {total_issued}")

        # Genre breakdown
        genre_counts = {}
        for b in self.books.values():
            genre_counts[b.genre] = genre_counts.get(b.genre, 0) + b.quantity
        print(f"\n  Genre Breakdown:")
        for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
            bar = '█' * count
            print(f"    {genre:<20}: {bar} ({count})")

        # Currently issued books
        issued_books = [b for b in self.books.values() if b.issued_count() > 0]
        if issued_books:
            print(f"\n  Currently Issued Books:")
            print("  " + "─" * 50)
            for b in issued_books:
                print(f"  📖 {b.title} ({b.issued_count()} copy/copies out)")
                for member, date in b.issued_to.items():
                    print(f"      → {member} since {date}")


# ---------- Menu ----------

def show_menu(library):
    total = len(library.books)
    issued = sum(b.issued_count() for b in library.books.values())
    print("\n" + "=" * 46)
    print("      📚 LIBRARY BOOK INVENTORY MANAGER")
    print("=" * 46)
    print(f"  Books: {total} title(s) | Issued: {issued} copy/copies")
    print("─" * 46)
    print("  [1] Add Book")
    print("  [2] List All Books")
    print("  [3] View Book Detail")
    print("  [4] Issue Book to Member")
    print("  [5] Return Book")
    print("  [6] Search Books")
    print("  [7] Delete Book")
    print("  [8] Library Report")
    print("  [9] Exit")
    print("=" * 46)


# ---------- Main ----------

def main():
    print("\n  Welcome to the Syntecxhub Library Book Inventory Manager!")
    library = Library()

    actions = {
        '1': library.add_book,
        '2': library.list_books,
        '3': library.view_book,
        '4': library.issue_book,
        '5': library.return_book,
        '6': library.search_books,
        '7': library.delete_book,
        '8': library.show_report,
    }

    while True:
        show_menu(library)
        choice = input("  Choose an option (1-9): ").strip()

        if choice == '9':
            print("\n  👋 Goodbye! Library data saved.\n")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("\n  ⚠  Invalid choice. Please enter 1 to 9.")


if __name__ == "__main__":
    main()