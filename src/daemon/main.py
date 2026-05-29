import os
import time
import socket
import subprocess
from pathlib import Path

SOCKET_PATH = "/run/zena-setup.sock"


def execute_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )

    output = f"exit {result.returncode}\n"
    output += result.stdout
    output += result.stderr
    return output


import os
import subprocess
from pathlib import Path


def create_user(fullname, username, homesize, password) -> str:
    output = ""

    try:
        subprocess.run(
            ["/usr/sbin/setenforce", "0"],
            check=False,
            capture_output=True,
            text=True,
        )

        cmd = [
            "/usr/bin/homectl",
            "create",
            "--enforce-password-policy=no",
            "--password-change-now=false",
            username,
            "--storage=luks",
            "--fs-type=btrfs",
            f"--disk-size={homesize}G",
            "--auto-resize-mode=shrink-and-grow",
            "--member-of=wheel,users,libvirt,kvm",
            f"--real-name={fullname}",
            "--luks-extra-mount-options=acl,compress=zstd,user_subvol_rm_allowed,defcontext=system_u:object_r:user_home_dir_t:s0"
        ]

        env = {
            "NEWPASSWORD": password,
            **os.environ
        }

        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
        )

        output += f"exit {result.returncode}\n"
        output += result.stdout
        output += result.stderr

    finally:
        subprocess.run(
            ["/usr/sbin/setenforce", "1"],
            check=False,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["/usr/bin/restorecon", "-RFv", "/var/home"],
            check=False,
            capture_output=True,
            text=True,
        )

        Path("/var/lib/zena-setup.done").touch()

    return output


def exit_setup():
    try:
        subprocess.run(['pkill', '-u', 'zena-setup', 'niri'])
        time.sleep(1)
        subprocess.run(['userdel', '-r', 'zena-setup'])
        subprocess.Popen(
            ['systemctl', 'reboot'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except subprocess.CalledProcessError as e:
        print(f"Error exiting: {e}")


def handle_request(request: str) -> str:
    try:
        tokens = request.split()
        command = tokens[0]

        match command:
            case "localectl":
                return execute_command(tokens)
            case "timedatectl":
                return execute_command(tokens)
            case "create-user":
                args = request.split(" ", 1)[1].split(":", 3)
                fullname, username, homesize, password = args
                return create_user(fullname, username, homesize, password)
            case "exit":
                exit_setup()
            case _:
                return "error: unknown command\n"

    except Exception as exc:
        return f"error: {exc}\n"


def accept_client_connections(server_socket: socket.socket) -> None:
    while True:
        conn, _ = server_socket.accept()
        with conn:
            request = conn.recv(4096).decode().strip()
            if not request:
                continue

            print(f"Received request: {request}")
            reply = handle_request(request)
            conn.sendall(reply.encode())


def start_daemon() -> None:
    try:
        os.remove(SOCKET_PATH)
    except FileNotFoundError:
        pass

    os.makedirs(os.path.dirname(SOCKET_PATH), exist_ok=True)

    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(SOCKET_PATH)
    server_socket.listen(1)

    os.chmod(SOCKET_PATH, 0o666)

    print(f"zena-setup daemon listening on {SOCKET_PATH}")
    accept_client_connections(server_socket)


if __name__ == "__main__":
    start_daemon()
