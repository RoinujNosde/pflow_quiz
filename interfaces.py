from tkinter import *
from tkinter import font, ttk, messagebox
import fetcher
from enum import Enum
import webbrowser
from datetime import datetime

TAMANHO_PEQUENO = 8
TAMANHO_MEDIO = 10
TAMANHO_GRANDE = 13

class TelaInicial:
    """Classe que representa a tela principal do programa"""
    def __init__(self, master=None):
        self.janela_quiz = None
        self.cache = None
        master.title('PflowQuiz')
        master.iconbitmap(default='icon.ico')
        global TAMANHO_MEDIO
        self.fonte_media = font.Font(size=TAMANHO_MEDIO)

        self.container1 = Frame(master)
        self.container1.pack(pady=5)

        self.container2 = Frame(master)
        self.container2['pady'] = 5
        self.container2.pack()
        
        self.container3 = Frame(master)
        self.container3['pady'] = 10
        self.container3.pack()

        self.container4 = Frame(master)
        self.container4.pack(side=RIGHT, padx=(0, 10))

        self.label = Label(text='Escolha o quiz para jogar:', master=self.container1)
        self.label.config(font=self.fonte_media)
        self.label.pack()
        
        self.quiz_tree = ttk.Treeview(show=['headings'], master=self.container2, selectmode='browse', columns=('nome', 'autor', 'data', 'perguntas'))
        self.quiz_tree.heading('nome', text='Nome', command= lambda: self.__ordenar('nome', False))
        self.quiz_tree.column('nome', width=150, minwidth=150, anchor='center')
        self.quiz_tree.heading('autor', text='Autor', command= lambda: self.__ordenar('autor', False))
        self.quiz_tree.column('autor', width=120, minwidth=120, anchor='center')
        self.quiz_tree.heading('data', text='Data de criação', command= lambda: self.__ordenar('data', False))
        self.quiz_tree.column('data', width=120, minwidth=120, anchor='center')
        self.quiz_tree.heading('perguntas', text='Perguntas', command= lambda: self.__ordenar('perguntas', True))
        self.quiz_tree.column('perguntas', width=120, minwidth=70, anchor='center')
        self.quiz_tree.pack(padx=20)
        
        self.filtrar_label = Label(text='Filtrar: ', master=self.container3)
        self.filtrar_label.pack(side=LEFT)
        self.filtrar_entry = Entry(self.container3)
        self.filtrar_entry.bind('<KeyRelease>', lambda key: self.__atualizar_tabela(key, False, True))
        self.filtrar_entry.pack(side=LEFT, padx=(0, 90))
        self.atualizar_button = Button(self.container3, text='Atualizar lista', command=self.__atualizar_tabela)
        self.atualizar_button.pack(side=LEFT, padx=15)
        self.jogar_button = Button(self.container3, text='Jogar', command=self.__iniciar_quiz)
        self.jogar_button.pack(side=RIGHT, padx=15)

        self.info_contato_label = Label(self.container4, text='Contato: pflowdev@outlook.com')
        self.info_contato_label.bind('<Button-1>', self.__abrir_url_contato)
        self.info_contato_label.pack()

        self.__atualizar_tabela()

    def __ordenar(self, coluna, reverso):
        """Ordena os itens da tabela alfabeticamente"""
        tv = self.quiz_tree
        itens = [(tv.set(item, coluna), item) for item in tv.get_children()]

        itens.sort(reverse=reverso)

        for i in range(0, len(itens)):
            tv.move(itens[i][1], '', i)

        tv.heading(coluna, command= lambda: self.__ordenar(coluna, not reverso))

    def __abrir_url_contato(self, evento):
        """Abre a URL de contato"""
        webbrowser.open('mailto:pflowdev@outlook.com')

    def __iniciar_quiz(self):
        """Inicia o Quiz selecionado"""
        #Se a janela ainda não existe
        if not self.janela_quiz or not self.janela_quiz.winfo_exists():
            #Pega o ID do Quiz selecionado
            selecionados = self.quiz_tree.selection()
            if len(selecionados) == 0:
                messagebox.showerror(title="Erro", message="Selecione um Quiz para poder continuar!")
                return
            id_selecionado = selecionados[0]
            #Pega os dados do Quiz no webapp
            quiz = fetcher.pegar_dados_do_quiz(id_selecionado)
            if quiz == None:
                messagebox.showerror(title="Erro", message="Não foi possível baixar o quiz. \nVerifique sua conexão com a internet e tente novamente!")
                return
            #Gera a Janela de jogo com esse Quiz
            self.janela_quiz = Jogo(quiz, self)
        else:
            self.janela_quiz.deiconify()

    def __limpar_tabela(self):
        """Limpa a Treeview contendo os dados dos quizes"""
        self.quiz_tree.delete(*self.quiz_tree.get_children())

    def __atualizar_tabela(self, key=None, limpar_filtro=True, usar_cache=False):
        """Limpa e preenche a Treeview com dados atualizados"""
        self.__limpar_tabela()
        if limpar_filtro:
            self.filtrar_entry.delete(0, 'end')

        if not usar_cache or self.cache == None:
            self.cache = fetcher.pegar_list_de_quizes(self.quiz_tree)
        
        if self.cache == None:
            messagebox.showerror(title="Erro", message="Não foi possível baixar a lista de quizes. \nVerifique sua conexão com a internet e tente novamente!")
            return

        for quiz in self.cache:
            texto = self.filtrar_entry.get().lower()
            if key != None and texto != '':
                if texto not in quiz['nome'].lower() and texto not in quiz['autor'].lower():
                    continue

            if not quiz['aprovado']:
                continue
            if quiz['quantidade_perguntas_aprovadas'] == 0:
                continue

            self.quiz_tree.insert('', 'end', quiz['id'], values=[quiz['nome'], quiz['autor'], quiz['data_criacao'],
                                              quiz['quantidade_perguntas_aprovadas']])
        self.__ordenar('data', False)



