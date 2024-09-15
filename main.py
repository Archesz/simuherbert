import streamlit as st

from pymongo import MongoClient
import pandas as pd
from collections import Counter
from collections import defaultdict
import numpy as np
# Gráficos
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.subplots as sp
import seaborn as sns
import matplotlib.pyplot as plt
import utils 

from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from Database import Database

st.set_page_config(layout="wide")

database = Database()
df = database.getAllStudents()
disciplinas = ["Matemática", "Física", "Química", "Biologia", "Geografia", "História", "Filosofia", "Sociologia", "Português", "Literatura", "Inglês"]
simulados = ["Unicamp_00001", "USP_00001", "Unicamp_00003"]

st.title("Herbert Analisa")

st.write("Geral: Análise geral dos simulados. Oferece uma visão ampla sobre como os estudantes do projeto estão no momento com todas as disciplinas.")
st.write("Disciplinas: Analise os simulados a partir das disciplinas e seus resultados.")
st.write("Aluno: Verifique o desempenho individual dos estudantes")

geral, disciplinas_tab, aluno, grupos = st.tabs(["Geral", "Disciplinas", "Aluno", "Grupos"])


with geral:
    st.subheader("Geral")
    
    st.write("Abaixo, temos a relação de cada disciplina e seu impacto na prova como um todo. Gráficos com as linhas 'Crescentes' significam que os alunos estão indo melhor na prova conforme vão bem na matéria, enquanto linhas 'Decrescentes' significam que alunos estão mal nas outras matérias em relação a sua.")
    st.write("Quanto mais inclinada para 'Cima' a reta for, mais impacto a disciplina em questão teve em relação as outras disciplinas.")
    
    nome_simulado = st.selectbox("Selecione o simulado: ", simulados, key="Simulado_geral")
    disciplinas_dict, disciplinas = utils.analiseGeralSimulado(df.query("curso == 'Pré-Vestibular'"), nome_simulado)

    df_disciplinas = pd.DataFrame(disciplinas_dict)
    df_disciplinas = df_disciplinas.drop_duplicates(subset=disciplinas)
    
    disciplina = "Total"

    for i in disciplinas:
        if i != disciplina:
            fig = px.scatter(df_disciplinas, x=disciplina, y=i, size="Total", hover_name="Nome",
                            marginal_x="rug", marginal_y="rug", title=f"Comparação de {disciplina} x {i}", trendline="ols", color="Periodo")
            st.plotly_chart(fig)
    
    # Matriz de correlação
    st.write("Abaixo, temos a correlação de cada disciplina com as demais. Quanto maior o número, mais relacionada estão as disciplinas.")
    correlation_matrix = df_disciplinas.query("Periodo == 'Noturno'")[disciplinas].corr()
    plt.figure(figsize=(10, 8))
    fig = sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5, vmin=-1, vmax=1)
    plt.title('Matriz de Correlação')
    st.pyplot(plt.gcf())
    
    
    
with disciplinas_tab:
    st.subheader("Disciplinas")
    
    nome_simulado = st.selectbox("Selecione o simulado: ", simulados)
    disciplinas_dict, disciplinas = utils.analiseGeralSimulado(df.query("curso == 'Pré-Vestibular'"), nome_simulado)

    df_disciplinas = pd.DataFrame(disciplinas_dict)
    df_disciplinas = df_disciplinas.drop_duplicates(subset=disciplinas)
    
    disciplina = st.selectbox("Selecione a disciplina: ", disciplinas)
    
    # Tabela dos alunos
    df_sorted = df_disciplinas.sort_values(by=disciplina, ascending=False)
    describe = df_sorted[disciplina].describe()
    describe = describe.rename({'count': 'Contagem', 'mean': 'Média', 'std': 'Desvio Padrão', 'min': 'Mínimo', '25%': '1º Quartil (25%)', '50%': 'Mediana (50%)', '75%': '3º Quartil (75%)', 'max': 'Máximo' })
    col_1, col_2 = st.columns(2)
    
    with col_1:
        st.write("Tabela do desempenho dos estudantes na disciplina")
        st.dataframe(df_sorted[["Nome", disciplina]])
    with col_2:
        st.subheader("Informações Resumidas")
        st.dataframe(describe)
    
    # Período e Sexo
    fig_1 = px.box(df_disciplinas, x="Periodo", y=disciplina, color="Genero", title=f"Distribuição da {disciplina} por período")
    st.plotly_chart(fig_1)

    # Período
    fig_2 = px.histogram(df_disciplinas, disciplina, title="Distribuição das notas na Disciplina por Período", color="Periodo", labels={"count": "Quantidade"}, facet_col="Periodo",
                   marginal="violin", text_auto=True)
    st.plotly_chart(fig_2)
    
    # Notas total
    fig_3 = px.histogram(df_disciplinas, disciplina, title="Distribuição das notas na Disciplina", labels={"count": "Quantidade"}, marginal="violin", text_auto=True)
    st.plotly_chart(fig_3)

    # Etnia
    fig_4 = px.box(df_disciplinas, x="Genero", y=disciplina, color="Etnia", title=f"Distribuição de {disciplina} por Gênero e Etnia")
    st.plotly_chart(fig_4)
    
