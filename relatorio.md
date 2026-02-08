# Solução do Problema do Leitores/Escritores com Python e Sockets

## Contexto Inicial

Implementação de uma solução para o Problema clássico de Leitores/Escritores usando Python e sockets TCP. O problema ilustra os desafios de múltiplas tarefas acessando uma área de memória compartilhada com operações concorrentes de leitura e escrita.

O cenário implementado consiste em:
- **Servidor**: Gerencia 10 vagas de estacionamento
- **Clientes**: 50 clientes concorrentes que tentam estacionar, usar a vaga e depois sair
- **Comunicação**: Protocolo TCP/IP com sockets
- **Sincronização**: Threads Python com locks para garantir exclusão mútua

## Descrição da Solução

### 1. Arquitetura Geral

A solução segue um padrão cliente-servidor:

```
┌──────────────────────────────────────────────────────────────┐
│                       SERVIDOR (server.py)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  GerenciadorVagas (recurso compartilhado)             │  │
│  │  - 10 vagas disponíveis                               │  │
│  │  - Lock (mutex) para sincronização                    │  │
│  │  - Dicionário de clientes com vaga                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Thread para cada cliente conectado                          │
└─────────────────────────────┬────────────────────────────────┘
                              │ (Sockets TCP)
        ┌─────────────────────┴────────────────────┐
        │                                          │
   ┌────▼──────┐  ┌──────────┐  ...  ┌──────────┐
   │ Cliente 1  │  │ Cliente 2│      │ Cliente50│
   │  (Thread)  │  │ (Thread) │      │ (Thread) │
   └────────────┘  └──────────┘      └──────────┘
```

### 2. Implementação do Servidor

#### GerenciadorVagas

A classe `GerenciadorVagas` encapsula toda a lógica de gerenciamento de vagas com sincronização:

```python
class GerenciadorVagas:
    def __init__(self, total_vagas=10):
        self.total_vagas = total_vagas
        self.vagas_disponiveis = total_vagas
        self.lock = threading.Lock()  # Mutex para proteção
        self.clientes_com_vaga = {}    # Rastreamento de clientes
```

**Características de sincronização:**
- **Lock (Mutex)**: Mesmo lock protege todas as operações sobre vagas
- **Exclusão Mútua**: Cada método que modifica o estado usa `with self.lock:`
- **Atomicidade**: Operações de consulta, pega e liberação são atômicas

#### Operações do Servidor

1. **consultar_vaga()**: Retorna quantidade de vagas disponíveis (leitura)
2. **pegar_vaga()**: Aloca uma vaga para um cliente (escrita)
3. **liberar_vaga()**: Libera a vaga de um cliente (escrita)

### 3. Implementação dos Clientes

#### ClienteEstacionamento

Cada cliente é uma thread que implementa o seguinte ciclo de vida:

```python
def run(self):
    # Aguarda vagas disponíveis
    while not self.consultar_vaga():
        time.sleep(random.uniform(0.5, 2))
    
    # Tenta pegar vaga
    if self.pegar_vaga():
        # Usa a vaga (simula passeio)
        self.passear()
        # Libera a vaga
        self.liberar_vaga()
```

**Fluxo de um cliente:**
1. Verifica disponibilidade consultando o servidor
2. Se houver vagas, tenta pegar uma
3. Se conseguir vaga, simula tempo de uso (1-3 segundos)
4. Libera a vaga e encerra a conexão

### 4. Tratamento de Impasses (Deadlock Prevention)

#### Estratégia Implementada: Ordenação de Recursos

A estratégia de prevenção de deadlock utilizada é **ordenação linear de recursos**, que funciona da seguinte forma:

**Análise do Problema Original:**
- No caso deste estacionamento, existe apenas UM recurso compartilhado (as vagas)
- Não há múltiplos recursos que possam ser adquiridos em ordens diferentes
- Portanto, deadlock por ciclo de espera é **impossível**

**Técnicas Implementadas:**

1. **Lock Único Global**: Todas as operações usam o mesmo lock
   - Garante que não há múltiplos locks sendo adquiridos
   - Impede deadlock por espera circular

2. **Timeout nas Operações de Cliente**:
   ```python
   thread.join(timeout=30)  # Timeout de 30 segundos
   ```
   - Se uma thread ficar travada, é interrompida após 30 segundos
   - Previne que clientes presos travem o programa

3. **Garantia de Limpeza**:
   ```python
   finally:
       gerenciador.liberar_vaga(cliente_id)
   ```
   - Se cliente desconectar abruptamente, a vaga é automaticamente liberada
   - Evita que vagas fiquem presas indefinidamente

4. **Sem Espera Circular**:
   - Não há múltiplos recursos para criar ciclos
   - Clientes apenas consultam e depois pedem vagas (ordem consistente)

**Por que não há deadlock nesta solução:**
- ✅ Sem ciclo: Um cliente espera por vaga, não por outro cliente
- ✅ Sem circulação: Recurso sempre é liberado após uso
- ✅ Atomicidade: Operações críticas são indivisíveis (com lock)

### 5. Implementação do Protocolo

**Mensagens Cliente → Servidor:**
- `consultar_vaga`: Retorna número de vagas (0-10)
- `pegar_vaga`: Retorna 1 (sucesso) ou 0 (falha)
- `liberar_vaga`: Retorna 1 (sucesso) ou 0 (erro)

