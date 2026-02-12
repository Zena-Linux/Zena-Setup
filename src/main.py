import time
import threading
from waitress import serve
from api import create_app

import gi
gi.require_version('Gtk', '4.0')
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, WebKit, GLib, Gio


PORT = 8080


def start_flask_server():
    """Start Flask server with all API routes"""
    app = create_app()
    serve(app, host='127.0.0.1', port=PORT, threads=8)


flask_thread = threading.Thread(target=start_flask_server, daemon=True)
flask_thread.start()
time.sleep(0.5)


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__()

        self.set_titlebar(None)
        self.set_decorated(False)

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        settings.set_enable_developer_extras(True)

        self.webview.load_uri(f"http://127.0.0.1:{PORT}")
        self.set_child(self.webview)
        self.fullscreen()

        self.connect("destroy", self.on_destroy)
        self.webview.connect("load-failed", self.on_load_failed)

    def on_destroy(self, widget):
        app = self.get_application()
        if app:
            app.quit()
        else:
            Gtk.Window.do_destroy(self)

    def on_load_failed(self, webview, load_event, failing_uri, error):
        print(f"Failed to load: {failing_uri}")
        print(f"Error: {error.message}")
        GLib.timeout_add_seconds(
            1, lambda: webview.load_uri(f"http://127.0.0.1:{PORT}"))
        return True


def main():
    """Start the application"""
    app = Gtk.Application(application_id="com.zena.setup")
    app.connect("activate", on_activate)
    return app.run(None)


def on_activate(app):
    """Called when the application is activated"""
    win = MainWindow()
    win.set_application(app)
    win.present()


if __name__ == "__main__":
    main()
