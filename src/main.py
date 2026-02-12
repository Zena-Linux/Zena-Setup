import sys
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, WebKit, GLib


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_titlebar(None)
        self.set_decorated(False)
        self.fullscreen()

        self.user_content = WebKit.UserContentManager()
        self.webview = WebKit.WebView(user_content_manager=self.user_content)

        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(True)
        self.webview.set_settings(settings)

        self.user_content.register_script_message_handler("pythonHandler")
        self.user_content.connect("script-message-received::pythonHandler",
                                  self.on_ui_message)

        html_path = Path(__file__).parent / "ui" / "index.html"
        self.webview.load_uri(f"file://{html_path}")

        self.set_child(self.webview)

        self.connect("destroy", self.on_destroy)
        self.webview.connect("load-failed", self.on_load_failed)

    def on_ui_message(self, user_content, js_result):
        message = js_result.to_string()
        print(f"Message from JS: {message}")

        if message == "get_data":
            self.send_to_ui("Hello from Python!")
        elif message.startswith("add:"):
            _, a, b = message.split(":")
            result = int(a) + int(b)
            self.send_to_ui(f"Result: {result}")

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


def on_activate(app):
    win = MainWindow()
    win.set_application(app)
    win.present()


def main():
    app = Gtk.Application()
    app.connect("activate", on_activate)
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
