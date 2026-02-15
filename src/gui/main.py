import sys
import shutil
import atexit
import zipfile
import tempfile
import threading
from pathlib import Path
from core import (send_locale_list, send_keymap_list,
                  send_timezone_list, send_free_space,
                  apply_locale, apply_keymap,
                  apply_timezone, create_user, exit_gui)

from ctypes import CDLL
CDLL('libgtk4-layer-shell.so.0')

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Gdk, Gtk4LayerShell, WebKit, GLib


class CommandThread(threading.Thread):
    def __init__(self, func, args=(), kwargs={}):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.daemon = True

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Thread error: {e}")


class MainWindow(Gtk.Window):
    def __init__(self, html_uri):
        super().__init__()
        self.thread_pool = []

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_exclusive_zone(self, -1)
        Gtk4LayerShell.set_keyboard_mode(self,
                                         Gtk4LayerShell.KeyboardMode.EXCLUSIVE)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            window {
                background-color: black;
            }
        """)

        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        self.set_titlebar(None)
        self.set_decorated(False)

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

        controller = Gtk.EventControllerKey.new()
        controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(controller)

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_q and (state & Gdk.ModifierType.ALT_MASK):
            self.close()
            return True
        return False

    def run_thread(self, func, *args, **kwargs):
        thread = CommandThread(
            func=func,
            args=args,
            kwargs=kwargs
        )
        thread.start()
        self.thread_pool.append(thread)
        self.thread_pool = [t for t in self.thread_pool if t.is_alive()]

    def on_ui_request(self, user_content, js_result):
        request = js_result.to_string()
        print(f"Request from UI: {request}")

        tokens = request.split(":", 1)

        match tokens:
            case ["get_locale_list"]:
                GLib.idle_add(lambda: send_locale_list(self))
            case ["post_locale", locale]:
                GLib.idle_add(lambda: apply_locale(self, locale))
            case ["get_keymap_list"]:
                GLib.idle_add(lambda: send_keymap_list(self))
            case ["post_keymap", keymap]:
                GLib.idle_add(lambda: apply_keymap(self, keymap))
            case ["get_timezone_list"]:
                GLib.idle_add(lambda: send_timezone_list(self))
            case ["post_timezone", timezone]:
                GLib.idle_add(lambda: apply_timezone(self, timezone))
            case ["get_free_space"]:
                GLib.idle_add(lambda: send_free_space(self))
            case ["post_user", args]:
                self.run_thread(create_user, self, args)
            case ["exit"]:
                GLib.idle_add(lambda: exit_gui())
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
