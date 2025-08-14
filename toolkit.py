import pandas as pd
import requests
from bs4 import BeautifulSoup

class CalcResult():
       
    def carrega_df(self):
        df = pd.read_pickle(r"bolao_final.pkl")
        # df_pos = df.loc[df['Posição']!=]
        return df

    def compara_df(self, df_alvo, df_artilheiro):
        df_geral = self.carrega_df()
        df_art = df_geral.loc[df_geral['Posição']=="Artilheiro"]
        df = df_geral.loc[df_geral["Posição"]!="Artilheiro"]
        lista_participantes = df['Nome'].unique().tolist()
        g6 = [1,2,3,4,5,6]
        z4 = [17,18,19,20]
        g6_alvo = df_alvo.loc[df_alvo["Posição"].isin(g6)]['Time'].tolist()
        z4_alvo = df_alvo.loc[df_alvo["Posição"].isin(z4)]['Time'].tolist()
        g6_alvo.sort()
        z4_alvo.sort()
        lista_final = []
        for participante in lista_participantes:
            score = 0
            cravadas = 0
            justificativa = ''
            df_participante = df.loc[df["Nome"]==participante]
            artilheiro_part = df_art.loc[df_art["Nome"]==participante]['Time/Jogador'].iloc[0]
            print(artilheiro_part)
            qtd_gols = df_artilheiro.loc[df_artilheiro["Jogador"]==artilheiro_part]["Gols"].iloc[0]
            g6_participante = df_participante.loc[df["Posição"].isin(g6)]["Time/Jogador"].tolist()
            z4_participante = df_participante.loc[df["Posição"].isin(z4)]["Time/Jogador"].tolist()
            g6_participante.sort()
            z4_participante.sort()
            if g6_alvo == g6_participante:
                score += 3
                justificativa += "3 pontos por acertar o G6 / "
            if z4_alvo == z4_participante:
                score += 3
                justificativa += "3 pontos por acertar o Z4 / "

            for idx, row in df_participante.iterrows():
                time = row["Time/Jogador"]
                pos = row["Posição"]
                df_alvo_temp = df_alvo.loc[df_alvo["Time"]==time]
                if len(df_alvo_temp)==0:
                    continue
                pos_alvo = df_alvo_temp["Posição"].iloc[0]

                #verifica se a posição é igual a posição alvo
                if pos == pos_alvo and pos_alvo==1:
                    score += 7
                    cravadas += 1
                    justificativa += f"7 pontos por acertar o campeão ({time})/ "
                elif pos == pos_alvo and pos_alvo!=1:
                    score += 6
                    cravadas += 1
                    justificativa += f"6 pontos por cravar a posição  ({time})/ "
                elif (pos_alvo in g6 and pos in g6) or (pos_alvo in z4 and pos in z4):
                    score += 2
                    justificativa += f"2 pontos por acertar a zona de classificação ({time})/ "
                elif (pos==1 and pos_alvo in z4) or (pos_alvo==1 and pos in z4):
                    score -= 10
                    justificativa += f"-10 pontos por colocar o campeão totalmente errado ({time})/ "
                elif (pos_alvo in g6 and pos in z4) or (pos_alvo in z4 and pos in g6):
                    score -= 7
                    justificativa += f"-7 pontos por errar a zona (ALO VANELLI) ({time})/ "
                
            lista_final.append(pd.DataFrame({'Nome':[participante],
                                            'Pontuação':[score],
                                            'JustificativaPontuação':[justificativa],
                                            'QtdGolsArtilheiro':[qtd_gols],
                                            'Cravadas':[cravadas]}))
        
        return pd.concat(lista_final)

    def organiza_posicao(self, df_pont):
        df_pont.sort_values(by=["Pontuação","QtdGolsArtilheiro","Cravadas"], ascending=False, inplace=True)
        # df_pont.drop(columns='ScoreDummy', inplace=True)
        df_pont['Posicao'] = range(1, len(df_pont) + 1)

        df_pont = df_pont[["Posicao", "Nome", "Pontuação", "JustificativaPontuação", "QtdGolsArtilheiro", "Cravadas"]]

        return df_pont
    
    def pega_lista_times(self):
        url = "https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-a/2025"

        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            td = soup.find_all("tr")
            nomes_times = []
            dicionario = {'Atlético Mineiro Saf' : 'Atlético Mineiro',
                            'Bahia' : 'Bahia',
                            'Botafogo' : 'Botafogo',
                            'Ceará' : 'Ceará',
                            'Corinthians' : 'Corinthians',
                            'Cruzeiro Saf' : 'Cruzeiro',
                            'Flamengo' : 'Flamengo',
                            'Fluminense' : 'Fluminense',
                            'Fortaleza Ec Saf' : 'Fortaleza',
                            'Grêmio' : 'Grêmio',
                            'Internacional' : 'Internacional',
                            'Juventude' : 'Juventude',
                            'Mirassol' : 'Mirassol',
                            'Palmeiras' : 'Palmeiras',
                            'Red Bull Bragantino' : 'Red Bull Bragantino',
                            'Santos Fc' : 'Santos',
                            'São Paulo' : 'São Paulo',
                            'Sport' : 'Sport',
                            'Vasco da Gama S.a.f.' : 'Vasco da Gama',
                            'Vitória' : 'Vitória',
                                                    }
            for tr in soup.find_all("strong"):
                texto = tr.get_text()
                if texto in dicionario.keys():
                    nomes_times.append(dicionario[texto]
                                        )
        return nomes_times

