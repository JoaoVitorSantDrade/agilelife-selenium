
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

def criar_sala(num_participantes:int = 1):
    
    host_da_sala = webdriver.Chrome(service=service)
    host_da_sala.set_window_size(400,320)
    host_da_sala.set_window_position(0,0)
    
    host_da_sala.get(config.URL)

    # Wait for the element to appear with a timeout of 10 seconds
    wait = WebDriverWait(host_da_sala, 30)
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala")]'))) \
        .click()

    wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
        .send_keys("Host")

    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala e Entrar")]'))) \
        .click()

    copiar_parent = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "COPIAR")]/parent::*')))
    input_com_link = copiar_parent.find_element(By.TAG_NAME, 'input')
    link = input_com_link.get_attribute('value')

    participantes_thread = []
    participantes_nomes = ["Host"]

    for i in range(num_participantes):
        id = str(uuid.uuid4())[:6]
        participantes_nomes.append(f"P-{id}")
        print(participantes_nomes)
        thread = Thread(target=entrar_na_sala, args=(link,id,), name=f'Participante {i + 1}')
        participantes_thread.append(thread)
        thread.start()

    alterar_thread = Thread(target=alterar_papel, args=(host_da_sala, num_participantes + 1), name='Alterar Papel')
    alterar_thread.start()

    for thread in participantes_thread:
        thread.join()

    host_da_sala.quit()

def verificar_se_todos_estao_na_salas(driver:webdriver.Chrome, num_participantes:int = 1):
    wait = WebDriverWait(driver, 10)
    for i in range(num_participantes):
        wait.until(EC.presence_of_element_located((By.ID, f'participante_{i}')))

    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Iniciar partida")]'))) \
        .click()
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

def entrar_na_sala(link, id):

    participante_da_sala = webdriver.Chrome(service=service)
    participante_da_sala.set_window_size(400,320)
    participante_da_sala.set_window_position(800,0)
    participante_da_sala.get(link)
    wait = WebDriverWait(participante_da_sala, 10)

    wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
        .send_keys(f"P-{id}")
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Entrar na Sala")]'))) \
        .click()
    participante_da_sala.quit()
      

if __name__ == '__main__':

    salas_thread = []
    for i in range(config.NUM_SALAS):
        thread = Thread(target=criar_sala,args=(config.PARTICIPANTES_POR_SALA,), name=f'Sala {i + 1}')
        salas_thread.append(thread)
        thread.start()

    for thread in salas_thread:
        thread.join()


    