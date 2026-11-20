from __future__ import annotations

import signal
import sys
import threading

from . import verification
from .config import Config
from .web import create_server


def _cleanup_loop(config: Config, stop: threading.Event) -> None:
    while not stop.wait(60):
        try:
            verification.cleanup(config)
        except Exception:
            # Cleanup must never take the service down.
            pass


def main() -> None:
    config = Config.from_env()
    for warning in config.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    server = create_server(config)
    stop = threading.Event()
    threading.Thread(
        target=_cleanup_loop, args=(config, stop), daemon=True, name="samsyn-cleanup"
    ).start()

    def shutdown(signum: int, frame: object) -> None:
        stop.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    host, port = server.server_address[:2]
    print(
        f"{config.app_name} {config.version} listening on http://{host}:{port} "
        f"(auth_mode={config.auth_mode})",
        flush=True,
    )
    print(f"Invitation base URL: {config.base_url}", flush=True)
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()


if __name__ == "__main__":
    main()