import streamlit as st

st.set_page_config(page_title="Bolão Brasileirão BXXT 2K25", layout="wide")
st.title("🏆 Bolão Brasileirão BXXT 2K25")

times_serie_a_2025 = CalcResult().pega_lista_times()
lista_art = ['Pedro/Flamengo',
'Lucas Moura/SP',
'Guilherme/Santos',
'Hulk/Atlético-MG',
'Yuri Alberto/Corinthians',
'memphis depay/corinthians',
]
lista_art.sort()
df_art = pd.DataFrame({"Jogador":lista_art})
df_art["Gols"] = 0
col1, col2, col3, col4, col5, col6 = st.columns(6)
with st.form("Dados"):
    with col1:
        primeiro = st.selectbox("1º Colocado", options=times_serie_a_2025, index=0)
        segundo = st.selectbox("2º Colocado", options=times_serie_a_2025, index=1)
        terceiro = st.selectbox("3º Colocado", options=times_serie_a_2025, index=2)
        quarto = st.selectbox("4º Colocado", options=times_serie_a_2025, index=3)
        quinto = st.selectbox("5º Colocado", options=times_serie_a_2025, index=4)
        sexto = st.selectbox("6º Colocado", options=times_serie_a_2025, index=5)
    with col2:
        dezessete = st.selectbox("17º Colocado", options=times_serie_a_2025, index=16)
        dezoito = st.selectbox("18º Colocado", options=times_serie_a_2025, index=17)
        dezenove = st.selectbox("19º Colocado", options=times_serie_a_2025, index=18)
        vinte = st.selectbox("20º Colocado", options=times_serie_a_2025, index=19)
    with col3:
        df_artilheiro = st.data_editor(df_art, hide_index=True)

    if st.form_submit_button("Calcular"):
        df = pd.DataFrame({"Time":[primeiro, segundo, terceiro, quarto, quinto, sexto, dezessete, dezoito, dezenove, vinte],
                           "Posição":[1,2,3,4,5,6,17,18,19,20]
        })
        df_base = CalcResult().compara_df(df_alvo=df, df_artilheiro=df_artilheiro)
        df_final = CalcResult().organiza_posicao(df_base)
        st.dataframe(df_final, hide_index=True)