import sys
import shutil
import atexit
import zipfile
import tempfile
from pathlib import Path
from core import (send_locale_list, send_keymap_list,
                  send_timezone_list, send_free_space)

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Gdk, WebKit, GLib


class MainWindow(Gtk.Window):
    def __init__(self, html_uri):
        super().__init__()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            window {
                background-color: black;
            }
        """)

        self.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.set_titlebar(None)
        self.set_decorated(False)
        self.fullscreen()

        self.user_content = WebKit.UserContentManager()
        self.webview = WebKit.WebView(user_content_manager=self.user_content)

        rgba = Gdk.RGBA()
        rgba.parse("black")
        self.webview.set_background_color(rgba)

        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(True)
        self.webview.set_settings(settings)

        self.user_content.register_script_message_handler("pythonHandler")
        self.user_content.connect("script-message-received::pythonHandler",
                                  self.on_ui_request)

        self.webview.load_uri(html_uri)
        self.set_child(self.webview)

        self.connect("destroy", self.on_destroy)
        self.webview.connect("load-failed", self.on_load_failed)

    def on_ui_request(self, user_content, js_result):
        request = js_result.to_string()
        print(f"Request from UI: {request}")

        match request:
            case "get_locale_list":
                GLib.idle_add(lambda: send_locale_list(self))
            case "get_keymap_list":
                GLib.idle_add(lambda: send_keymap_list(self))
            case "get_timezone_list":
                GLib.idle_add(lambda: send_timezone_list(self))
            case "get_free_space":
                GLib.idle_add(lambda: send_free_space(self))
            case _:
                print(f"Unknown request: {request}")

    def send_to_ui(self, text):
        script = f"window.receiveFromPython?.('{text}')"
        self.webview.evaluate_javascript(script, -1, None, None, None)

    def on_destroy(self, widget):
        app = self.get_application()
        if app:
            app.quit()
        else:
            Gtk.Window.do_destroy(self)

    def on_load_failed(self, webview, load_event, failing_uri, error):
        print(f"Failed to load: {failing_uri}")
        print(f"Error: {error.message}")
        GLib.timeout_add_seconds(1, lambda: webview.load_uri(failing_uri))
        return True


def get_ui():
    src = Path(__file__).parent / "ui"
    if src.exists():
        return src

    temp_dir = Path(tempfile.mkdtemp())
    atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

    with zipfile.ZipFile(sys.argv[0], "r") as zf:
        for member in zf.namelist():
            if member.startswith("ui/"):
                if member.endswith("/"):
                    continue
                rel_path = Path(member).relative_to("ui")
                target = temp_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(target, "wb") as dest:
                    shutil.copyfileobj(source, dest)
    return temp_dir


def on_activate(app):
    ui_path = get_ui()
    html_uri = (ui_path / "index.html").as_uri()

    window = MainWindow(html_uri)
    window.set_application(app)
    window.present()


def main():
    app = Gtk.Application()
    app.connect("activate", on_activate)
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
