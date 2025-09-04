
import unittest
from unittest.mock import patch
import tempfile
import shutil
from pathlib import Path

from shortcut_generator.config_writer import (
    ensure_source_in_rc,
    add_alias_line,
    get_shortcuts_path,
    SOURCE_BLOCK_HEADER,
    SOURCE_BLOCK_FOOTER,
    SHORTCUTS_FILENAME,
)

class TestConfigWriter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.home_patch = patch('pathlib.Path.home', return_value=Path(self.test_dir))
        self.home_patch.start()
        self.rc_path = Path.home() / ".testrc"
        self.shortcuts_path = Path.home() / SHORTCUTS_FILENAME

    def tearDown(self):
        self.home_patch.stop()
        shutil.rmtree(self.test_dir)

    def test_get_shortcuts_path(self):
        """Test that get_shortcuts_path returns the correct path inside the mocked home."""
        expected_path = Path(self.test_dir) / SHORTCUTS_FILENAME
        self.assertEqual(get_shortcuts_path(), expected_path)

    def test_ensure_source_in_rc_creates_file(self):
        """Test that ensure_source_in_rc creates the RC file if it doesn't exist."""
        self.assertFalse(self.rc_path.exists())
        ensure_source_in_rc(self.rc_path, self.shortcuts_path)
        self.assertTrue(self.rc_path.exists())

    def test_ensure_source_in_rc_adds_block(self):
        """Test that the source block is added to a file without it."""
        self.rc_path.write_text("initial_content\n")
        ensure_source_in_rc(self.rc_path, self.shortcuts_path)
        content = self.rc_path.read_text()
        self.assertIn(SOURCE_BLOCK_HEADER, content)
        self.assertIn(f'source "{self.shortcuts_path}"', content)
        self.assertIn(SOURCE_BLOCK_FOOTER, content)

    def test_ensure_source_in_rc_is_idempotent(self):
        """Test that no changes are made if the block already exists."""
        source_line = f'source "{self.shortcuts_path}"'
        initial_content = f"{SOURCE_BLOCK_HEADER}\n{source_line}\n{SOURCE_BLOCK_FOOTER}"
        self.rc_path.write_text(initial_content)
        ensure_source_in_rc(self.rc_path, self.shortcuts_path)
        self.assertEqual(self.rc_path.read_text(), initial_content)
        backups = list(Path(self.test_dir).glob(".testrc.bak-*"))
        self.assertEqual(len(backups), 0)

    def test_ensure_source_in_rc_creates_backup(self):
        """Test that a backup is created when the RC file is modified."""
        self.rc_path.write_text("some content")
        ensure_source_in_rc(self.rc_path, self.shortcuts_path)
        backups = list(Path(self.test_dir).glob(".testrc.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "some content")

    def test_add_alias_line_creates_file(self):
        """Test that add_alias_line creates the shortcuts file if it doesn't exist."""
        self.assertFalse(self.shortcuts_path.exists())
        add_alias_line(self.shortcuts_path, "alias gs='git status'")
        self.assertTrue(self.shortcuts_path.exists())
        self.assertIn("alias gs='git status'", self.shortcuts_path.read_text())

    def test_add_alias_line_appends_new_alias(self):
        """Test that a new alias is appended to the shortcuts file."""
        self.shortcuts_path.write_text("alias ga='git add'\n")
        add_alias_line(self.shortcuts_path, "alias gc='git commit'")
        content = self.shortcuts_path.read_text()
        self.assertIn("alias ga='git add'", content)
        self.assertIn("alias gc='git commit'", content)

    def test_add_alias_line_updates_existing_alias(self):
        """Test that an existing alias is updated."""
        self.shortcuts_path.write_text("alias gco='git checkout'\n")
        add_alias_line(self.shortcuts_path, "alias gco='git checkout -b'")
        content = self.shortcuts_path.read_text()
        self.assertNotIn("alias gco='git checkout'\n", content)
        self.assertIn("alias gco='git checkout -b'", content)

    def test_add_alias_line_is_idempotent(self):
        """Test that no changes are made if the exact alias already exists."""
        initial_content = "alias gl='git log'\n"
        self.shortcuts_path.write_text(initial_content)
        add_alias_line(self.shortcuts_path, "alias gl='git log'")
        self.assertEqual(self.shortcuts_path.read_text(), initial_content)

if __name__ == '__main__':
    unittest.main()
