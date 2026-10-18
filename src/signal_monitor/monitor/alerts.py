import json
import urllib.request


def alert(signal):
    try:
        payload = json.dumps({"text": f"{signal.side} {signal.strategy} @ {signal.price}"}).encode()
        req = urllib.request.Request(
            "https://api.telegram.org/bot<TOKEN>/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass
