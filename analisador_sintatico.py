import re
from pathlib import Path
import sys

class Token:
    def __init__(self,tipo,lexema,linha):
        self.tipo=tipo;self.lexema=lexema;self.linha=linha
    def __str__(self):return f'{self.tipo} -> {self.lexema}'

class NoArvore:
    def __init__(self,simbolo,terminal=False):
        self.simbolo=simbolo;self.terminal=terminal;self.filhos=[]
    def adicionar(self,no):self.filhos.append(no)
    def obter_terminais(self):
        # MISSÃO 4 - TODO: Percorra os filhos na ordem; descarte epsilon; devolva os lexemas das folhas terminais.
        if self.terminal:
            if self.simbolo == 'epsilon':
                return []
            return [self.simbolo]
        terminais = []
        for filho in self.filhos:
            terminais.extend(filho.obter_terminais())
        return terminais

    def linhas(self,prefixo='',ultimo=True):
        saida=[prefixo+('`-- ' if ultimo else '|-- ')+self.simbolo]
        pref=prefixo+('    ' if ultimo else '|   ')
        for i,filho in enumerate(self.filhos): saida.extend(filho.linhas(pref, i==len(self.filhos)-1))
        return saida

class AnalisadorLexico:
    PALAVRAS_RESERVADAS={'public':'PUBLIC','class':'CLASS','static':'STATIC','void':'VOID','main':'MAIN','String':'STRING','int':'INT','if':'IF','while':'WHILE','for':'FOR'}
    PADRAO=re.compile(r'<=|>=|==|!=|<|>|[A-Za-z_][A-Za-z0-9_]*|[0-9]+|\+|-|\*|/|=|\(|\)|\{|\}|\[|\]|;')
    def __init__(self,codigo):self.codigo=codigo
    def tokenizar(self):
        tokens=[];posicao=0
        for m in self.PADRAO.finditer(self.codigo):
            intervalo=self.codigo[posicao:m.start()]
            if intervalo.strip():raise SyntaxError(f'Caractere não reconhecido: {intervalo!r}')
            lexema=m.group(0)
            if lexema in self.PALAVRAS_RESERVADAS:tipo=self.PALAVRAS_RESERVADAS[lexema]
            elif lexema.isdigit():tipo='NUM'
            elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',lexema):tipo='ID'
            elif lexema in ['<','>','<=','>=','==','!=']:tipo='OP_REL'
            else:tipo=lexema
            tokens.append(Token(tipo,lexema,self.codigo.count('\n',0,m.start())+1))
            posicao=m.end()
        if self.codigo[posicao:].strip():raise SyntaxError('Caractere final não reconhecido')
        return tokens

