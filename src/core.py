import subprocess


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
