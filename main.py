import os
import time
import requests
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(BASE_DIR, "pw-browsers")
OUTPUT_DIR = "images"
RESIZE_DIR = "images_resize"

def crop_to_square(filepath, filename):
    try:
        if filepath.lower().endswith('.svg'):
            return

        with Image.open(filepath) as img:
            width, height = img.size
            resize_path = os.path.join(RESIZE_DIR, filename)
            
            if width == height:
                img.save(resize_path)
                return

            if width > height:
                left = (width - height) // 2
                right = left + height
                top = 0
                bottom = height
            else:
                top = (height - width) // 2
                bottom = top + width
                left = 0
                right = width

            img_cropped = img.crop((left, top, right, bottom))
            img_cropped.save(resize_path)
            
    except Exception as e:
        print(f"  [Crop error] Failed to crop {filename}: {e}")

def download_image(url, filepath):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://tiermaker.com/",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status() 
        
        content_type = response.headers.get('Content-Type', '').lower()
        if 'image' not in content_type:
            return False
            
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) < 500: 
             return False

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  [Error] Failed to download {url}: {e}")
        return False

def scroll_progressively(page):
    print("[Playwright] Starting progressive scroll to trigger lazy loading...")
    
    last_height = 0
    scroll_attempts = 0
    
    while True:
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        time.sleep(0.5) 
        
        new_height = page.evaluate("window.scrollY + window.innerHeight")
        document_height = page.evaluate("document.body.scrollHeight")
        
        if new_height >= document_height:
            scroll_attempts += 1
            time.sleep(1)
            if scroll_attempts >= 3: 
                break
        else:
            scroll_attempts = 0
            
        last_height = new_height
        
    print("[Playwright] Scrolling finished.")

def main():
    url_input = input("Please enter the URL: ")
    
    reponse_carre = input("Do you want to crop the images to a centered square format? (y/n): ").strip().lower()
    do_square_crop = reponse_carre in ['o', 'oui', 'y', 'yes']

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directory '{OUTPUT_DIR}' created.")

    if do_square_crop and not os.path.exists(RESIZE_DIR):
        os.makedirs(RESIZE_DIR)
        print(f"Directory '{OUTPUT_DIR}' created.")

    image_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        def handle_response(response):
            if response.request.resource_type == "image":
                url = response.url
                if not url.startswith("data:image"):
                    image_urls.add(url)

        page.on("response", handle_response)

        print(f"[Playwright] Opening page: {url_input}")
        page.goto(url_input, wait_until="networkidle") 

        scroll_progressively(page)
        
        print("[Playwright] Final extraction from the DOM...")
        img_elements = page.locator("img").element_handles()
        for img in img_elements:
            src = img.get_attribute("src")
            data_src = img.get_attribute("data-src")
            
            final_src = data_src if data_src else src
            if final_src and not final_src.startswith("data:image"):
                absolute_url = urljoin(url_input, final_src)
                image_urls.add(absolute_url)

        browser.close()

    print(f"\n:Extraction complete! {len(image_urls)} unique images found.")
    print("Starting download...\n")

    success_count = 0
    for i, img_url in enumerate(image_urls, start=1):
        parsed = urlparse(img_url)
        ext = os.path.splitext(parsed.path)[1].lower()
        
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']:
            ext = '.png'
            
        filename = f"img_{i}{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        print(f"[{i}/{len(image_urls)}] Downloading {filename}...")
        
        if download_image(img_url, filepath):
            success_count += 1
            if do_square_crop:
                crop_to_square(filepath, filename)
            
    print(f"\nOperation completed successfully! {success_count}/{len(image_urls)} images saved.")

if __name__ == "__main__":
    main()