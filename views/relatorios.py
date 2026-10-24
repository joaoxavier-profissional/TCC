"""Gráficos e exportação CSV dos eventos indexados."""
from collections import Counter
import pandas as pd
import streamlit as st

def mostrar_relatorios(eventos):
    st.subheader('Análise das detecções')
    if not eventos:
        st.info('Não existem eventos para gerar relatórios.')
    else:
        por_classe = Counter((classe for video, classe, inicio, fim in eventos))
        por_video = Counter((video for video, classe, inicio, fim in eventos))
        esquerda, direita = st.columns(2)
        with esquerda:
            st.markdown('**Eventos por classe**')
            dados_classes = pd.DataFrame([{'Classe': classe.capitalize(), 'Eventos': quantidade} for classe, quantidade in sorted(por_classe.items())])
            dados_classes = dados_classes.set_index('Classe')
            st.bar_chart(dados_classes, color='#28d4bd')
        with direita:
            st.markdown('**Eventos por gravação**')
            dados_videos = pd.DataFrame([{'Vídeo': video, 'Eventos': quantidade} for video, quantidade in sorted(por_video.items())])
            dados_videos = dados_videos.set_index('Vídeo')
            st.bar_chart(dados_videos, color='#28d4bd')
        st.subheader('Eventos registrados')
        tabela = pd.DataFrame(eventos, columns=['Vídeo', 'Classe', 'Início', 'Fim'])
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        st.download_button('Exportar eventos para CSV', data=tabela.to_csv(index=False).encode('utf-8-sig'), file_name='relatorio_eventos_cftv.csv', mime='text/csv')
        st.caption('Relatórios calculados a partir dos eventos armazenados no SQLite.')
