import os
import requests
from xml.etree import ElementTree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tkinter import Tk, Label, Text, Button, Scrollbar, messagebox
from tkinter.filedialog import askdirectory

# Função para capturar o screenshot
def capture_screenshot(url, folder_name):
    options = Options()
    options.headless = True  # Executar em modo headless (sem abrir o navegador)

    # Caminho para o ChromeDriver
    chromedriver_path = r'C:\chromium\chromedriver.exe'

    # Usando Service para especificar o caminho do ChromeDriver
    service = Service(chromedriver_path)
    
    # Inicia o driver com o caminho do ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # Cria a pasta se não existir
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Nome do arquivo para a captura da página completa
    full_page_file_name = os.path.join(folder_name, "full_page.png")
    # Nome do arquivo para a captura com largura de 1140px
    width_1140_file_name = os.path.join(folder_name, "width_1140px.png")

    # Captura da página completa ajustando a janela para a altura total da página
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1920, total_height)
    driver.get_screenshot_as_file(full_page_file_name)
    print(f"Screenshot da página completa salva em {full_page_file_name}")

    # Captura com largura de 1140px
    driver.set_window_size(1140, total_height)
    driver.get_screenshot_as_file(width_1140_file_name)
    print(f"Screenshot com largura de 1140px salva em {width_1140_file_name}")

    driver.quit()

# Função para pegar URLs de um sitemap
def get_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    sitemap = ElementTree.fromstring(response.content)
    urls = [url.find("loc").text for url in sitemap.findall(".//url")]

    # Exibe as URLs recuperadas para verificação
    print(f"URLs encontradas no sitemap: {urls}")
    return urls

# Função para limpar caracteres inválidos no nome do diretório
def clean_folder_name(url):
    # Substitui os caracteres inválidos para Windows por um sublinhado (_)
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        url = url.replace(char, "_")
    return url

# Função principal para processar as URLs inseridas
def process_urls():
    # Obtém o texto da caixa de entrada
    input_text = url_textbox.get("1.0", "end-1c")
    
    # Divide as URLs por linha
    urls = input_text.split("\n")
    
    if not urls or all(url.strip() == "" for url in urls):
        messagebox.showerror("Erro", "Por favor, insira pelo menos uma URL.")
        return
    
    # Solicita ao usuário a seleção de uma pasta de saída
    Tk().withdraw()  # Oculta a janela principal do Tkinter
    base_folder = askdirectory(title="Selecione a pasta para salvar as capturas de tela")

    # Verifica se o usuário selecionou uma pasta
    if not base_folder:
        print("Nenhuma pasta selecionada. O processo será encerrado.")
        return

    # Para cada URL, captura um screenshot
    for url in urls:
        url = url.strip()  # Remove espaços em branco no início e no final
        if url:
            print(f"Processando URL: {url}")
            
            # Verifica se a URL fornecida é um sitemap
            urls_to_capture = []
            if 'sitemap.xml' in url:
                print('URL é um sitemap. Buscando URLs...')
                urls_to_capture = get_urls_from_sitemap(url)
            else:
                print('URL não é um sitemap. Capturando screenshot da página...')
                urls_to_capture.append(url)
            
            for url_to_capture in urls_to_capture:
                # Limpa o nome da pasta usando a função clean_folder_name
                folder_name = os.path.join(base_folder, clean_folder_name(url_to_capture))
                capture_screenshot(url_to_capture, folder_name)

    messagebox.showinfo("Sucesso", "Processo de captura concluído!")

# Configuração da interface gráfica com Tkinter
root = Tk()
root.title("Captura de Screenshots de URLs")

# Texto de instrução
label = Label(root, text="Insira as URLs (uma por linha):")
label.pack(pady=10)

# Caixa de texto para entrada de URLs
url_textbox = Text(root, height=10, width=50)
url_textbox.pack(pady=10)

# Adicionando barra de rolagem
scrollbar = Scrollbar(root, command=url_textbox.yview)
scrollbar.pack(side="right", fill="y")
url_textbox.config(yscrollcommand=scrollbar.set)

# Botão para iniciar o processo
process_button = Button(root, text="Iniciar Captura", command=process_urls)
process_button.pack(pady=20)

# Rodando a interface gráfica
root.mainloop()
