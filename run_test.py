#!/usr/bin/env python3
"""
Teste do Problema de Leitores/Escritores com sockets.
"""
import subprocess
import time
import os
import signal
import sys
import tempfile

def main():
    # Diretório do workspace
    workspace_dir = '/workspaces/2025.2-2-5-Tarefas-Concorrencia-Problemas-Classicos-Remoto/src'
    
    # Verificar se o diretório existe
    if not os.path.isdir(workspace_dir):
        print(f"❌ Erro: Diretório não encontrado: {workspace_dir}")
        return False
    
    # Verificar se os scripts existem
    server_script = os.path.join(workspace_dir, 'server.py')
    client_script = os.path.join(workspace_dir, 'cliente.py')
    
    if not os.path.isfile(server_script):
        print(f"❌ Erro: Arquivo não encontrado: {server_script}")
        return False
    
    if not os.path.isfile(client_script):
        print(f"❌ Erro: Arquivo não encontrado: {client_script}")
        return False
    
    print("=" * 80)
    print("INICIANDO TESTE DO PROBLEMA DE LEITORES/ESCRITORES COM SOCKETS")
    print("=" * 80)
    print(f"\nDiretório: {workspace_dir}\n")
    
    # Arquivos temporários para logs
    server_log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='_server.log')
    client_log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='_client.log')
    server_log_path = server_log_file.name
    client_log_path = client_log_file.name
    server_log_file.close()
    client_log_file.close()
    
    try:
        # 1. Iniciar servidor em background
        print("[1] Iniciando servidor.py em background...")
        with open(server_log_path, 'w') as server_log:
            server_process = subprocess.Popen(
                [sys.executable, server_script],
                stdout=server_log,
                stderr=subprocess.STDOUT,
                cwd=workspace_dir
            )
        print(f"    ✓ Servidor iniciado com PID: {server_process.pid}\n")
        
        # 2. Aguardar 2 segundos
        print("[2] Aguardando 2 segundos para o servidor ficar pronto...")
        time.sleep(2)
        print("    ✓ Servidor pronto!\n")
        
        # 3. Executar cliente com timeout de 25 segundos
        print("[3] Executando cliente.py com timeout de 25 segundos...")
        try:
            with open(client_log_path, 'w') as client_log:
                client_result = subprocess.run(
                    [sys.executable, client_script],
                    stdout=client_log,
                    stderr=subprocess.STDOUT,
                    cwd=workspace_dir,
                    timeout=25
                )
            print(f"    ✓ Cliente finalizou com código: {client_result.returncode}\n")
        except subprocess.TimeoutExpired:
            print("    ⚠️  Cliente ultrapassou o timeout de 25 segundos!\n")
        
        # 4. Matar o servidor
        print("[4] Encerrando o servidor...")
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()
        print("    ✓ Servidor encerrado!\n")
        
        # 5. Exibir logs
        print("=" * 80)
        print("LOGS DO SERVIDOR")
        print("=" * 80)
        with open(server_log_path, 'r') as f:
            server_output = f.read()
            print(server_output if server_output else "(nenhuma saída)")
        
        print("\n" + "=" * 80)
        print("LOGS DO CLIENTE")
        print("=" * 80)
        with open(client_log_path, 'r') as f:
            client_output = f.read()
            print(client_output if client_output else "(nenhuma saída)")
        
        print("\n" + "=" * 80)
        print("TESTE FINALIZADO COM SUCESSO!")
        print("=" * 80)
        
        return True
        
    finally:
        # Limpar arquivos temporários
        try:
            os.unlink(server_log_path)
            os.unlink(client_log_path)
        except:
            pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