class AnalisadorSintatico:
    def __init__(self,tokens):self.tokens=tokens;self.posicao=0
    def atual(self):return self.tokens[self.posicao] if self.posicao<len(self.tokens) else None
    def consumir(self,tipo):
        t=self.atual()
        if t is None:raise SyntaxError(f'Esperado {tipo}, mas o código terminou.')
        if t.tipo!=tipo and t.lexema!=tipo:raise SyntaxError(f"Esperado {tipo}, mas foi encontrado '{t.lexema}' (linha {t.linha}).")
        self.posicao+=1
        return NoArvore(t.lexema,True)
    def epsilon(self):return NoArvore('epsilon',True)
    def analisar(self):
        raiz=self.programa()
        if self.atual() is not None:raise SyntaxError(f"Token excedente '{self.atual().lexema}'")
        return raiz
    def programa(self):
        n=NoArvore('programa')
        for tipo in ['PUBLIC','CLASS','ID','{']:n.adicionar(self.consumir(tipo))
        n.adicionar(self.metodo_main());n.adicionar(self.consumir('}'))
        return n
    def metodo_main(self):
        n=NoArvore('metodo_main')
        for tipo in ['PUBLIC','STATIC','VOID','MAIN','(','STRING','[',']','ID',')']:n.adicionar(self.consumir(tipo))
        n.adicionar(self.bloco());return n
    def bloco(self):
        # MISSÃO 4 - TODO: Implemente bloco -> "{" lista_stmt "}"; gere os respectivos nós.
        n = NoArvore('bloco')
        n.adicionar(self.consumir('{'))
        n.adicionar(self.lista_stmt())
        n.adicionar(self.consumir('}'))
        return n

    def lista_stmt(self):
        # MISSÃO 4 - TODO: Implemente lista_stmt -> stmt lista_stmt | epsilon; encerre quando encontrar "}".
        n = NoArvore('lista_stmt')
        t = self.atual()
        if t is None or t.lexema == '}':
            n.adicionar(self.epsilon())
        else:
            n.adicionar(self.stmt())
            n.adicionar(self.lista_stmt())
        return n

    def stmt(self):
        # MISSÃO 4 - TODO: Escolha a produção compatível com o token atual (INT, ID, IF, WHILE, FOR ou "{").
        n = NoArvore('stmt')
        t = self.atual()
        if t is None:
            raise SyntaxError('Instrução incompleta: o código terminou.')
        if t.tipo == 'INT':
            n.adicionar(self.declaracao())
            n.adicionar(self.consumir(';'))
        elif t.tipo == 'ID':
            n.adicionar(self.atribuicao())
            n.adicionar(self.consumir(';'))
        elif t.tipo == 'IF':
            n.adicionar(self.if_stmt())
        elif t.tipo == 'WHILE':
            n.adicionar(self.while_stmt())
        elif t.tipo == 'FOR':
            n.adicionar(self.for_stmt())
        elif t.lexema == '{':
            n.adicionar(self.bloco())
        else:
            # Nenhuma produção de stmt começa com este token: rejeição.
            raise SyntaxError(f"Instrução inválida: '{t.lexema}' (linha {t.linha}).")
        return n

    def declaracao(self):
        n=NoArvore('declaracao');n.adicionar(self.consumir('INT'));n.adicionar(self.consumir('ID'));n.adicionar(self.inicializacao());return n
    def inicializacao(self):
        n=NoArvore('inicializacao')
        if self.atual() is not None and self.atual().lexema=='=':
            n.adicionar(self.consumir('='));n.adicionar(self.expr())
        else:n.adicionar(self.epsilon())
        return n
    def atribuicao(self):
        n=NoArvore('atribuicao');n.adicionar(self.consumir('ID'));n.adicionar(self.consumir('='));n.adicionar(self.expr());return n
    def if_stmt(self):
        n=NoArvore('if_stmt');n.adicionar(self.consumir('IF'));n.adicionar(self.consumir('('));n.adicionar(self.condicao());n.adicionar(self.consumir(')'));n.adicionar(self.stmt());return n
    def while_stmt(self):
        # MISSÃO 4 - TODO: Implemente while_stmt -> "while" "(" condicao ")" stmt.
        n = NoArvore('while_stmt')
        n.adicionar(self.consumir('WHILE'))
        n.adicionar(self.consumir('('))
        n.adicionar(self.condicao())
        n.adicionar(self.consumir(')'))
        n.adicionar(self.stmt())
        return n

    def for_stmt(self):
        n=NoArvore('for_stmt');n.adicionar(self.consumir('FOR'));n.adicionar(self.consumir('('));n.adicionar(self.atribuicao());n.adicionar(self.consumir(';'));n.adicionar(self.condicao());n.adicionar(self.consumir(';'));n.adicionar(self.atribuicao());n.adicionar(self.consumir(')'));n.adicionar(self.stmt());return n
    def condicao(self):
        n=NoArvore('condicao');n.adicionar(self.expr());n.adicionar(self.consumir('OP_REL'));n.adicionar(self.expr());return n
    def expr(self):
        n=NoArvore('expr');n.adicionar(self.termo());n.adicionar(self.expr_linha());return n
    def expr_linha(self):
        n=NoArvore('expr_linha')
        if self.atual() is not None and self.atual().lexema in ['+','-']:
            n.adicionar(self.consumir(self.atual().lexema));n.adicionar(self.termo());n.adicionar(self.expr_linha())
        else:n.adicionar(self.epsilon())
        return n
    def termo(self):
        n=NoArvore('termo');n.adicionar(self.fator());n.adicionar(self.termo_linha());return n
    def termo_linha(self):
        n=NoArvore('termo_linha')
        if self.atual() is not None and self.atual().lexema in ['*','/']:
            n.adicionar(self.consumir(self.atual().lexema));n.adicionar(self.fator());n.adicionar(self.termo_linha())
        else:n.adicionar(self.epsilon())
        return n
    def fator(self):
        n=NoArvore('fator')
        t=self.atual()
        if t is None:raise SyntaxError('Fator incompleto')
        if t.tipo in ['NUM','ID']:n.adicionar(self.consumir(t.tipo))
        elif t.lexema=='(':
            n.adicionar(self.consumir('('));n.adicionar(self.expr());n.adicionar(self.consumir(')'))
        else:raise SyntaxError(f"Fator inválido: '{t.lexema}'")
        return n

def executar(caminho):
    codigo=Path(caminho).read_text(encoding='utf-8')
    tokens=AnalisadorLexico(codigo).tokenizar()
    raiz=AnalisadorSintatico(tokens).analisar()
    folhas=raiz.obter_terminais()
    assert folhas==[t.lexema for t in tokens], 'Yield divergente do fluxo de tokens'
    return tokens, raiz

if __name__=='__main__':
    arquivo=Path(sys.argv[1] if len(sys.argv)>1 else 'codigo_fonte.txt')
    try:
        tokens,arvore=executar(arquivo)
        texto='RESULTADO: CADEIA RECONHECIDA\n\nCADEIA DE TERMINAIS\n'+' '.join(arvore.obter_terminais())+'\n\nARVORE DE DERIVACAO\n'+'\n'.join(arvore.linhas())
    except NotImplementedError as e:
        texto='IMPLEMENTACAO INCOMPLETA\n\nPENDENCIA\n'+str(e)
    except SyntaxError as e:
        texto='RESULTADO: CADEIA NAO RECONHECIDA\n\nERRO SINTATICO\n'+str(e)
    Path('saida.txt').write_text(texto,encoding='utf-8')
    print(texto.splitlines()[0]);print('Relatório: saida.txt')
