#!/usr/bin/env python3
"""Offline checks for the deployable static Pages and PWA bundles."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import subprocess
import sys
import tempfile
from threading import Thread
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urljoin
from urllib.request import ProxyHandler, build_opener

BASE = "https://offline.invalid/LYWU/"
URL_ATTRS = {
    "a": ("href",), "link": ("href",), "script": ("src",),
    "img": ("src",), "iframe": ("src",), "source": ("src",),
    "video": ("src", "poster"), "audio": ("src",), "object": ("data",),
    "embed": ("src",), "use": ("href", "xlink:href"),
}
JS_TYPES = {"", "module", "text/javascript", "application/javascript"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.refs, self.scripts = [], []
        self.script = None
        self.roots = [0, 0, 0]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("html", "head", "body"):
            self.roots[("html", "head", "body").index(tag)] += 1
        self.refs.extend(attrs[attr] for attr in URL_ATTRS.get(tag, ()) if attrs.get(attr))
        if tag == "script" and not attrs.get("src") and (attrs.get("type") or "").lower() in JS_TYPES:
            self.script = (self.getpos()[0], attrs.get("type") == "module", [])

    def handle_data(self, data):
        if self.script is not None:
            self.script[2].append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append(self.script)
            self.script = None


def local_ref(source, ref):
    split = urlsplit(ref)
    if split.scheme or split.netloc or not split.path:
        return None
    absolute = urlsplit(urljoin(urljoin(BASE, source), ref)).path
    if not absolute.startswith("/LYWU/"):
        raise ValueError(f"{source}: local reference outside the GitHub Pages project: {ref}")
    path = unquote(absolute.removeprefix("/LYWU/"))
    parts = path.split("/")
    if any(p in (".", "..") for p in parts) or "\\" in path:
        raise ValueError(f"{source}: malformed local reference: {ref}")
    if not path or path.endswith("/"):
        path += "index.html"
    return path


def require_ref(source, ref, tracked):
    target = local_ref(source, ref)
    if target is not None and target not in tracked:
        raise ValueError(f"{source}: missing local reference: {target}")


def parse_page(text):
    page = Page()
    page.feed(text)
    page.close()
    if page.roots != [1, 1, 1] or page.script is not None:
        raise ValueError("document needs one html/head/body and closed script tags")
    return page


def checked(command, label):
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode:
        print(result.stderr.decode("utf-8", errors="replace")[:4000], file=sys.stderr)
        raise ValueError(f"{label}: syntax check failed")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def http_smoke(root, pages):
    """Fetch the index and each linked HTML page on an ephemeral loopback port."""
    with tempfile.TemporaryDirectory() as webroot:
        Path(webroot, "LYWU").symlink_to(root, target_is_directory=True)
        handler = partial(QuietHandler, directory=webroot)
        with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            origin = f"http://127.0.0.1:{server.server_port}/LYWU/"
            opener = build_opener(ProxyHandler({}))
            try:
                for page in sorted(pages):
                    with opener.open(origin + quote(page), timeout=5) as response:
                        if response.status != 200 or response.headers.get_content_type() != "text/html":
                            raise ValueError(f"{page}: could not serve as HTML")
                        if response.read() != (root / page).read_bytes():
                            raise ValueError(f"{page}: HTTP response differs from checked-in bundle")
            finally:
                server.shutdown()
                worker.join()
    print(f"Loopback smoke passed for {len(pages)} entry pages")


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"]).decode("utf-8").split("\0")
    tracked = set(filter(None, files))
    if "index.html" not in tracked:
        raise ValueError("main index.html is missing")
    entry_pages = {"index.html"}
    counts = {"html": 0, "inline scripts": 0, "js": 0, "manifest": 0, "shell": 0}
    with tempfile.TemporaryDirectory() as work:
        for path in sorted(tracked):
            source = Path(path)
            if source.suffix == ".html":
                try:
                    page = parse_page(source.read_text(encoding="utf-8"))
                except ValueError as err:
                    raise ValueError(f"{path}: {err}") from err
                for ref in page.refs:
                    require_ref(path, ref, tracked)
                if path == "index.html":
                    entry_pages.update(
                        target for ref in page.refs
                        if (target := local_ref(path, ref)) is not None and target.endswith(".html")
                    )
                    if len(entry_pages) < 2:
                        raise ValueError("main index.html does not link to an app")
                counts["html"] += 1
                for line, module, script in page.scripts:
                    if not "".join(script).strip():
                        continue
                    tmp = Path(work, "inline.mjs" if module else "inline.cjs")
                    tmp.write_text("".join(script), encoding="utf-8")
                    checked(["node", "--check", str(tmp)], f"{path}:{line}")
                    counts["inline scripts"] += 1
            elif source.suffix == ".js":
                checked(["node", "--check", path], path)
                counts["js"] += 1
            elif source.suffix == ".sh":
                checked(["bash", "-n", path], path)
                counts["shell"] += 1
            elif source.suffix == ".webmanifest":
                manifest = json.loads(source.read_text(encoding="utf-8"))
                if not isinstance(manifest.get("start_url"), str) or not manifest.get("icons"):
                    raise ValueError(f"{path}: missing manifest launch URL or icons")
                require_ref(path, manifest["start_url"], tracked)
                for icon in manifest["icons"]:
                    require_ref(path, icon["src"], tracked)
                counts["manifest"] += 1
    http_smoke(Path.cwd(), entry_pages)
    print("Validated " + ", ".join(f"{count} {kind}" for kind, count in counts.items()))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
