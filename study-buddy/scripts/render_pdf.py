"""Render a prep-pack HTML file to PDF with whatever engine is available.

Tries, in order: Playwright (Chromium), a Chrome/Chromium/Edge binary in
headless mode, WeasyPrint, wkhtmltopdf. Optionally writes PNG previews of
every page (pdftoppm or pypdfium2) so you can look at the result.

Usage:
  python render_pdf.py pack/02-core-guide.html [--out file.pdf] [--png-preview] [--engine NAME]
Exit code 2 means no engine was found: deliver the HTML and ask the learner
to open it in a browser and Print > Save as PDF (A4, background graphics on).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def try_playwright(html, pdf):
    from playwright.sync_api import sync_playwright  # noqa: import inside for optional dependency
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True)
        browser.close()


def find_chrome():
    names = ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge", "microsoft-edge"]
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    return next((c for c in candidates if os.path.exists(c)), None)


def try_chrome(html, pdf):
    exe = find_chrome()
    if not exe:
        raise RuntimeError("no Chrome/Chromium/Edge binary")
    with tempfile.TemporaryDirectory() as profile:
        cmd = [exe, "--headless=new", "--disable-gpu", "--no-sandbox", f"--user-data-dir={profile}",
               "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.resolve().as_uri()]
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError("Chrome produced no PDF")


def try_weasyprint(html, pdf):
    import weasyprint  # noqa
    weasyprint.HTML(filename=str(html), base_url=str(html.parent)).write_pdf(str(pdf))


def try_wkhtmltopdf(html, pdf):
    exe = shutil.which("wkhtmltopdf")
    if not exe:
        raise RuntimeError("no wkhtmltopdf")
    subprocess.run([exe, "--enable-local-file-access", "-s", "A4", "--print-media-type", str(html), str(pdf)],
                   check=True, capture_output=True, timeout=180)


ENGINES = {"playwright": try_playwright, "chrome": try_chrome, "weasyprint": try_weasyprint, "wkhtmltopdf": try_wkhtmltopdf}


def previews(pdf, dpi=60):
    outdir = pdf.with_suffix("")
    outdir = outdir.parent / (outdir.name + "-preview")
    outdir.mkdir(exist_ok=True)
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(outdir / "page")], check=True)
        return outdir
    try:
        import pypdfium2 as pdfium  # noqa
        doc = pdfium.PdfDocument(str(pdf))
        for i in range(len(doc)):
            doc[i].render(scale=dpi / 72).to_pil().save(outdir / f"page-{i + 1:02d}.png")
        return outdir
    except Exception as error:  # previews are optional
        print(f"no preview tool ({error}); open the PDF to check it", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--engine", choices=list(ENGINES))
    ap.add_argument("--png-preview", action="store_true")
    args = ap.parse_args()
    if not args.html.exists():
        sys.exit(f"not found: {args.html}")
    pdf = args.out or args.html.with_suffix(".pdf")
    order = [args.engine] if args.engine else list(ENGINES)
    errors = []
    for name in order:
        try:
            ENGINES[name](args.html, pdf)
            print(f"rendered {pdf} with {name}")
            break
        except Exception as error:
            errors.append(f"{name}: {str(error).splitlines()[0] if str(error) else type(error).__name__}")
    else:
        print("No PDF engine worked:\n  " + "\n  ".join(errors), file=sys.stderr)
        print("Deliver the HTML and ask the learner to Print > Save as PDF (A4, background graphics on).", file=sys.stderr)
        sys.exit(2)
    if args.png_preview:
        out = previews(pdf)
        if out:
            print(f"previews in {out}")


if __name__ == "__main__":
    main()
