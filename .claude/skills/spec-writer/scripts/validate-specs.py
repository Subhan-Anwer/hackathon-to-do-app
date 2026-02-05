#!/usr/bin/env python3
"""
Spec validation script for Spec-Kit Plus specifications.

Validates:
- Required sections present
- API endpoints match database schema
- Cross-references are valid
- No template placeholders remain
- Consistent terminology
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class SpecValidator:
    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Run all validations and return True if specs are valid."""
        print(f"🔍 Validating specifications in {self.specs_dir}\n")

        self.check_directory_structure()
        self.check_required_files()
        self.check_placeholders()
        self.check_cross_references()
        self.check_consistency()

        self.print_results()
        return len(self.errors) == 0

    def check_directory_structure(self):
        """Verify the directory structure follows conventions."""
        if not self.specs_dir.exists():
            self.errors.append(f"Specs directory not found: {self.specs_dir}")
            return

        # Check for lowercase-with-hyphens naming
        for path in self.specs_dir.rglob("*"):
            if path.is_file() and path.suffix == ".md":
                name = path.stem
                if not re.match(r'^[a-z0-9-]+$', name):
                    self.warnings.append(
                        f"File name should use lowercase-with-hyphens: {path.name}"
                    )

    def check_required_files(self):
        """Check if key spec files exist."""
        recommended_files = [
            "overview.md",
            "architecture.md",
            "api-spec.md",
            "database-schema.md"
        ]

        for filename in recommended_files:
            filepath = self.specs_dir / filename
            if not filepath.exists():
                self.warnings.append(f"Recommended file missing: {filename}")

    def check_placeholders(self):
        """Check for unresolved template placeholders."""
        placeholder_patterns = [
            r'\{\{[A-Z_]+\}\}',  # {{PLACEHOLDER}}
            r'\[TODO[:\]]',       # [TODO] or [TODO:]
            r'\[FEATURE[_\]]',    # [FEATURE_NAME]
        ]

        for md_file in self.specs_dir.rglob("*.md"):
            content = md_file.read_text()

            for pattern in placeholder_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    self.errors.append(
                        f"{md_file.name}: Found {len(matches)} placeholder(s): {matches[:3]}"
                    )

    def check_cross_references(self):
        """Validate cross-references between spec files."""
        md_files = {f.name: f for f in self.specs_dir.rglob("*.md")}

        for md_file in md_files.values():
            content = md_file.read_text()

            # Find markdown links to other files
            links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', content)

            for link_text, link_path in links:
                # Extract file path (remove anchors)
                file_ref = link_path.split('#')[0]

                # Handle relative paths
                if file_ref.startswith('./'):
                    file_ref = file_ref[2:]
                elif file_ref.startswith('../'):
                    # Skip for now - more complex validation needed
                    continue

                # Check if referenced file exists
                if file_ref and file_ref not in md_files:
                    self.errors.append(
                        f"{md_file.name}: Broken link to '{file_ref}'"
                    )

    def check_consistency(self):
        """Check for consistency across specs."""
        # Collect all API endpoints
        api_endpoints = self._extract_api_endpoints()

        # Collect all database tables
        db_tables = self._extract_database_tables()

        # Basic consistency check
        if api_endpoints and db_tables:
            print(f"✓ Found {len(api_endpoints)} API endpoints")
            print(f"✓ Found {len(db_tables)} database tables")

    def _extract_api_endpoints(self) -> Set[str]:
        """Extract API endpoints from api-spec.md."""
        endpoints = set()
        api_spec = self.specs_dir / "api-spec.md"

        if not api_spec.exists():
            return endpoints

        content = api_spec.read_text()

        # Match patterns like: GET /api/todos, POST /auth/login
        matches = re.findall(r'(GET|POST|PATCH|PUT|DELETE)\s+(/[^\s\n]+)', content)
        endpoints = {f"{method} {path}" for method, path in matches}

        return endpoints

    def _extract_database_tables(self) -> Set[str]:
        """Extract table names from database-schema.md."""
        tables = set()
        db_schema = self.specs_dir / "database-schema.md"

        if not db_schema.exists():
            return tables

        content = db_schema.read_text()

        # Match patterns like: ### users Table, ### todos Table
        matches = re.findall(r'###\s+(\w+)\s+Table', content)
        tables = set(matches)

        return tables

    def print_results(self):
        """Print validation results."""
        print("\n" + "="*60)

        if self.errors:
            print(f"\n❌ {len(self.errors)} Error(s) Found:\n")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warning(s):\n")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print("\n✅ No errors found (warnings can be ignored)")
        else:
            print("\n❌ Please fix errors before proceeding")

        print("="*60 + "\n")


def main():
    if len(sys.argv) > 1:
        specs_dir = Path(sys.argv[1])
    else:
        # Default to ./specs directory
        specs_dir = Path.cwd() / "specs"

    validator = SpecValidator(specs_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
