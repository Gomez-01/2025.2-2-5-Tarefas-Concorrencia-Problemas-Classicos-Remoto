#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente TCP para gerenciamento de vagas de estacionamento.
O cliente envia comandos ao servidor para consultar,
pegar e liberar vagas.

Autor: ChatGPT e Copilot com orientação e revisão de Minora
Data: 2024-06-15

"""

import threading
import socket
import os
import time
import random
from dotenv import load_dotenv


class ClienteEstacionamento(threading.Thread):
    def __init__(self, socket_cliente, id_cliente):
        threading.Thread.__init__(self)
        self.socket_cliente = socket_cliente
        self.id_cliente = id_cliente
        self.daemon = True

    def run(self):
        """Método de execução da thread - implementa ciclo de vida do cliente"""
        try:
            print(f'[Cliente {self.id_cliente}] Iniciando')
            
            # Tenta consultar vagas
            while not self.consultar_vaga():
                print(f'[Cliente {self.id_cliente}] Estacionamento lotado, aguardando...')
                time.sleep(random.uniform(0.5, 2))
            
            # Tenta pegar vaga
            if self.pegar_vaga():
                print(f'[Cliente {self.id_cliente}] ESTACIONOU com sucesso!')
                
                # Passeia (simula tempo de uso da vaga)
                self.passear()
                
                # Libera a vaga
                if self.liberar_vaga():
                    print(f'[Cliente {self.id_cliente}] SAIU do estacionamento')
                else:
                    print(f'[Cliente {self.id_cliente}] Erro ao sair')
            else:
                print(f'[Cliente {self.id_cliente}] FALHOU ao tentar estacionar')
                
        except Exception as e:
            print(f'[Cliente {self.id_cliente}] ERRO: {e}')
        finally:
            self.socket_cliente.close()

    def consultar_vaga(self):
        """Consulta a quantidade de vagas disponíveis no servidor"""
        try:
            self.socket_cliente.send('consultar_vaga'.encode('utf-8'))
            resposta = self.socket_cliente.recv(1024).decode('utf-8')
            vagas = int(resposta)
            return vagas > 0
        except Exception as e:
            print(f'[Cliente {self.id_cliente}] Erro ao consultar: {e}')
            return False

    def pegar_vaga(self):
        """Tenta pegar uma vaga no servidor"""
        try:
            self.socket_cliente.send('pegar_vaga'.encode('utf-8'))
            resposta = self.socket_cliente.recv(1024).decode('utf-8')
            return resposta == '1'
        except Exception as e:
            print(f'[Cliente {self.id_cliente}] Erro ao pegar vaga: {e}')
            return False

    def liberar_vaga(self):
        """Libera a vaga ocupada no servidor"""
        try:
            self.socket_cliente.send('liberar_vaga'.encode('utf-8'))
            resposta = self.socket_cliente.recv(1024).decode('utf-8')
            return resposta == '1'
        except Exception as e:
            print(f'[Cliente {self.id_cliente}] Erro ao liberar vaga: {e}')
            return False
    
    def passear(self):
        """Simula o tempo que o cliente fica com a vaga ocupada"""
        tempo_uso = random.uniform(1, 3)  # Entre 1 e 3 segundos
        print(f'[Cliente {self.id_cliente}] Passeando por {tempo_uso:.1f}s')
        time.sleep(tempo_uso)

def criar_socket_cliente(porta):
    """Cria e retorna um socket TCP para o cliente"""
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', porta))
    return cliente

def main():
    """Função principal para iniciar 50 clientes concorrentes"""
    load_dotenv()
    PORTA = int(os.getenv('PORT', 5000))
    NUM_CLIENTES = 50
    
    print(f'Iniciando {NUM_CLIENTES} clientes...\n')
    
    threads_clientes = []
    
    # Criar e iniciar 50 clientes
    for i in range(NUM_CLIENTES):
        try:
            socket_cliente = criar_socket_cliente(PORTA)
            cliente = ClienteEstacionamento(socket_cliente, i + 1)
            cliente.start()
            threads_clientes.append(cliente)
            time.sleep(0.05)  # Pequeno delay entre criações para evitar sobrecarga
        except Exception as e:
            print(f'Erro ao criar cliente {i + 1}: {e}')
    
    # Aguard todas as threads finalizarem
    for thread in threads_clientes:
        thread.join(timeout=30)  # Timeout de 30 segundos por thread
    
    print('\nTodos os clientes finalizaram!')

if __name__ == "__main__":
    main()
