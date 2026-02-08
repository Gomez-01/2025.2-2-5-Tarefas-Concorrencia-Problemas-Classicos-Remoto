#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor TCP para gerenciamento de vagas de estacionamento.
O servidor escuta conexões de clientes e responde a comandos para consultar,
pegar e liberar vagas.

Autor: ChatGPT e Copilot com orientação e revisão de Minora
Data: 2024-06-15

Procure por FIXME para identificar pontos que precisam de implementação adicional.

"""
import socket
import os
import threading
import time
from dotenv import load_dotenv

# Gerenciador de vagas compartilhado entre threads
class GerenciadorVagas:
    def __init__(self, total_vagas=10):
        self.total_vagas = total_vagas
        self.vagas_disponiveis = total_vagas
        self.lock = threading.Lock()
        self.clientes_com_vaga = {}  # Dicionário para controlar qual cliente tem vaga
        
    def consultar_vaga(self):
        """Retorna quantidade de vagas disponíveis"""
        with self.lock:
            return self.vagas_disponiveis
    
    def pegar_vaga(self, cliente_id):
        """Tenta alocar uma vaga para o cliente"""
        with self.lock:
            if self.vagas_disponiveis > 0:
                self.vagas_disponiveis -= 1
                self.clientes_com_vaga[cliente_id] = True
                return True
            return False
    
    def liberar_vaga(self, cliente_id):
        """Libera a vaga do cliente"""
        with self.lock:
            if cliente_id in self.clientes_com_vaga:
                self.vagas_disponiveis += 1
                del self.clientes_com_vaga[cliente_id]
                return True
            return False

# Instância global do gerenciador de vagas
gerenciador = GerenciadorVagas(10)

def escutar_cliente(nova_conexao, endereco, contador_clientes):
    """Função para tratar a comunicação com cada cliente"""
    cliente_id = f"{endereco[0]}:{endereco[1]}_{contador_clientes[0]}"
    contador_clientes[0] += 1
    
    print(f'Cliente {cliente_id} conectado')
    
    try:
        while True:
            mensagem = nova_conexao.recv(1024)
            if not mensagem:
                break            
            comando = mensagem.decode("utf-8").strip()
            
            if comando == 'consultar_vaga':
                # retorna quantidade de vagas disponíveis
                vagas = gerenciador.consultar_vaga()
                resposta = str(vagas)
                nova_conexao.send(resposta.encode('utf-8'))
                print(f'[{cliente_id}] Consulta: {vagas} vagas disponíveis')
                
            elif comando == 'pegar_vaga':
                # tenta alocar uma vaga
                sucesso = gerenciador.pegar_vaga(cliente_id)
                resposta = str(1) if sucesso else str(0)
                nova_conexao.send(resposta.encode('utf-8'))
                if sucesso:
                    print(f'[{cliente_id}] PEGOU vaga. Vagas restantes: {gerenciador.consultar_vaga()}')
                else:
                    print(f'[{cliente_id}] Não conseguiu vaga (lotado)')
                
            elif comando == 'liberar_vaga':
                # libera a vaga do cliente
                sucesso = gerenciador.liberar_vaga(cliente_id)
                resposta = str(1) if sucesso else str(0)
                nova_conexao.send(resposta.encode('utf-8'))
                if sucesso:
                    print(f'[{cliente_id}] LIBEROU vaga. Vagas disponíveis: {gerenciador.consultar_vaga()}')
                    break  # Encerra conexão após liberar vaga
                else:
                    print(f'[{cliente_id}] Erro ao liberar vaga (não tinha vaga)')
                
            else:
                # retorna -1 para comando inválido
                resposta = '-1'
                nova_conexao.send(resposta.encode('utf-8'))
                
    finally:
        nova_conexao.close()
        print(f'Cliente {cliente_id} desconectado')
        # Garante limpeza caso cliente desconecte sem liberar vaga
        gerenciador.liberar_vaga(cliente_id)

def iniciar_servidor():
    """Função para iniciar o servidor TCP"""
    load_dotenv()
    PORTA = int(os.getenv('PORT', 5000))

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('localhost', PORTA))
    servidor.listen(50)
    print(f'Servidor escutando na porta {PORTA}')
    print('Aguardando conexões de clientes...\n')
    return servidor

def main():
    servidor = iniciar_servidor()
    contador_clientes = [0]  # Contador para IDs únicos
    
    try:
        while True:
            nova_conexao, endereco = servidor.accept()
            thread = threading.Thread(
                target=escutar_cliente, 
                args=(nova_conexao, endereco, contador_clientes)
            )
            thread.daemon = True
            thread.start()
        
    except KeyboardInterrupt:
        print('\nServidor encerrado pelo usuário')
    finally:
        servidor.close()
        print('Servidor finalizado')

if __name__ == '__main__':
    main()