import streamlit as st
import sqlite3

BANCO = "cftv.db"

st.set_page_config(
    page_title="Sistema Inteligente de CFTV",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 Sistema Inteligente de CFTV")

st.write(
    "Busque objetos identificados automaticamente nas gravações."
)

st.divider()

opcao = st.selectbox(
    "O que você deseja procurar?",
    ["Selecione...", "Pessoa", "Carro", "Motocicleta"]
)

if st.button("Buscar"):

    if opcao == "Selecione...":
        st.warning("Selecione um objeto para realizar a busca.")

    else:
        busca = opcao.lower()

        conexao = sqlite3.connect(BANCO)
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT video, classe, inicio, fim
            FROM eventos
            WHERE classe = ?
            ORDER BY inicio
            """,
            (busca,)
        )

        resultados = cursor.fetchall()

        conexao.close()

        if resultados:

            st.success(
                f"{len(resultados)} evento(s) encontrado(s)."
            )

            for video, classe, inicio, fim in resultados:

                st.subheader(classe.capitalize())

                st.write(f"**Vídeo:** {video}")

                if inicio == fim:
                    st.write(f"**Momento:** {inicio}")
                else:
                    st.write(
                        f"**Intervalo:** {inicio} até {fim}"
                    )

                st.divider()

        else:
            st.error(
                f"Nenhum resultado encontrado para '{busca}'."
            )