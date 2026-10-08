"""Browser automation via Playwright.

Keeps one persistent browser/page across calls within a run so a sequence
like navigate -> click -> read_text behaves like a real session.
"""
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
from jarvis.config import load_config

_playwright = None
_browser = None
_page = None


class DomainNotAllowed(Exception):
    pass


def _check_domain(url: str):
    cfg = load_config()
    allowed = cfg.get("browser", {}).get("allowed_domains", [])
    if not allowed:
        return  # empty allowlist = unrestricted
    host = urlparse(url).netloc
    if not any(host == d or host.endswith("." + d) for d in allowed):
        raise DomainNotAllowed(f"'{host}' is not in browser.allowed_domains: {allowed}")


def _ensure_page():
    global _playwright, _browser, _page
    if _page is None:
        cfg = load_config()
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=cfg.get("browser", {}).get("headless", False))
        _page = _browser.new_page()
    return _page


def browser_navigate(url: str) -> str:
    _check_domain(url)
    page = _ensure_page()
    page.goto(url, wait_until="domcontentloaded")
    return f"navigated to {url}"


def browser_click(selector: str) -> str:
    page = _ensure_page()
    page.click(selector, timeout=5000)
    return f"clicked {selector}"


def browser_type(selector: str, text: str) -> str:
    page = _ensure_page()
    page.fill(selector, text, timeout=5000)
    return f"typed into {selector}"


def browser_read_text(selector: str = "body") -> str:
    page = _ensure_page()
    return page.inner_text(selector)


def browser_close():
    global _playwright, _browser, _page
    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()
    _browser = _page = _playwright = None
