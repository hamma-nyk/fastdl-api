from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import asyncio
import os

app = FastAPI()

async def scrape_fastdl(target: str, mode: str):
    target_endpoint = "/postsV2" if mode == "posts" else "/userInfo"
    
    async with async_playwright() as p:
        # 1. Launch Browser dengan argumen optimasi
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # Sembunyikan tanda bot
            ]
        )
        
        # 2. Setup Context dengan User-Agent asli
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()

        # 3. AKTIFKAN STEALTH MODE
        # Ini akan menyembunyikan properti webdriver dan memperbaiki fingerprint browser
        #await stealth_async(page)
        
        api_data = {"result": None}

        # Listener untuk menangkap JSON
        async def handle_response(response):
            if target_endpoint in response.url:
                try:
                    api_data["result"] = await response.json()
                except:
                    pass

        page.on("response", handle_response)
        
        try:
            # 4. Blokir resource berat (Gambar/Ads) untuk menghemat RAM Render
            await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,otf}", lambda route: route.abort())

            # 5. Jalankan proses navigasi
            await page.goto("https://fastdl.app/en", wait_until="networkidle", timeout=60000)
            
            # Tunggu form muncul
            await page.wait_for_selector("#search-form-input", timeout=10000)
            await page.fill("#search-form-input", target)
            
            # Gunakan delay kecil saat klik agar lebih manusiawi
            await page.click(".search-form__button")

            # 6. Polling sampai data dapat (max 30 detik)
            for _ in range(30): 
                if api_data["result"]: 
                    break
                await asyncio.sleep(1)
            
            return api_data["result"]
            
        except Exception as e:
            print(f"Error Scraper: {e}")
            return None
        finally:
            await browser.close()

@app.get("/info")
async def get_info(user: str = Query(..., example="siputzx_")):
    data = await scrape_fastdl(user, mode="info")
    return data or {"error": "Gagal mendapatkan data user info"}

@app.get("/posts")
async def get_posts(user: str = Query(..., example="siputzx_")):
    data = await scrape_fastdl(user, mode="posts")
    return data or {"error": "Gagal mendapatkan data postingan"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)