with aluno:
    st.subheader("Aluno Específico")

    students_cpf = database.getNomeCpfDict()
    names = students_cpf.keys()
    
    student_select = st.selectbox("Selecione o estudante", names)
    
    student_select = utils.analyzeStudent(df, students_cpf[student_select])

    st.write(f'Nome: {student_select["nome"]} | Gênero: {student_select["genero"]} | Etnia: {student_select["etnia"]}') 
    simulado_select = st.selectbox("Selecione o simulado: ", student_select["Simulados"].keys(), key="simulado_individual")
    
    fig_001 = utils.plot_acertos_por_materia(student_select, simulado_select)
    st.plotly_chart(fig_001)
    
    try:
        fig_002 = utils.plot_histograma_erros(student_select, simulado_select)
        st.plotly_chart(fig_002)
    except:
        pass
    
    
    
with grupos:
    st.subheader("Grupos | Clusters")
    st.write("Abaixo, temos separação de grupos dos alunos, permitindo analisar estudantes com déficits em comum.")

    colunas = ["Nome", "Total", "Português", "Literatura", "Matemática", "Física",
            "Química", "Biologia", "História", "Geografia", "Filosofia",
            "Sociologia", "Inglês"]

    df_prov = pd.DataFrame(columns=colunas)

    for i in range(0, len(df)):
        student = df.iloc[i]
        try:
            scores = utils.getStudentData(student)
            if scores["Total"] != 0:
                linha_df = pd.DataFrame([scores])
                df_prov = pd.concat([df_prov, linha_df], ignore_index=True)
        except:
            continue

    names = df_prov["Nome"]
    df_prov = df_prov.drop(["Nome"], axis=1).drop_duplicates()
    df_prov["Nome"] = names
    notas = df_prov.drop(columns=["Nome"])

    # Aplicando a normalização
    scaler = MinMaxScaler()
    notas_normalizadas = scaler.fit_transform(notas)

    # Criando um novo DataFrame com os dados normalizados
    df_normalizado = pd.DataFrame(notas_normalizadas, columns=notas.columns)

    # Criando o modelo K-Means
    kmeans = KMeans(n_clusters=6, random_state=42)
    kmeans.fit(df_normalizado)
    df_prov["Cluster"] = kmeans.labels_

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(df_normalizado)

    # Adicionando os resultados do PCA ao DataFrame
    df_prov["PCA1"] = pca_result[:, 0]
    df_prov["PCA2"] = pca_result[:, 1]

    df_clusters = df_prov.drop(["Nome"], axis=1).groupby("Cluster").mean().reset_index()
    infos_df = df_clusters.describe().T.reset_index()

    clusters_dict = {}

    for i in range(len(df_clusters)):
        cluster = int(df_clusters.iloc[i]["Cluster"])
        clusters_dict[cluster] = {
            "Desempenho": utils.getDesempenho(df_clusters, infos_df, i),
            "Número de Alunos": len(df_prov.query(f"Cluster == {i}"))
        }

    # Mapeando desempenho ao cluster
    desempenho_to_cluster = {v["Desempenho"]: k for k, v in clusters_dict.items()}

    # Seletor baseado em desempenho
    desempenho_selecionado = st.selectbox("Selecione o desempenho:", list(desempenho_to_cluster.keys()))

    # Obter o cluster correspondente ao desempenho selecionado
    cluster_selecionado = desempenho_to_cluster[desempenho_selecionado]

    # Obter os alunos do cluster selecionado
    students_cluster = utils.getStudentsCluster(df_prov, cluster_selecionado)

    # Exibir os alunos do cluster selecionado
    st.write(f"Alunos do Cluster com Desempenho: {desempenho_selecionado}")
    st.write(students_cluster)
    st.write(clusters_dict)
    # Exibir os dados dos clusters e o dicionário final
