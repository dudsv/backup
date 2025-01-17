import asyncio
import aiohttp
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from lxml import etree
import time
from concurrent.futures import ThreadPoolExecutor

# Função para fechar popups de cookies
def close_cookie_popup(driver):
    try:
        cookie_selectors = [
            "//button[contains(text(), 'Aceitar')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'OK')]",
            "//div[contains(@class, 'cookie')]/button"
        ]
        for selector in cookie_selectors:
            try:
                cookie_button = driver.find_element(By.XPATH, selector)
                cookie_button.click()
                time.sleep(1)
                break
            except NoSuchElementException:
                continue
    except Exception:
        pass

# Função para capturar screenshots
def capture_full_page_screenshot(url, folder_path, width):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(2)
        close_cookie_popup(driver)

        driver.set_window_size(width, 1080)
        time.sleep(2)

        total_width = driver.execute_script("return document.body.scrollWidth")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(width, total_height)
        time.sleep(2)

        temp_path = os.path.join(folder_path, "temp_screenshot.png")
        driver.save_screenshot(temp_path)

        output_path = os.path.join(folder_path, f"screenshot_{width}px.png")
        with Image.open(temp_path) as img:
            cropped_image = img.crop((0, 0, width, total_height))
            cropped_image.save(output_path)
        os.remove(temp_path)

    except Exception as e:
        print(f"Erro ao capturar screenshot de {url}: {e}")
    finally:
        driver.quit()

# Função assíncrona para processar URLs
async def process_urls(urls, output_dir):
    async with aiohttp.ClientSession() as session:
        tasks = []
        with ThreadPoolExecutor() as executor:
            for url in urls:
                folder_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
                folder_path = os.path.join(output_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, capture_full_page_screenshot, url, folder_path, 1920
                    )
                )
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, capture_full_page_screenshot, url, folder_path, 1140
                    )
                )
            await asyncio.gather(*tasks)

# Função para extrair URLs de um sitemap
async def extract_sitemap_urls(sitemap_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(sitemap_url) as response:
            xml_content = await response.text()
            root = etree.fromstring(xml_content.encode("utf-8"))
            return [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]

# Interface gráfica com Tkinter
def run_gui():
    def start_process():
        urls = entry_urls.get("1.0", "end").strip().split("\n")
        sitemap_url = entry_sitemap.get().strip()
        output_dir = filedialog.askdirectory(title="Selecione o Diretório de Saída")

        if not output_dir:
            messagebox.showerror("Erro", "Por favor, selecione um diretório de saída.")
            return

        if sitemap_url:
            asyncio.run(run_sitemap_process(sitemap_url, output_dir))
        elif urls:
            asyncio.run(run_url_process(urls, output_dir))
        else:
            messagebox.showerror("Erro", "Insira URLs ou forneça um sitemap.")

    async def run_url_process(urls, output_dir):
        await process_urls(urls, output_dir)
        messagebox.showinfo("Sucesso", "Processo concluído!")

    async def run_sitemap_process(sitemap_url, output_dir):
        urls = await extract_sitemap_urls(sitemap_url)
        if urls:
            await process_urls(urls, output_dir)
            messagebox.showinfo("Sucesso", "Processo concluído!")
        else:
            messagebox.showerror("Erro", "Nenhuma URL encontrada no sitemap.")

    root = tk.Tk()
    root.title("Screenshot Automático")

    tk.Label(root, text="Insira URLs (uma por linha):").pack()
    entry_urls = tk.Text(root, height=10, width=50)
    entry_urls.pack()

    tk.Label(root, text="Ou forneça a URL do Sitemap:").pack()
    entry_sitemap = tk.Entry(root, width=50)
    entry_sitemap.pack()

    tk.Button(root, text="Iniciar Processo", command=start_process).pack()
    root.mainloop()

if __name__ == "__main__":
    run_gui()
