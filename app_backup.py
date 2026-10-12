
# ============================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ============================================================

# sqlite3:
# Permite conectar, consultar e manipular o banco SQLite.
# No nosso TCC, usamos para buscar os eventos detectados.
import sqlite3

# Path:
# Facilita trabalhar com caminhos de arquivos e pastas.
# Funciona independentemente de onde o projeto estiver salvo.
from pathlib import Path

# streamlit:
# Biblioteca responsável por construir toda a interface web.
# O apelido "st" facilita a utilização dos comandos.
import streamlit as st


# ============================================================
# 2. CONFIGURAÇÕES DO PROJETO
# ============================================================

# Localiza automaticamente a pasta onde está o app.py.
# Exemplo: C:/Users/{usuario}/Desktop/TCC_CFTV
BASE = Path(__file__).resolve().parent

# Define o caminho do banco de dados.
# O operador / é utilizado para juntar caminhos.
BANCO = BASE / "cftv.db"

# Define a pasta onde ficam armazenados os vídeos.
VIDEOS = BASE / "videos"


# ============================================================
# 3. CONFIGURAÇÕES DA PÁGINA
# ============================================================

# Define as configurações gerais da aplicação.
# IMPORTANTE: deve aparecer antes dos outros comandos
# Streamlit que criam elementos na página.

st.set_page_config(

    # Nome exibido na aba do navegador.
    # PERSONALIZÁVEL: pode alterar livremente.
    page_title="CFTV | Central de Segurança",

    # Ícone exibido na aba do navegador.
    # PERSONALIZÁVEL: pode usar outro emoji.
    page_icon="📹",

    # Define a largura da área principal.
    #
    # "wide"     = ocupa mais espaço horizontal.
    # "centered" = conteúdo centralizado e mais estreito.
    #
    # Para o dashboard de CFTV, "wide" é mais adequado.
    layout="wide",

    # Define como o menu lateral aparece inicialmente.
    #
    # "expanded"  = menu aberto.
    # "collapsed" = menu recolhido.
    initial_sidebar_state="expanded"
)


# ============================================================
# 4. ESTILO VISUAL - CSS
# ============================================================

# st.markdown permite inserir HTML/CSS na aplicação.
#
# O CSS controla:
# - Cores
# - Espaçamentos
# - Tamanhos
# - Bordas
# - Aparência dos botões
# - Aparência dos indicadores
#
# unsafe_allow_html=True permite inserir HTML e CSS.
#
# ATENÇÃO:
# Algumas estruturas internas do Streamlit podem mudar
# entre versões, afetando determinados seletores CSS.

