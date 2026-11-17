# Operação Sentinela - Analisador Sintático

**Global Solution 2026.2 · Resilient Community Infrastructure**
Linguagens, Autômatos e Computabilidade - FIAP 

Prof. Fabio Henrique Pimentel

Júlia Santos (RM 97897), Kauê Miziara (RM 550451) - 4ECA

## Sobre o projeto

Em uma emergência climática, escolas, ginásios e centros culturais viram **Pontos Comunitários de Apoio**, monitorados por dispositivos que emitem rotinas de alerta sobre quatro recursos essenciais: energia, água, controle de acesso e condições ambientais. Antes de chegar ao painel de supervisão, cada rotina precisa ter uma estrutura válida.

Este projeto implementa, em Python orientado a objetos, o **analisador sintático** que faz essa validação. As rotinas são escritas em um subconjunto didático de Java e passam por três etapas:

```
codigo_fonte.txt
   → Analisador léxico     (lexemas e tokens)
   → Analisador sintático  (descendente recursivo, gramática LL(1))
   → Árvore de derivação   (cadeia de terminais reconhecida)
   → saida.txt
```

O programa **aceita** rotinas que pertencem à linguagem da gramática e **rejeita** as malformadas, indicando o símbolo esperado, o símbolo encontrado e a linha.

> A validação sintática é uma camada complementar de segurança: ela verifica a **forma** do alerta, não a sua veracidade. Autenticação de dispositivos, integridade e plausibilidade dos dados ficam fora do escopo deste projeto.

### Estrutura

| Arquivo | Conteúdo |
|---|---|
| `analisador_sintatico.py` | Classes `Token`, `NoArvore`, `AnalisadorLexico` e `AnalisadorSintatico` |
| `gramatica_java.txt` | Gramática livre de contexto do subconjunto de Java (especificação formal) |
| `codigo_fonte.txt` | Rotina de alerta de referência |
| `casos_teste/` | Os quatro casos da bateria de homologação |
| `saida.txt` | Relatório da última execução |

## Como reproduzir

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/)

O projeto usa apenas a biblioteca padrão do Python, sem dependências externas. O uv instala automaticamente a versão do Python definida em `.python-version` na primeira execução.

### Executando

Na raiz do repositório:

```bash
uv sync
```

```bash
uv run python analisador_sintatico.py casos_teste/A_valido.txt
```

O resultado é exibido no terminal, e o relatório completo (resultado, cadeia de terminais e árvore de derivação, ou a mensagem de erro) é gravado em `saida.txt`.

> Cada execução **sobrescreve** o `saida.txt`.

Sem argumento, o programa analisa `codigo_fonte.txt`:

```bash
uv run python analisador_sintatico.py
```

### Casos de teste

| Caso | Comando | Resultado esperado |
|---|---|---|
| A | `uv run python analisador_sintatico.py casos_teste/A_valido.txt` | Cadeia reconhecida |
| B | `uv run python analisador_sintatico.py casos_teste/B_sem_ponto_virgula.txt` | Rejeitada: `Esperado ;, mas foi encontrado '}' (linha 22).` |
| C | `uv run python analisador_sintatico.py casos_teste/C_sem_abre_parenteses.txt` | Rejeitada: `Esperado (, mas foi encontrado 'temperatura' (linha 17).` |
| D | `uv run python analisador_sintatico.py casos_teste/D_parenteses_valido.txt` | Cadeia reconhecida, com os parênteses na árvore |