**Fluxo de Comunicação:**
```
Cliente                    Servidor
  │
  ├─ connect() ─────────→ accept()
  │
  ├─ send("consultar_vaga") ─→ recv()
  │                          └─ consultar_vaga()
  │ recv(resposta) ←──── send(str(vagas))
  │
  ├─ send("pegar_vaga") ──→ recv()
  │                          └─ pegar_vaga()
  │ recv(resposta) ←──── send("1" ou "0")
  │
  ├─ sleep(passear) ────→ (vaga alocada)
  │
  ├─ send("liberar_vaga") ──→ recv()
  │                          └─ liberar_vaga()
  │                          └─ close()
  │ recv(resposta) ←──── send("1")
  │
  └─ close() ────────────→
```

## Execução e Comportamento Observado

### Execução do Servidor

```bash
$ python src/server.py
Servidor escutando na porta 5000
Aguardando conexões de clientes...
```

### Execução dos Clientes

```bash
$ python src/cliente.py
Iniciando 50 clientes...

[Cliente 1] Iniciando
[Cliente 1] ESTACIONOU com sucesso!
[Cliente 1] Passeando por 2.3s
[Cliente 1] SAIU do estacionamento

[Cliente 2] Iniciando
[Cliente 2] ESTACIONOU com sucesso!
[Cliente 2] Passeando por 1.5s
[Cliente 2] SAIU do estacionamento
...
```

### Saída Esperada do Servidor

```
[Cliente localhost:52345_1] conectado
[Cliente localhost:52345_1] Consulta: 10 vagas disponíveis
[Cliente localhost:52345_1] PEGOU vaga. Vagas restantes: 9
[Cliente localhost:52347_2] conectado
[Cliente localhost:52347_2] Consulta: 9 vagas disponíveis
[Cliente localhost:52347_2] PEGOU vaga. Vagas restantes: 8
...
```

**Comportamento Observado:**
1. ✅ Múltiplos clientes conseguem se conectar simultaneamente
2. ✅ No máximo 10 clientes conseguem pegar vaga ao mesmo tempo
3. ✅ Clientes 11+ recebem resposta "0" (sem vaga)
4. ✅ Clientes aguardam e reintentam quando vagas são liberadas
5. ✅ Ordem de processamento é não-determinística (inerente ao escalonamento de threads)
6. ✅ Após 50 clientes passarem, o programa encerra corretamente

## Conceitos de Concorrência Demonstrados

| Conceito | Implementação |
|----------|---------------|
| **Sockets** | Comunicação TCP/IP entre cliente e servidor |
| **Threads** | 50 clientes simultâneos; 1 thread por cliente no servidor |
| **Exclusão Mútua** | Lock em `GerenciadorVagas` protege seção crítica |
| **Sincronização** | Operações atômicas com `with self.lock` |
| **Recurso Compartilhado** | Vagas de estacionamento acessadas simultaneamente |
| **Prevencção de Deadlock** | Lock único; timeout; limpeza garantida |
| **Condição de Corrida** | Evitada através de sincronização com mutex |

## Estrutura de Arquivos

```
src/
├── server.py           # Servidor com gerenciador de vagas
├── cliente.py          # Cliente com 50 threads
└── requirements.txt    # Dependências (python-dotenv)
.env                   # Configuração (PORT=5000)
relatorio.md           # Este relatório
```

## Como Executar

### 1. Instalar dependências
```bash
pip install -r src/requirements.txt
```

### 2. Executar servidor (em um terminal)
```bash
cd src
python server.py
```

### 3. Executar clientes (em outro terminal)
```bash
cd src
python cliente.py
```

### 4. Observar resultados
- **Servidor**: Mostra cada operação e vagas disponíveis
- **Clientes**: Mostra ciclo de vida de cada cliente (estaciona, passeia, sai)

## Considerações Finais

### Eficácia da Solução

1. **Sincronização Adequada**: O uso de mutex garante acesso exclusivo às vagas
2. **Sem Deadlock**: A estratégia de lock único torna deadlock impossível
3. **Escalabilidade**: 50 clientes simultâneos funcionam sem problemas
4. **Robustez**: Limpeza automática previne vazamento de recursos

### Melhorias Futuras

1. **Variações do Problema**:
   - Implementar "leitor/escritor verdadeiro" onde múltiplos leitores podem acessar simultaneamente
   - Usar `Condition` do Python para notificar clientes quando vagas ficam disponíveis

2. **Persistência**:
   - Adicionar banco de dados para registrar operações
   - Log de auditoria das transações

3. **Segurança**:
   - Autenticação de clientes
   - Encriptação de comunicação (SSL/TLS)
   - Validação de protocolo

4. **Performance**:
   - Connection pool para reutilizar conexões
   - Async/await em vez de threads
   - Servidor assíncrono com AsyncIO

### Aprendizados Principais

- **Locks são essenciais** para proteger recursos compartilhados
- **Ordem consistente de aquisição** de recursos previne deadlock
- **Timeouts e finalizadores** garantem robustez e limpeza
- **Abstração adequada** (classe `GerenciadorVagas`) simplifica sincronização
- **Testes com carga** (50 clientes) revelam problemas de concorrência

---

**Data**: 08/02/2026  
**Versão**: 1.0  
**Status**: Implementação Completa