st.markdown("""

<style>

/* ==========================================================
   4.1. FUNDO PRINCIPAL DA APLICAÇÃO
   ========================================================== */

.stApp {

    /* Cor de fundo de toda a aplicação.
       PERSONALIZÁVEL: altere o código hexadecimal. */
    background: #0b1220;

    /* Cor padrão dos textos da aplicação. */
    color: #e5edf7;
}


/* ==========================================================
   4.2. MENU LATERAL
   ========================================================== */

[data-testid="stSidebar"] {

    /* Cor de fundo do menu lateral. */
    background: #111c2e;

    /* Borda direita do menu.
       1px = espessura.
       solid = linha contínua.
       #26364b = cor da borda. */
    border-right: 1px solid #26364b;
}


/* ==========================================================
   4.3. ÁREA PRINCIPAL DO DASHBOARD
   ========================================================== */

.block-container {

    /* Distância entre o topo da área principal
       e o primeiro elemento da página.

       1rem normalmente equivale a 16px,
       dependendo do tamanho da fonte raiz.

       PERSONALIZÁVEL:
       2rem = mais espaço.
       1rem = menos espaço.
       0.5rem = espaço ainda menor. */
    padding-top: 2rem;

    /* Largura máxima do conteúdo.

       Se a tela for maior que 1450px,
       o conteúdo não ultrapassará esse limite.

       PERSONALIZÁVEL:
       1200px = conteúdo mais estreito.
       1600px = conteúdo mais largo.
       100% = utiliza a largura disponível. */
    max-width: 1450px;
}


/* ==========================================================
   4.4. TÍTULOS
   ========================================================== */

/* h1 = título principal.
   h2 = título secundário.
   h3 = subtítulo. */

h1, h2, h3 {

    /* Define a cor dos títulos.

       !important dá prioridade a essa regra
       sobre outras regras CSS de menor prioridade. */
    color: #f2f6fc !important;
}


/* ==========================================================
   4.5. CARTÕES DOS INDICADORES
   ========================================================== */

/* Este seletor identifica os componentes st.metric. */

[data-testid="stMetric"] {

    /* Cor de fundo dos cartões. */
    background: #152238;

    /* Borda dos cartões. */
    border: 1px solid #293b53;

    /* Espaçamento interno.
       Quanto maior, maior o espaço ocupado pelo cartão. */
    padding: 18px;

    /* Arredondamento dos cantos.

       0px = quadrado.
       12px = arredondamento moderado.
       25px = mais arredondado. */
    border-radius: 12px;
}


/* ==========================================================
   4.6. NÚMEROS DOS INDICADORES
   ========================================================== */

[data-testid="stMetricValue"] {

    /* Cor dos números dos indicadores.

       No seu sistema, é o verde-água utilizado em:
       Vídeos indexados
       Eventos registrados
       Classes identificadas */
    color: #5eead4;
}


/* ==========================================================
   4.7. BORDAS DOS CONTAINERS
   ========================================================== */

/* Modifica a cor das bordas de alguns containers
   utilizados com st.container(border=True). */

div[data-testid="stVerticalBlockBorderWrapper"] > div {

    border-color: #293b53;
}


/* ==========================================================
   4.8. BOTÕES PRINCIPAIS
   ========================================================== */

/* Altera botões criados com type="primary". */

.stButton > button[kind="primary"] {

    /* Cor de fundo do botão. */
    background: #0f9f91;

    /* Cor da borda do botão. */
    border-color: #0f9f91;

    /* Cor do texto do botão. */
    color: white;
}


/* ==========================================================
   4.9. EFEITO AO PASSAR O MOUSE
   ========================================================== */

/* :hover significa que o mouse está sobre o botão. */

.stButton > button[kind="primary"]:hover {

    /* Escurece o botão quando o mouse passa sobre ele. */
    background: #0b8177;

    /* Escurece também a borda. */
    border-color: #0b8177;
}


/* ==========================================================
   4.10. MENSAGENS DO SISTEMA
   ========================================================== */

/* Controla o arredondamento de mensagens como:
   st.success, st.warning, st.info e st.error. */

div[data-testid="stAlert"] {

    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 5. FUNÇÃO PARA CONVERTER HORÁRIOS
# ============================================================

# Essa função recebe um horário no formato HH:MM:SS
# e transforma o horário em segundos.
#
# Exemplo:
# "00:00:12" -> 12 segundos.
# "00:01:30" -> 90 segundos.
#
# Precisamos disso porque st.video(start_time=...)
# utiliza o instante inicial do vídeo.

def segundos(tempo):

    # Converte o valor recebido para texto e separa
    # as partes utilizando ":".
    #
    # Exemplo:
    # "00:01:30" -> ["00", "01", "30"]
    partes = str(tempo).split(":")

    # Confere se existem exatamente três partes.
    # Caso contrário, informa que o horário é inválido.
    if len(partes) != 3:
        raise ValueError("Horário inválido")

    # Converte cada parte para número inteiro.
    #
    # h = horas
    # m = minutos
    # s = segundos
    h, m, s = map(int, partes)

    # Converte tudo para segundos.
    #
    # 1 hora = 3600 segundos.
    # 1 minuto = 60 segundos.
    return h * 3600 + m * 60 + s


# ============================================================
# 6. FUNÇÃO PARA CONSULTAR O BANCO DE DADOS
# ============================================================

def carregar_eventos():

    # Verifica se o arquivo cftv.db existe.
    if not BANCO.is_file():

        # Retorna uma lista vazia e uma mensagem de erro.
        return [], "Banco de dados não encontrado."

    try:

        # Abre a conexão com o banco SQLite.
        # O with gerencia o contexto da conexão.
        with sqlite3.connect(BANCO) as con:

            # Executa uma consulta SQL.
            dados = con.execute(
                """
                SELECT video, classe, inicio, fim
                FROM eventos
                ORDER BY video, inicio
                """
            ).fetchall()

            # SELECT:
            # Seleciona as colunas desejadas.
            #
            # FROM eventos:
            # Define a tabela consultada.
            #
            # ORDER BY video, inicio:
            # Ordena os resultados pelo nome do vídeo
            # e depois pelo horário inicial.
            #
            # fetchall():
            # Retorna todos os registros encontrados.

        # Retorna os dados e indica ausência de erro.
        return dados, None

    # Captura erros relacionados ao SQLite.
    except sqlite3.Error as erro:

        return [], f"Erro ao consultar banco: {erro}"


# Executa a função de consulta.
#
# eventos = lista de registros encontrados.
# erro = mensagem de erro ou None.
eventos, erro = carregar_eventos()


# ============================================================
# 7. SESSION STATE - MEMÓRIA DA INTERFACE
# ============================================================

# O Streamlit executa novamente o script quando
# o usuário interage com determinados componentes.
#
# st.session_state permite preservar informações
# entre essas execuções.
#
# Sem ele, clicar em "Assistir" poderia fazer
# os resultados da pesquisa desaparecerem.


# Armazena os resultados da última pesquisa.
if "resultados" not in st.session_state:

    st.session_state.resultados = None


# Armazena o índice do evento selecionado.
if "selecionado" not in st.session_state:

    st.session_state.selecionado = None


# ============================================================
# 8. MENU LATERAL
# ============================================================

# Tudo dentro de with st.sidebar aparece
# no painel lateral esquerdo da aplicação.

with st.sidebar:

    # Título principal do menu.
    # PERSONALIZÁVEL.
    st.title("📹 CFTV")

    # Texto pequeno abaixo do título.
    st.caption("CENTRAL INTELIGENTE")

    # Adiciona uma linha horizontal.
    st.divider()

    # Cria o menu de navegação.
    #
    # st.radio permite escolher uma opção por vez.
    #
    # A variável pagina recebe a opção selecionada.
    pagina = st.radio(

        # Nome interno do campo.
        "Navegação",

        # Opções disponíveis no menu.
        [
            "Visão geral",
            "Buscar eventos",
            "Vídeos"
        ],

        # Oculta o rótulo "Navegação" da interface.
        label_visibility="collapsed"
    )

    # Outra linha divisória.
    st.divider()

    # Texto informativo.
    st.caption("SISTEMA DE INDEXAÇÃO")

    # Exibe uma mensagem verde.
    #
    # IMPORTANTE:
    # Essa mensagem é apenas visual.
    # Não verifica se uma câmera está funcionando.
    st.success("● Aplicação ativa")

    # Identificação do projeto.
    st.caption(
        "Projeto de TCC | Visão Computacional"
    )


# ============================================================
# 9. CABEÇALHO DA APLICAÇÃO
# ============================================================

# Título principal da área central.
st.title("Central Inteligente de CFTV")

# Descrição exibida abaixo do título.
st.caption(
    "Indexação, pesquisa e recuperação de eventos "
    "em gravações de segurança"
)

# Linha horizontal separando o cabeçalho dos indicadores.
st.divider()


# Caso exista algum erro no banco:
if erro:

    # Exibe a mensagem de erro em vermelho.
    st.error(erro)

    # Interrompe a execução da página.
    st.stop()


# ============================================================
# 10. INDICADORES DO DASHBOARD
# ============================================================

# Conta quantos nomes diferentes de vídeos
# aparecem nos eventos registrados.
#
# e[0] representa a coluna video.
#
# set() remove valores repetidos.
# len() conta quantos elementos restaram.
total_videos = len(set(e[0] for e in eventos))


# Conta quantas classes diferentes existem.
#
# e[1] representa a coluna classe.
total_classes = len(set(e[1] for e in eventos))


# Divide a área principal em três colunas iguais.
#
# a = primeira coluna.
# b = segunda coluna.
# c = terceira coluna.
#
# PERSONALIZÁVEL:
# st.columns(2) cria duas colunas.
# st.columns(4) cria quatro colunas.
a, b, c = st.columns(3)


# Cria o primeiro indicador.
a.metric(
    "Vídeos indexados",
    total_videos
)

# Cria o segundo indicador.
#
# len(eventos) representa a quantidade
# total de eventos registrados.
b.metric(
    "Eventos registrados",
    len(eventos)
)

# Cria o terceiro indicador.
c.metric(
    "Classes identificadas",
    total_classes
)


# ============================================================
# 11. PÁGINA: VISÃO GERAL
# ============================================================

# Essa parte só aparece quando o usuário
# seleciona "Visão geral" no menu lateral.

if pagina == "Visão geral":

    # Subtítulo da página.
    st.subheader("Visão geral do monitoramento")

    # Caixa informativa azul.
    st.info(
        "Consulte os eventos registrados ou abra "
        "'Buscar eventos' para reproduzir as detecções."
    )

    st.subheader("Eventos recentes")

    # Verifica se existem eventos no banco.
    if eventos:

        # eventos[-10:] seleciona os últimos dez registros
        # da lista carregada.
        #
        # [::-1] inverte a ordem desses registros.
        #
        # OBSERVAÇÃO:
        # Como a consulta SQL está ordenada por vídeo
        # e início, isso não representa necessariamente
        # os eventos mais recentes por data de gravação.
        for video, classe, inicio, fim in eventos[-10:][::-1]:

            # Cria um cartão com borda.
            with st.container(border=True):

                # Mostra a classe e o nome do vídeo.
                #
                # capitalize() coloca a primeira letra
                # em maiúscula.
                #
                # **texto** aplica negrito em Markdown.
                st.write(
                    f"**{classe.capitalize()}** — {video}"
                )

                # Exibe o intervalo temporal.
                st.caption(
                    f"{inicio} até {fim}"
                )

    else:

        # Mensagem exibida quando não existem eventos.
        st.warning("Nenhum evento cadastrado.")


# ============================================================
# 12. PÁGINA: BUSCAR EVENTOS
# ============================================================

# elif significa "senão, se".
#
# Essa página só aparece quando a opção selecionada
# no menu lateral for "Buscar eventos".

elif pagina == "Buscar eventos":

    st.subheader("🔎 Pesquisa de eventos")


    # --------------------------------------------------------
    # 12.1. ORGANIZAÇÃO DOS FILTROS
    # --------------------------------------------------------

    # Divide a área em duas colunas iguais.
    #
    # PERSONALIZÁVEL:
    # st.columns([1, 2]) cria uma coluna menor
    # e outra duas vezes maior.
    col1, col2 = st.columns(2)


    # Cria uma lista de classes sem repetições.
    #
    # e[1] representa a classe do objeto.
    # sorted() organiza em ordem alfabética.
    classes = sorted(set(e[1] for e in eventos))


    # Cria uma lista de vídeos sem repetições.
    #
    # e[0] representa o nome do vídeo.
    videos = sorted(set(e[0] for e in eventos))


    # --------------------------------------------------------
    # 12.2. FILTRO DE CLASSE
    # --------------------------------------------------------

    # Tudo dentro de with col1 aparece
    # na primeira coluna.
    with col1:

        # Cria uma caixa de seleção.
        #
        # "Todas" permite pesquisar todas as classes.
        #
        # O valor escolhido fica armazenado
        # na variável classe.
        classe = st.selectbox(
            "Tipo de objeto",
            ["Todas"] + classes
        )


    # --------------------------------------------------------
    # 12.3. FILTRO DE VÍDEO
    # --------------------------------------------------------

    with col2:

        # Permite selecionar um vídeo específico
        # ou pesquisar em todos os vídeos.
        video_filtro = st.selectbox(
            "Vídeo",
            ["Todos"] + videos
        )


    # --------------------------------------------------------
    # 12.4. BOTÃO DE PESQUISA
    # --------------------------------------------------------

    if st.button(

        # Texto exibido no botão.
        "Pesquisar eventos",

        # Utiliza o estilo principal definido no CSS.
        type="primary",

        # Faz o botão ocupar toda a largura disponível.
        use_container_width=True
    ):

        # Filtra os eventos que já foram carregados
        # do banco SQLite.
        #
        # Não executa uma nova consulta SQL.
        st.session_state.resultados = [

            e for e in eventos

            # Verifica se a classe corresponde
            # à classe selecionada pelo usuário.
            if (
                classe == "Todas"
                or e[1] == classe
            )

            # Verifica se o vídeo corresponde
            # ao vídeo selecionado.
            and (
                video_filtro == "Todos"
                or e[0] == video_filtro
            )
        ]

        # Limpa o evento anteriormente selecionado.
        #
        # Isso evita manter o vídeo de uma pesquisa anterior.
        st.session_state.selecionado = None


    # Recupera os resultados salvos na sessão.
    resultados = st.session_state.resultados


    # --------------------------------------------------------
    # 12.5. EXIBIÇÃO DOS RESULTADOS
    # --------------------------------------------------------

    # None significa que nenhuma pesquisa foi feita
    # nesta sessão.
    #
    # Uma lista vazia [] significa que a pesquisa
    # foi feita, mas não encontrou eventos.
    if resultados is not None:

        # Mostra a quantidade de eventos encontrados.
        st.write(
            f"**{len(resultados)} evento(s) encontrado(s)**"
        )


        # Percorre os eventos encontrados.
        #
        # enumerate() fornece:
        # i = posição do evento na lista.
        # video, objeto, inicio, fim = dados do evento.
        for i, (video, objeto, inicio, fim) in enumerate(resultados):


            # Cria um cartão para cada evento.
            with st.container(border=True):


                # Divide o cartão em duas colunas.
                #
                # [4, 1] significa:
                # esquerda = 4 partes.
                # direita = 1 parte.
                #
                # A coluna esquerda ocupa aproximadamente
                # 80% do espaço, desconsiderando o gap.
                #
                # PERSONALIZÁVEL:
                # [3, 1] deixa o botão com mais espaço.
                # [2, 1] aumenta ainda mais essa proporção.
                esquerda, direita = st.columns([4, 1])


                # --------------------------------------------
                # 12.6. INFORMAÇÕES DO EVENTO
                # --------------------------------------------

                with esquerda:

                    # Exibe a classe como título.
                    #
                    # #### cria um título Markdown nível 4.
                    st.markdown(
                        f"#### {objeto.capitalize()}"
                    )

                    # Exibe o vídeo e o intervalo detectado.
                    st.caption(
                        f"Vídeo: {video} | "
                        f"Início: {inicio} | Fim: {fim}"
                    )


                # --------------------------------------------
                # 12.7. BOTÃO ASSISTIR
                # --------------------------------------------

                with direita:

                    if st.button(

                        # Texto do botão.
                        "▶ Assistir",

                        # Cada botão precisa de uma chave
                        # diferente para o Streamlit
                        # identificar corretamente.
                        key=f"evento_{i}",

                        # Ocupa a largura da coluna.
                        use_container_width=True
                    ):

                        # Salva o índice do evento selecionado.
                        #
                        # Isso permite manter o vídeo
                        # selecionado após outras interações.
                        st.session_state.selecionado = i


                # --------------------------------------------
                # 12.8. REPRODUÇÃO DO VÍDEO
                # --------------------------------------------

                # Verifica se este é o evento selecionado.
                if st.session_state.selecionado == i:

                    # Monta o caminho do vídeo.
                    #
                    # Path(video).name extrai somente
                    # o nome do arquivo.
                    #
                    # Exemplo:
                    # videos/teste.mp4 -> teste.mp4
                    caminho = VIDEOS / Path(video).name


                    # Confere se o arquivo existe.
                    if caminho.is_file():

                        try:

                            # Cria o reprodutor de vídeo.
                            st.video(

                                # Caminho completo do arquivo.
                                str(caminho),

                                # Define em qual segundo
                                # o vídeo deve iniciar.
                                #
                                # Exemplo:
                                # "00:00:12" -> 12 segundos.
                                start_time=segundos(inicio)
                            )

                        # Captura erros de conversão do horário.
                        except ValueError:

                            st.error(
                                "Horário do evento inválido."
                            )

                    else:

                        # Informa que o arquivo não foi localizado.
                        st.warning(
                            f"Arquivo não encontrado: {caminho}"
                        )


# ============================================================
# 13. PÁGINA: BIBLIOTECA DE VÍDEOS
# ============================================================

elif pagina == "Vídeos":

    st.subheader("📁 Biblioteca de vídeos")


    # Verifica se a pasta videos existe.
    if VIDEOS.exists():

        # Procura todos os arquivos com extensão .mp4
        # diretamente dentro da pasta videos.
        #
        # glob("*.mp4") não procura em subpastas.
        # sorted() organiza os nomes.
        videos_locais = sorted(VIDEOS.glob("*.mp4"))

    else:

        # Se a pasta não existir, utiliza uma lista vazia.
        videos_locais = []


    # Verifica se encontrou arquivos.
    if videos_locais:

        # Percorre os arquivos encontrados.
        for arquivo in videos_locais:

            # Cria um cartão para cada vídeo.
            with st.container(border=True):

                # Mostra o nome do arquivo.
                #
                # arquivo.name retorna somente o nome,
                # sem o caminho completo.
                st.write(
                    f"🎞️ **{arquivo.name}**"
                )

                # Texto informativo.
                st.caption(
                    "Arquivo disponível localmente"
                )


                # Cria uma seção expansível.
                #
                # O usuário clica para abrir ou fechar.
                with st.expander("Reproduzir vídeo"):

                    # Exibe o vídeo completo.
                    #
                    # Diferentemente da busca de eventos,
                    # aqui não definimos start_time.
                    st.video(str(arquivo))

    else:

        # Mensagem quando nenhum MP4 foi encontrado.
        st.info(
            "Nenhum vídeo MP4 encontrado na pasta videos."
        )
