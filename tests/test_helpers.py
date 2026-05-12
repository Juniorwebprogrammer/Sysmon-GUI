from unittest.mock import patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.presentation.helpers import icon_path, load_css, load_pixbuf


class TestIconPath:
    def test_returns_installed_when_exists(self):
        with patch("app.presentation.helpers.os.path.exists") as mock_exists:
            mock_exists.return_value = True
            path = icon_path()
            assert "/usr/share/icons" in path

    def test_returns_local_when_installed_missing(self):
        with patch("app.presentation.helpers.os.path.exists") as mock_exists:
            mock_exists.return_value = False
            path = icon_path()
            assert "icon.png" in path


class TestLoadPixbuf:
    def test_returns_none_when_no_icon(self):
        with patch("app.presentation.helpers.os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch(
                "app.presentation.helpers.GdkPixbuf.Pixbuf.new_from_file_at_size",
                side_effect=Exception("no file"),
            ):
                result = load_pixbuf(size=22)
                assert result is None


class TestLoadCss:
    def test_loads_valid_css(self):
        result = load_css(b".test { color: red; }")
        assert result is None

    def test_loads_empty_css(self):
        result = load_css(b"")
        assert result is None
