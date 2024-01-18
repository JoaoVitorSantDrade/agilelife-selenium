
import threading
import uuid

import config
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.core.os_manager import ChromeType


service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
service.start()

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

class MyException(Exception):
    pass

# Custom Thread Class
class exceptionThread(threading.Thread):
     
    def run(self):
        self.exc = None
        try:
            threading.Thread.run(self)
        except BaseException as e:
            self.exc = e
       
    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc

def criar_sala(num_participantes:int = 1):
    
    print("\nIniciando teste de criação de sala\n")
    host_da_sala = webdriver.Remote(service.service_url, options=options)

    tabs = [host_da_sala.current_window_handle]
    try:
        host_da_sala.get(config.URL)
    except:
        raise MyException("Não foi possível acessar a URL")

    # Wait for the element to appear with a timeout of 10 seconds
    wait = WebDriverWait(host_da_sala, 30)

    print("\nAguardando botão de criar sala ficar disponível\n")

    try:
        assert wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala")]'))).is_enabled()
    except:
        raise MyException("Botão de criar sala não está disponível")
    
    print("Teste passou: botão de criar sala está disponível\n")
    host_da_sala.find_element(By.XPATH, '//button[contains(text(), "Criar Sala")]').click()

    try:
        print("Inserindo nome do host\n")
        wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
        .send_keys("Host")
    except:
        raise MyException("Não foi possível inserir o nome do host")

    assert wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Criar Sala e Entrar")]'))) \
        .is_enabled()
    print("Teste passou: botão de criar sala e entrar está disponível\n")

    host_da_sala.find_element(By.XPATH, '//button[contains(text(), "Criar Sala e Entrar")]').click()

    try:
        copiar_parent = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "COPIAR")]/parent::*')))
        input_com_link = copiar_parent.find_element(By.TAG_NAME, 'input')
        link = input_com_link.get_attribute('value')
    except:
        raise MyException("Não foi possível copiar o link da sala")

    participantes_nomes = ["Host"]

    for i in range(num_participantes - 1):
        print(f"Participante {i + 1} entrando na sala\n")
        id = str(uuid.uuid4())[:6]
        participantes_nomes.append(f"P-{id}")
        host_da_sala.switch_to.new_window('tab')
        host_da_sala.get(link)
        tabs.append(host_da_sala.current_window_handle)
        entrar_na_sala(host_da_sala, id)

    host_da_sala.switch_to.window(tabs[0])
    alterar_papel(host_da_sala, len(participantes_nomes))
    print("Teste passou: todos os participantes tiveram seu Papel alterado\n")
    for i , tab in enumerate(tabs):
        host_da_sala.switch_to.window(tab)
        try:
            verificar_se_esta_na_sala(host_da_sala)
        except:
            raise MyException(f"Participante {i} não entrou no tabuleiro")
            

    print("Teste passou: todos os participantes estão na sala\n")
    host_da_sala.quit()
        

def verificar_se_esta_na_sala(driver:webdriver.Chrome):
    wait = WebDriverWait(driver, 10)
    assert wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Tabuleiro'))).is_displayed()
    return

def alterar_papel(driver:webdriver.Chrome, num_participantes:int = 1):
    wait = WebDriverWait(driver, 10)
    for i in range(num_participantes):
        try:
            select_element = wait.until(EC.presence_of_element_located((By.ID, f'participante_{i}')))
            select_element = select_element.find_element(By.TAG_NAME, 'select')
            Select(select_element).select_by_index(i + 1)
        except:
            raise MyException(f"Não foi possível alterar o papel do participante {i + 1}")

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Iniciar partida")]'))) \
        .click()
    except:
        raise MyException("Não foi possível iniciar a partida")
    
    return

def entrar_na_sala(driver, id):

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'input-nick'))) \
            .send_keys(f"P-{id}")
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Entrar na Sala")]'))) \
            .click()
        return
    except:
        raise MyException("Não foi possível entrar na sala")
    

if __name__ == '__main__':
    
    salas_thread = []
    try:
        for i in range(config.NUM_SALAS):
            thread = exceptionThread(target=criar_sala, args=(config.PARTICIPANTES_POR_SALA,), name=f'Sala {i + 1}')
            salas_thread.append(thread)
            print("Criando sala")
            thread.start()
        
        for thread in salas_thread:
            thread.join()
    except MyException as e:
        print(f"Exception: {e}")
        exit(1)


    