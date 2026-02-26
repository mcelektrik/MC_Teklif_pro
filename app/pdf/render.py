import os
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from app.core.schema import Offer
from app.core.settings import DOCUMENTS_DIR

# Determine where templates are located
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = Path(sys._MEIPASS) / "app" / "pdf"
    # Set Playwright Browsers Path for frozen app
    # We assume browsers are located in a 'browsers' folder next to the executable
    # or inside _MEIPASS if we bundle them there.
    # For onefile, it's better to bundle them or put them next to exe.
    # Let's assume we put them in 'browsers' folder next to the installed exe.
    
    # However, standard Playwright behavior looks for env var.
    # If we ship 'ms-playwright' folder, we need to point to it.
    
    # Strategy:
    # 1. Check if 'ms-playwright' exists next to executable (installed app)
    # 2. If so, set env var.
    
    exe_dir = Path(sys.executable).parent
    local_browsers = exe_dir / "ms-playwright"
    if local_browsers.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(local_browsers)
    
else:
    BASE_DIR = Path(__file__).parent

TEMPLATE_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"

def render_html(offer: Offer, settings: dict) -> str:
    """
    Renders the HTML content using Jinja2.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("offer.html")
    
    # CSS Path needs to be absolute for Playwright to find it locally or embedded
    css_path = (ASSETS_DIR / "default.css").as_uri()
    
    # Prepare context
    # Convert image paths to file URIs if they exist
    logo_path = settings.get("logo_path")
    if logo_path and os.path.exists(logo_path):
        settings["logo_path"] = Path(logo_path).as_uri()
    
    signature_path = settings.get("signature_path")
    if signature_path and os.path.exists(signature_path):
        settings["signature_path"] = Path(signature_path).as_uri()
        
    return template.render(offer=offer, settings=settings, css_path=css_path)

def generate_pdf(offer: Offer, settings: dict, output_path: Path = None) -> Path:
    """
    Generates a PDF file from the offer.
    If output_path is not provided, it generates one based on the convention.
    """
    html_content = render_html(offer, settings)
    
    if output_path is None:
        # Create directory: Documents/MC_Teklif/YYYY-MM/CUSTOMER_NAME/
        date_str = offer.created_at.strftime("%Y-%m")
        customer_name = offer.customer.name.replace(" ", "_") if offer.customer else "Unknown"
        # Sanitize filename
        customer_name = "".join(c for c in customer_name if c.isalnum() or c in ('_', '-'))
        
        target_dir = DOCUMENTS_DIR / date_str / customer_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # File name: MC_ELEKTRIK_TE_KLF_{teklifNo}_v{n}.pdf
        base_name = f"MC_ELEKTRIK_TE_KLF_{offer.offer_no}"
        
        # Versioning logic
        version = 1
        while True:
            suffix = f"_v{version}" if version > 1 else ""
            file_name = f"{base_name}{suffix}.pdf"
            output_path = target_dir / file_name
            if not output_path.exists():
                break
            version += 1
            
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        page.pdf(path=str(output_path), format="A4", print_background=True, margin={
            "top": "20mm",
            "bottom": "20mm",
            "left": "20mm",
            "right": "20mm"
        })
        browser.close()
        
    return output_path
