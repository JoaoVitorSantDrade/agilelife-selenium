
import asyncio
from re import T
import time
import uuid
import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from threading import Thread

service = Service(executable_path='B:\\dev\\webdriver\\chromedriver.exe')

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

async def criar_sala(num_participantes:int = 1):
    
    host_da_sala = webdriver.Chrome(service=service)

    tabs = [host_da_sala.current_window_handle]
    
    host_da_sala.get(config.URL)

    # Wait for the element to appear with a timeout of 10 seconds
    wait = WebDriverWait(host_da_sala, 30)

    print("Aguardando botão de criar sala ficar disponível")
    assert wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala")]'))).is_enabled()
    print("Teste passou: botão de criar sala está disponível\n")
    host_da_sala.find_element(By.XPATH, '//button[contains(text(), "Criar Sala")]').click()

    wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
        .send_keys("Host")

    assert wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala e Entrar")]'))) \
        .is_enabled()
    print("Teste passou: botão de criar sala e entrar está disponível\n")

    host_da_sala.find_element(By.XPATH, '//button[contains(text(), "Criar Sala e Entrar")]').click()

    copiar_parent = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "COPIAR")]/parent::*')))
    input_com_link = copiar_parent.find_element(By.TAG_NAME, 'input')
    link = input_com_link.get_attribute('value')

    participantes_nomes = ["Host"]

    for i in range(num_participantes):
        id = str(uuid.uuid4())[:6]
        participantes_nomes.append(f"P-{id}")
        host_da_sala.switch_to.new_window('tab')
        host_da_sala.get(link)
        tabs.append(host_da_sala.current_window_handle)
        entrar_na_sala(host_da_sala, id)

    host_da_sala.switch_to.window(tabs[0])
    alterar_papel(host_da_sala, len(participantes_nomes))
    for  tab in tabs:
        host_da_sala.switch_to.window(tab)
        verificar_se_esta_na_sala(host_da_sala)

    print("Teste passou: todos os participantes estão na sala\n")
    host_da_sala.quit()
    return

def verificar_se_esta_na_sala(driver:webdriver.Chrome):
    wait = WebDriverWait(driver, 10)
    assert wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Tabuleiro'))).is_displayed()
    return

def alterar_papel(driver:webdriver.Chrome, num_participantes:int = 1):
    wait = WebDriverWait(driver, 10)
    for i in range(num_participantes):
        select_element = wait.until(EC.presence_of_element_located((By.ID, f'participante_{i}')))
        select_element = select_element.find_element(By.TAG_NAME, 'select')
        Select(select_element).select_by_index(i + 1)

    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Iniciar partida")]'))) \
        .click()
    return

def entrar_na_sala(driver, id):


    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
        .send_keys(f"P-{id}")
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Entrar na Sala")]'))) \
        .click()
    return

if __name__ == '__main__':
    
    salas_thread = []
    for i in range(config.NUM_SALAS):
        thread = Thread(target=asyncio.run(criar_sala(config.PARTICIPANTES_POR_SALA)), name=f'Sala {i + 1}')
        salas_thread.append(thread)
        print("Criando sala")
        thread.start()
    
    for thread in salas_thread:
        print("Aguardando sala ser criada")
        thread.join()
        print("Entrou na sala")


    