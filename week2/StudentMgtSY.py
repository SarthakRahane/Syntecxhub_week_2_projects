# ============================================
#   Syntecxhub Internship - Week 2, Project 1
#   Student Management System
# ============================================

import json
import os
from datetime import datetime

# ---------- File Config ----------

DATA_FILE = "students.json"

# ---------- Student Class ----------

class Student:
    """Represents a single student record."""

    def __init__(self, student_id, name, grade, course, email=""):
        self.student_id = str(student_id).strip().upper()
        self.name       = name.strip().title()
        self.grade      = grade.strip().upper()
        self.course     = course.strip().title()
        self.email      = email.strip().lower()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        """Serialize student to a dictionary for JSON storage."""
        return {
            "student_id" : self.student_id,
            "name"       : self.name,
            "grade"      : self.grade,
            "course"     : self.course,
            "email"      : self.email,
            "created_at" : self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a student from a dictionary."""
        s = cls(
            student_id = data["student_id"],
            name       = data["name"],
            grade      = data["grade"],
            course     = data["course"],
            email      = data.get("email", ""),
        )
        s.created_at = data.get("created_at", "N/A")
        return s

    def __str__(self):
        email_str = self.email if self.email else "N/A"
        return (
            f"  ID      : {self.student_id}\n"
            f"  Name    : {self.name}\n"
            f"  Grade   : {self.grade}\n"
            f"  Course  : {self.course}\n"
            f"  Email   : {email_str}\n"
            f"  Added   : {self.created_at}"
        )


# ---------- StudentManager Class ----------

class StudentManager:
    """Manages a collection of Student records with file persistence."""

    VALID_GRADES = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F'}

    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.students = {}   # dict: student_id -> Student (HashMap-style lookup)
        self._load()

    # ---- File I/O ----

    def _load(self):
        """Load students from JSON file into memory."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                records = json.load(f)
            self.students = {
                r["student_id"]: Student.from_dict(r) for r in records
            }
        except (json.JSONDecodeError, KeyError, IOError):
            print("  ⚠  Could not load data file. Starting fresh.")
            self.students = {}

    def _save(self):
        """Persist all students to JSON file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(
                    [s.to_dict() for s in self.students.values()],
                    f, indent=4
                )
        except IOError:
            print("  ❌ Error: Could not save data to file.")

    # ---- Validation ----

    def _id_exists(self, student_id):
        return student_id.strip().upper() in self.students

    def _validate_grade(self, grade):
        return grade.strip().upper() in self.VALID_GRADES

    # ---- CRUD Operations ----

    def add_student(self):
        """Prompt user and add a new student."""
        print("\n  --- Add New Student ---")

        student_id = input("  Student ID   : ").strip().upper()
        if not student_id:
            print("  ⚠  Student ID cannot be empty.")
            return
        if self._id_exists(student_id):
            print(f"  ⚠  Student ID '{student_id}' already exists. Use Update instead.")
            return

        name = input("  Full Name    : ").strip()
        if not name:
            print("  ⚠  Name cannot be empty.")
            return

        grade = input(f"  Grade ({'/'.join(sorted(self.VALID_GRADES))}): ").strip().upper()
        if not self._validate_grade(grade):
            print(f"  ⚠  Invalid grade. Choose from: {', '.join(sorted(self.VALID_GRADES))}")
            return

        course = input("  Course       : ").strip()
        if not course:
            print("  ⚠  Course cannot be empty.")
            return

        email = input("  Email (opt.) : ").strip()

        student = Student(student_id, name, grade, course, email)
        self.students[student.student_id] = student
        self._save()
        print(f"\n  ✅ Student '{name}' added successfully!")

    def list_students(self):
        """Display all students in a formatted table."""
        print("\n  --- Student Records ---")
        if not self.students:
            print("  📭 No student records found.")
            return

        # Table header
        print("\n  " + "─" * 72)
        print(f"  {'ID':<12} {'Name':<22} {'Grade':<8} {'Course':<20} {'Email'}")
        print("  " + "─" * 72)

        for s in sorted(self.students.values(), key=lambda x: x.student_id):
            email = s.email if s.email else "—"
            print(f"  {s.student_id:<12} {s.name:<22} {s.grade:<8} {s.course:<20} {email}")

        print("  " + "─" * 72)
        print(f"  Total: {len(self.students)} student(s)")

    def view_student(self):
        """Show detailed info for a single student."""
        student_id = input("\n  Enter Student ID to view: ").strip().upper()
        student = self.students.get(student_id)
        if not student:
            print(f"  ⚠  No student found with ID '{student_id}'.")
            return
        print(f"\n  {'─'*40}")
        print(student)
        print(f"  {'─'*40}")

    def update_student(self):
        """Update an existing student's details."""
        print("\n  --- Update Student ---")
        student_id = input("  Enter Student ID to update: ").strip().upper()
        student = self.students.get(student_id)
        if not student:
            print(f"  ⚠  No student found with ID '{student_id}'.")
            return

        print(f"\n  Current record:\n{student}")
        print("\n  (Press Enter to keep current value)")

        name = input(f"\n  New Name  [{student.name}]  : ").strip()
        if name:
            student.name = name.title()

        grade = input(f"  New Grade [{student.grade}] : ").strip().upper()
        if grade:
            if not self._validate_grade(grade):
                print(f"  ⚠  Invalid grade '{grade}'. Grade not updated.")
            else:
                student.grade = grade

        course = input(f"  New Course [{student.course}] : ").strip()
        if course:
            student.course = course.title()

        email = input(f"  New Email [{student.email}] : ").strip()
        if email:
            student.email = email.lower()

        self._save()
        print(f"\n  ✅ Student '{student.student_id}' updated successfully!")

    def delete_student(self):
        """Delete a student record by ID."""
        print("\n  --- Delete Student ---")
        student_id = input("  Enter Student ID to delete: ").strip().upper()
        student = self.students.get(student_id)
        if not student:
            print(f"  ⚠  No student found with ID '{student_id}'.")
            return

        confirm = input(f"  ⚠  Delete '{student.name}' ({student_id})? (yes/no): ").strip().lower()
        if confirm in ('yes', 'y'):
            del self.students[student_id]
            self._save()
            print(f"  🗑  Student '{student_id}' deleted successfully.")
        else:
            print("  ❌ Deletion cancelled.")

    def search_students(self):
        """Search students by name, ID, or course."""
        print("\n  --- Search Students ---")
        print("  Search by: [1] Name  [2] ID  [3] Course  [4] Grade")
        option = input("  Choose (1-4): ").strip()

        keyword = input("  Enter search keyword: ").strip().lower()
        results = []

        for s in self.students.values():
            if option == '1' and keyword in s.name.lower():
                results.append(s)
            elif option == '2' and keyword in s.student_id.lower():
                results.append(s)
            elif option == '3' and keyword in s.course.lower():
                results.append(s)
            elif option == '4' and keyword == s.grade.lower():
                results.append(s)

        if not results:
            print(f"  🔍 No students found matching '{keyword}'.")
            return

        print(f"\n  Found {len(results)} result(s):")
        print("\n  " + "─" * 72)
        print(f"  {'ID':<12} {'Name':<22} {'Grade':<8} {'Course':<20} {'Email'}")
        print("  " + "─" * 72)
        for s in results:
            email = s.email if s.email else "—"
            print(f"  {s.student_id:<12} {s.name:<22} {s.grade:<8} {s.course:<20} {email}")
        print("  " + "─" * 72)

    def show_summary(self):
        """Display summary stats of all student records."""
        print("\n  --- Summary Report ---")
        total = len(self.students)
        if total == 0:
            print("  📭 No records available.")
            return

        grade_counts = {}
        for s in self.students.values():
            grade_counts[s.grade] = grade_counts.get(s.grade, 0) + 1

        course_counts = {}
        for s in self.students.values():
            course_counts[s.course] = course_counts.get(s.course, 0) + 1

        print(f"\n  📊 Total Students : {total}")
        print(f"\n  Grade Distribution:")
        for grade in sorted(grade_counts):
            bar = '█' * grade_counts[grade]
            print(f"    {grade:<5}: {bar} ({grade_counts[grade]})")

        print(f"\n  Courses:")
        for course, count in sorted(course_counts.items(), key=lambda x: -x[1]):
            print(f"    {course:<25}: {count} student(s)")


# ---------- Menu ----------

def show_menu(manager):
    """Display the main menu."""
    total = len(manager.students)
    print("\n" + "=" * 44)
    print("      🎓 STUDENT MANAGEMENT SYSTEM")
    print("=" * 44)
    print(f"  Total Records: {total} student(s)")
    print("─" * 44)
    print("  [1] Add Student")
    print("  [2] List All Students")
    print("  [3] View Student Detail")
    print("  [4] Update Student")
    print("  [5] Delete Student")
    print("  [6] Search Students")
    print("  [7] Summary Report")
    print("  [8] Exit")
    print("=" * 44)


# ---------- Main ----------

def main():
    print("\n  Welcome to the Syntecxhub Student Management System!")
    manager = StudentManager()

    menu_actions = {
        '1': manager.add_student,
        '2': manager.list_students,
        '3': manager.view_student,
        '4': manager.update_student,
        '5': manager.delete_student,
        '6': manager.search_students,
        '7': manager.show_summary,
    }

    while True:
        show_menu(manager)
        choice = input("  Choose an option (1-8): ").strip()

        if choice == '8':
            print("\n  👋 Goodbye! All records saved.\n")
            break
        elif choice in menu_actions:
            menu_actions[choice]()
        else:
            print("\n  ⚠  Invalid choice. Please enter 1 to 8.")


if __name__ == "__main__":
    main()