class Jogo(Toplevel):
    """Classe que representa a tela de jogo"""
    class Direcao(enum.Enum):
        ANTERIOR = 1
        PROXIMO = 2

    def __init__(self, quiz, tela_inicial):
        super().__init__()
        self.tela_inicial = tela_inicial
        self.quiz = quiz
        self.quantidade_perguntas = len(self.quiz['pergunta_set'])
        self.pergunta_atual = 0
        self.escolhas_salvas = {}

        self.title(quiz['nome'])
        #self.attributes('-topmost', 'true')

        self.container1 = Frame(self)
        self.container1.pack(anchor=W, padx=80)

        self.container2 = Frame(self)
        self.container2.pack(anchor=W, padx=80)

        self.container3 = Frame(self)
        self.container3.pack()

        self.titulo_pergunta = Label(self.container1, width=35, wraplength=250)
        self.titulo_pergunta.pack(pady=10, anchor=W)

        self.resposta_selecionada = IntVar(value=0)
        self.resposta1_radio = Radiobutton(self.container2, variable=self.resposta_selecionada, value=0)
        self.resposta1_radio.pack(anchor=W)
        self.resposta2_radio = Radiobutton(self.container2, variable=self.resposta_selecionada, value=1)
        self.resposta2_radio.pack(anchor=W)
        self.resposta3_radio = Radiobutton(self.container2, variable=self.resposta_selecionada, value=2)
        self.resposta3_radio.pack(anchor=W)
        self.resposta4_radio = Radiobutton(self.container2, variable=self.resposta_selecionada, value=3)
        self.resposta4_radio.pack(anchor=W)

        self.anterior_button = Button(self.container3, text="Anterior", command= lambda: self.trocar_pergunta(Jogo.Direcao.ANTERIOR))
        self.anterior_button.pack(side=LEFT, padx=30)
        self.proximo_button = Button(self.container3, command= lambda: self.trocar_pergunta(Jogo.Direcao.PROXIMO))
        self.proximo_button.pack(side=RIGHT, padx= 30, pady=15)

        self.__atualizar_botoes()
        self.__atualizar_pergunta()
        self.__atualizar_respostas()

        self.focus()

    def __atualizar_botoes(self):
        """Ativa ou desativa o botão Anterior ou muda o nome do botão de avançar entre Finalizar/Próximo, de acordo com o index da pergunta atual"""
        if self.pergunta_atual == 0:
            state = 'disabled'
        else:
            state = 'normal'
        self.anterior_button['state'] = state

        if self.pergunta_atual == (self.quantidade_perguntas - 1):
            texto = "Finalizar"
        else:
            texto = "Próximo"
        self.proximo_button.config(text=texto)

    def __atualizar_pergunta(self):
        """Atualiza o texto da Label de pergunta de acordo com a atual"""
        titulo = str(self.pergunta_atual + 1) + ". " + self.quiz['pergunta_set'][self.pergunta_atual]['titulo_pergunta']
        self.titulo_pergunta.config(text=titulo)

    def __atualizar_respostas(self):
        """Atualiza os textos dos campos de resposta de acordo com a pergunta atual"""
        self.resposta_selecionada.set(self.escolhas_salvas.get(self.pergunta_atual, 0))
        self.resposta1_radio.config(text="A) " + self.quiz['pergunta_set'][self.pergunta_atual]['resposta_set'][0]['texto_resposta'])
        self.resposta2_radio.config(text="B) " + self.quiz['pergunta_set'][self.pergunta_atual]['resposta_set'][1]['texto_resposta'])
        self.resposta3_radio.config(text="C) " + self.quiz['pergunta_set'][self.pergunta_atual]['resposta_set'][2]['texto_resposta'])
        self.resposta4_radio.config(text="D) " + self.quiz['pergunta_set'][self.pergunta_atual]['resposta_set'][3]['texto_resposta'])

    def __salvar_escolha(self):
        """Salva a resposta escolhida pelo usuário"""
        self.escolhas_salvas[self.pergunta_atual] = self.resposta_selecionada.get()

    def trocar_pergunta(self, direcao):
        """Troca para a pergunta anterior, para a próxima de acordo com o parâmetro 'direcao' ou finaliza o jogo caso esteja na última pergunta"""
        self.__salvar_escolha()
        if direcao == Jogo.Direcao.PROXIMO:
            if self.pergunta_atual == (self.quantidade_perguntas - 1):
                self.tela_inicial.janela_quiz = FimDeJogo(self.quiz['nome'], self.get_pontuacao())
                self.destroy()
                return
            self.pergunta_atual += 1
        else:
            self.pergunta_atual -= 1
        self.__atualizar_botoes()
        self.__atualizar_pergunta()
        self.__atualizar_respostas()

    def get_pontuacao(self):
        corretas = {}
        index_pergunta = 0
        for pergunta in self.quiz['pergunta_set']:
            index_resposta = 0
            for resposta in pergunta['resposta_set']:
                if resposta['correta']:
                    corretas[index_pergunta] = index_resposta
                index_resposta += 1
            index_pergunta += 1

        acertos = 0
        for pergunta in corretas.keys():
            if corretas[pergunta] == self.escolhas_salvas[pergunta]:
                acertos += 1

        pontuacao = (acertos / len(corretas)) * 100
        return "%d%%" % pontuacao

