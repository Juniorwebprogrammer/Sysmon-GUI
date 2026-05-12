from unittest.mock import MagicMock, patch

import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

Gtk.init_check()

from app.domain.process_info import ProcessInfo
from app.presentation.widgets.process_panel import ProcessPanel


class TestProcessPanel:
    @pytest.fixture
    def panel(self):
        panel = ProcessPanel()
        panel._expanded = True
        return panel

    def test_creation(self, panel):
        assert isinstance(panel, Gtk.Box)

    def test_update_adds_processes(self, panel):
        processes = [
            ProcessInfo(pid=1, name="python", cpu_percent=50.0, mem_percent=10.0),
            ProcessInfo(pid=2, name="chrome", cpu_percent=30.0, mem_percent=20.0),
        ]
        panel.update(processes)
        data_store = panel._store
        assert len(data_store) == 2
        assert data_store[0][1] == "python"

    def test_update_replaces_previous(self, panel):
        panel.update(
            [ProcessInfo(pid=1, name="old", cpu_percent=10.0, mem_percent=5.0)]
        )
        panel.update(
            [ProcessInfo(pid=2, name="new", cpu_percent=20.0, mem_percent=8.0)]
        )
        assert panel._store[0][1] == "new"
        assert len(panel._store) == 1

    def test_update_empty(self, panel):
        panel.update([])
        assert len(panel._store) == 0

    def test_update_with_resize_callback(self):
        callback = MagicMock()
        panel = ProcessPanel(on_resize_callback=callback)
        panel._expanded = True
        processes = [
            ProcessInfo(pid=1, name="test", cpu_percent=10.0, mem_percent=5.0)
        ]
        panel.update(processes)
        assert len(panel._store) == 1

    def test_update_when_collapsed_does_nothing(self):
        panel = ProcessPanel()
        panel._expanded = False
        panel.update(
            [ProcessInfo(pid=1, name="x", cpu_percent=1.0, mem_percent=1.0)]
        )
        assert len(panel._store) == 0

    def test_default_state_is_collapsed(self):
        panel = ProcessPanel()
        assert panel._expanded is False
        assert panel._revealer.get_reveal_child() is False

    def test_toggle_expands_panel(self):
        panel = ProcessPanel()
        panel._on_toggle(panel._toggle_btn)
        assert panel._expanded is True
        assert panel._revealer.get_reveal_child() is True

    def test_toggle_collapses_panel(self):
        panel = ProcessPanel()
        panel._on_toggle(panel._toggle_btn)
        panel._on_toggle(panel._toggle_btn)
        assert panel._expanded is False
        assert panel._revealer.get_reveal_child() is False

    def test_toggle_changes_button_label(self):
        panel = ProcessPanel()
        assert "\u25b8" in panel._toggle_btn.get_label()
        panel._on_toggle(panel._toggle_btn)
        assert "\u25be" in panel._toggle_btn.get_label()
        panel._on_toggle(panel._toggle_btn)
        assert "\u25b8" in panel._toggle_btn.get_label()

    def test_toggle_with_resize_callback(self):
        callback = MagicMock()
        panel = ProcessPanel(on_resize_callback=callback)
        with patch("app.presentation.widgets.process_panel.GLib") as mock_glib:
            mock_glib.timeout_add = MagicMock()
            panel._on_toggle(panel._toggle_btn)
            mock_glib.timeout_add.assert_called_once_with(300, callback)

    def test_format_float_formats_to_two_decimals(self, panel):
        from gi.repository import GObject

        tree_column = MagicMock()
        cell_renderer = MagicMock()
        tree_model = panel._store
        tree_iter = tree_model.append([1, "test", 50.0, 10.0])

        # Test CPU% column (index 2)
        panel._format_float(tree_column, cell_renderer, tree_model, tree_iter, 2)
        cell_renderer.set_property.assert_called_once_with("text", "50.00")

        # Test MEM% column (index 3)
        cell_renderer.reset_mock()
        panel._format_float(tree_column, cell_renderer, tree_model, tree_iter, 3)
        cell_renderer.set_property.assert_called_once_with("text", "10.00")
