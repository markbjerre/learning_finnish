"""
Frontend tests for Learning Finnish app using Playwright.

Tests the React app rendering in src/App.tsx, including:
- Page title and heading visibility
- Subtitle content
- CSS gradient background styling
- DOM structure and root element

Run with: python tests/playwright/test_frontend.py
Or with pytest: pytest tests/playwright/test_frontend.py

Requires:
- BASE_URL defined in conftest.py
- Playwright sync_api installed
- React dev server running
"""

import sys
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")
from conftest import BASE_URL


def test_heading_visible():
    """Test that h1 is visible and contains 'Learning Finnish'."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            h1 = page.locator("h1")
            assert h1.is_visible(), "h1 element is not visible"
            assert h1.text_content() == "Learning Finnish", f"h1 text is '{h1.text_content()}', expected 'Learning Finnish'"
            print("✓ test_heading_visible passed")
        finally:
            browser.close()


def test_subtitle_visible():
    """Test that p element is visible and contains 'Skeleton'."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            p_elem = page.locator("p")
            assert p_elem.is_visible(), "p element is not visible"
            text = p_elem.text_content()
            assert "Skeleton" in text, f"'Skeleton' not found in paragraph text: '{text}'"
            print("✓ test_subtitle_visible passed")
        finally:
            browser.close()


def test_gradient_background():
    """Test that body backgroundImage contains 'gradient' via page.evaluate."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            background_image = page.evaluate("window.getComputedStyle(document.body).backgroundImage")
            assert "gradient" in background_image.lower(), f"'gradient' not found in backgroundImage: '{background_image}'"
            print("✓ test_gradient_background passed")
        finally:
            browser.close()


def test_root_element_exists():
    """Test that #root exists and has non-empty innerHTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            root = page.locator("#root")
            assert root.count() > 0, "#root element not found"
            inner_html = page.locator("#root").evaluate("el => el.innerHTML")
            assert inner_html.strip(), "#root has empty innerHTML"
            print("✓ test_root_element_exists passed")
        finally:
            browser.close()


def test_page_title():
    """Test that page.title() equals 'Learning Finnish'."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="networkidle")
            title = page.title()
            assert title == "Learning Finnish", f"page title is '{title}', expected 'Learning Finnish'"
            print("✓ test_page_title passed")
        finally:
            browser.close()


if __name__ == "__main__":
    tests = [
        test_heading_visible,
        test_subtitle_visible,
        test_gradient_background,
        test_root_element_exists,
        test_page_title,
    ]

    failures = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failures += 1

    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(failures)