class FimDeJogo(Toplevel):
    """Classe que representa a tela de fim de jogo"""
    def __init__(self, nome_quiz, pontuacao):
        super().__init__()
        self.title('Fim de jogo')
        global TAMANHO_GRANDE, TAMANHO_MEDIO, TAMANHO_PEQUENO
        self.fonte_grande = font.Font(size=TAMANHO_GRANDE)
        self.fonte_media = font.Font(size=TAMANHO_MEDIO)
        self.fonte_pequena = font.Font(size=TAMANHO_PEQUENO)

        self.container1 = Frame(self)
        self.container1.pack()

        self.container2 = Frame(self)
        self.container2.pack()

        self.mensagem_de_fim = Label(self.container1, font=self.fonte_grande, text="Você finalizou o quiz %s!" % nome_quiz)
        self.mensagem_de_fim.pack(pady=15, padx=20)

        self.pontuacao_titulo = Label(self.container2, font=self.fonte_media, text="Sua pontuação:")
        self.pontuacao_titulo.pack()

        self.pontuacao_label = Label(self.container2, font=self.fonte_media, text=pontuacao)
        self.pontuacao_label.pack(pady=(15, 25))

        self.mensagem_adicionar_quiz = Label(self.container2, font=self.fonte_pequena, wraplength=220, text="Que tal adicionar o seu próprio quiz ao jogo? Clique aqui e faça seu cadastro!")
        self.mensagem_adicionar_quiz.bind("<Button-1>", self.__abrir_pagina_cadastro)
        self.mensagem_adicionar_quiz.pack(pady=(0, 5))

        self.focus()

    def __abrir_pagina_cadastro(self, evento):
        """Abre a URL da página de cadastro"""
        webbrowser.open('http://roinujnosde.pythonanywhere.com/register')
