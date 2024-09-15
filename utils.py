import pandas as pd
import plotly.express as px
from collections import Counter
from collections import defaultdict

def analiseGeralSimulado(df, nome_simulado, metric="Acertos"):

  # Pegando os alunos que fizeram o Simulado
  df_select = df[df['Simulados'].apply(
      lambda x: isinstance(x, dict) and
                nome_simulado in x and
                x[nome_simulado] is not None
  )]

  # Adquirindo as disciplinas do Simulado
  disciplinas = list(df_select.iloc[0]["Simulados"][nome_simulado][metric].keys())
  disciplinas_dict = {"Nome": [], "Periodo": [], "Genero": [], "Etnia": []}

  for disciplina in disciplinas:
    disciplinas_dict[disciplina] = []

  # Plotar uma matriz de acertos
  for i in range(len(df_select)):
    disciplinas_dict["Nome"].append(df_select.iloc[i]["nome"])
    disciplinas_dict["Periodo"].append(df_select.iloc[i]["periodo"])
    disciplinas_dict["Genero"].append(df_select.iloc[i]["genero"])
    disciplinas_dict["Etnia"].append(df_select.iloc[i]["etnia"])

    for disciplina in disciplinas:
      disciplinas_dict[disciplina].append(df_select.iloc[i]["Simulados"][nome_simulado][metric][disciplina])


  return disciplinas_dict, disciplinas

def getDesempenho(df_clusters, infos_df, i):
    # Nota Total média do cluster
    total_media = df_clusters.iloc[i]["Total"]

    # Obter os quartis e o máximo a partir do `infos_df`
    Q1 = infos_df.loc[infos_df['index'] == 'Total', '25%'].values[0]
    Q2 = infos_df.loc[infos_df['index'] == 'Total', '50%'].values[0]
    Q3 = infos_df.loc[infos_df['index'] == 'Total', '75%'].values[0]
    max_value = infos_df.loc[infos_df['index'] == 'Total', 'max'].values[0]
    min_value = infos_df.loc[infos_df['index'] == 'Total', 'min'].values[0]

    # Classificar o desempenho com base na nota Total
    if total_media == max_value:
        return "Excelente"
    elif total_media >= Q3:
        return "Muito Bom"
    elif total_media >= Q2:
        return "Bom"
    elif total_media >= Q1:
        return "Mediano"
    elif total_media == min_value:
        return "Necessita Melhorar"
    else:
        return "Analisar"
    
def getStudentsCluster(df, cluster):
    return df.query(f"Cluster == {cluster}")

def getStudentData(student):
    nome = student["nome"]
    simulados = student["Simulados"]

    # Dicionário para armazenar as notas por disciplina
    notas_dict = {
        "Total": [], "Português": [], "Literatura": [], "Matemática": [], "Física": [], "Química": [],
        "Biologia": [], "História": [], "Geografia": [], "Filosofia": [], "Sociologia": [], "Inglês": []
    }

    # Iterar sobre os simulados
    for key in simulados.keys():
        if key != "Colmeias_Inicial":
            disciplinas = simulados[key]["Acertos"]

            # Adicionar as notas ao dicionário de notas
            for disciplina, nota in disciplinas.items():
                if disciplina in notas_dict:
                    notas_dict[disciplina].append(nota)
                else:
                    notas_dict[disciplina] = [nota]

    # Dicionário para armazenar as médias calculadas
    scores_dict = {}

    # Calcular a média de cada disciplina
    for disciplina, notas in notas_dict.items():
        if len(notas) != 0:
            scores_dict[disciplina] = sum(notas) / len(notas)
        else:
            scores_dict[disciplina] = 0.0  # Caso não haja notas, retorna 0.0

    scores_dict["Nome"] = nome.strip()

    return scores_dict

def getClustersScore(df_students):
    colunas = ["Nome", "Total", "Português", "Literatura", "Matemática", "Física",
               "Química", "Biologia", "História", "Geografia", "Filosofia",
               "Sociologia", "Inglês"]
    df = pd.DataFrame(columns=colunas)

    return df

def analyzeStudent(df, cpf):
  cpf = cpf.replace(".", "")
  cpf = cpf.replace("-", "")
  student = df.query(f"cpf == '{cpf}'").index[0]

  return df.iloc[student]

def plot_acertos_por_materia(simulados, simulado):
    dados = simulados["Simulados"][simulado]

    materias = list(dados['Acertos'].keys())
    acertos = list(dados["Acertos"].values())

    fig = px.bar(x=materias, y=acertos, title=f'Acertos por Matéria - {simulado}', color=materias)
    fig.update_layout(xaxis_title='Matéria', yaxis_title='Acertos')

    return fig

def plot_histograma_erros(simulados, simulado):
    dados = simulados["Simulados"][simulado]
    erros = dados['Erros']
    contagem_erros = Counter(erros)

    fig = px.bar(
        x=list(contagem_erros.keys()),
        y=list(contagem_erros.values()),
        labels={'x':'Erros por Matéria', 'y':'Frequência'},
        title=f'Histograma de Erros - {simulado}',
        color_discrete_sequence=['salmon']
    )
    fig.update_xaxes(tickangle=-45)
    return fig

def plot_distribuicao_scores(simulados, simulado):
    dados = simulados["Simulados"][simulado]
    if 'Score' in dados:
        materias = list(dados['Score'].keys())
        scores = list(dados['Score'].values())

        fig = px.bar(
            x=materias,
            y=scores,
            labels={'x': 'Matérias', 'y': 'Score'},
            title=f'Distribuição de Scores por Matéria - {simulado}',
            color_discrete_sequence=['lightgreen']
        )
        fig.update_xaxes(tickangle=-45)
        return fig
    
