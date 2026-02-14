import socket
import shutil
import subprocess

SOCKET_PATH = "/run/zena-setup.sock"


def send_command(command: str) -> str:
    try:
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(SOCKET_PATH)
        client_socket.sendall(command.encode())
        response = client_socket.recv(4096).decode()
        return response

    except FileNotFoundError:
        return f"Error: Daemon socket not found at {SOCKET_PATH}."
    except ConnectionRefusedError:
        return "Error: Connection refused."
    except Exception as e:
        return f"Error: {e}"
    finally:
        client_socket.close()


def send_locale_list(self):
    """Get list of available locales from localectl and send to UI"""
    try:
        result = subprocess.run(['localectl', 'list-locales'],
                                capture_output=True, text=True, check=True)
        locales = result.stdout.strip().split('\n')

        locales = [locale.strip() for locale in locales if locale.strip()]
        self.send_to_ui(f"locales:{','.join(locales)}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting locales: {e}")
        self.send_to_ui("locales:ERROR")
    except FileNotFoundError:
        print("localectl command not found")
        self.send_to_ui("locales:NOT_FOUND")


def apply_locale(self, locale):
    try:
        response = send_command(f"localectl set-locale LANG={locale}")
        print(response)
    except subprocess.CalledProcessError as e:
        print(f"Error getting locales: {e}")
    except FileNotFoundError:
        print("localectl command not found")


def send_keymap_list(self):
    """Get list of available keymaps from localectl and send to UI"""
    try:
        result = subprocess.run(['localectl', 'list-keymaps'],
                                capture_output=True, text=True, check=True)
        keymaps = result.stdout.strip().split('\n')
        keymaps = [keymap.strip() for keymap in keymaps if keymap.strip()]

        self.send_to_ui(f"keymaps:{','.join(keymaps)}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting keymaps: {e}")
        self.send_to_ui("keymaps:ERROR")
    except FileNotFoundError:
        print("localectl command not found")
        self.send_to_ui("keymaps:NOT_FOUND")


def apply_keymap(self, keymap):
    try:
        response = send_command(f"localectl set-keymap {keymap}")
        print(response)
    except subprocess.CalledProcessError as e:
        print(f"Error getting locales: {e}")
    except FileNotFoundError:
        print("localectl command not found")


def send_timezone_list(self):
    """Get list of available timezones from timedatectl and send to UI"""
    try:
        result = subprocess.run(['timedatectl', 'list-timezones'],
                                capture_output=True, text=True, check=True)
        timezones = result.stdout.strip().split('\n')
        timezones = [tz.strip() for tz in timezones if tz.strip()]

        self.send_to_ui(f"timezones:{','.join(timezones)}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting timezones: {e}")
        self.send_to_ui("timezones:ERROR")
    except FileNotFoundError:
        print("timedatectl command not found")
        self.send_to_ui("timezones:NOT_FOUND")


def apply_timezone(self, timezone):
    try:
        response = send_command(f"timedatectl set-timezone {timezone}")
        print(response)
    except subprocess.CalledProcessError as e:
        print(f"Error getting locales: {e}")
    except FileNotFoundError:
        print("localectl command not found")


def send_free_space(self=None):
    """Send free space in GB"""
    try:
        path = "/var"
        usage = shutil.disk_usage(path)

        free_gb = int(usage.free / (10**9))
        self.send_to_ui(f"free_space:{free_gb}")

    except Exception as e:
        print(f"Error: {e}")
        self.send_to_ui("free_space:ERROR")


def create_user(self, args):
    try:
        response = send_command(f"create-user {args}")
        print(response)
    except subprocess.CalledProcessError as e:
        print(f"Error getting locales: {e}")
    except FileNotFoundError:
        print("localectl command not found")
