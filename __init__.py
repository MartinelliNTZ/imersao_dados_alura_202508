import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pycountry


df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")


def rename_columns(base):
    # Dicionário de tradução de colunas para português
    traducao_colunas = {
        'work_year': 'ano',
        'experience_level': 'senioridade',
        'employment_type': 'contrato',
        'job_title': 'cargo',
        'salary': 'salario',
        'salary_currency': 'moeda',
        'salary_in_usd': 'usd',
        'employee_residence': 'residencia',
        'remote_ratio': 'remoto',
        'company_location': 'empresa',
        'company_size': 'tamanho_empresa'
    }

    # Renomeando as colunas com base no dicionário acima
    base = base.rename(columns=traducao_colunas)
    return base
def rename_categories(base):
    # Dicionários para traduzir os códigos das colunas categóricas para nomes legíveis
    mapa_senioridade = {
        'SE': 'Sênior',
        'MI': 'Pleno',
        'EN': 'Júnior',
        'EX': 'Executivo'
    }

    mapa_contrato = {
        'FT': 'Tempo Integral',
        'PT': 'Meio Período',
        'CT': 'Contrato',
        'FL': 'Freelancer'
    }

    mapa_remoto = {
        0: 'Presencial',
        50: 'Híbrido',
        100: 'Remoto'
    }

    mapa_tamanho_empresa = {
        'S': 'Pequena',
        'M': 'Média',
        'L': 'Grande'
    }

    # Aplicando as traduções nas colunas
    base['senioridade'] = base['senioridade'].map(mapa_senioridade)
    base['contrato'] = base['contrato'].map(mapa_contrato)
    base['remoto'] = base['remoto'].map(mapa_remoto)
    base['tamanho_empresa'] = base['tamanho_empresa'].map(mapa_tamanho_empresa)
    return base
def clean_data(base):
    # Limpando dados inconsistentes
    base = base.dropna()
    base = base.assign(ano=base['ano'].astype('int64'))
    base = base.assign(salario=base['salario'].astype('float64'))
    return base
def show_clean_data(base):
    # Mostrando os dados limpos
    print(base.head())
    print(base.info())
    print(base.describe())
    print(base.isnull().sum())
    print(base['ano'].unique())
    print(base[base.isnull().any(axis= 1)])
    df_clean = df.dropna()
    df_clean = df_clean.assign(ano=df_clean['ano'].astype('int64'))
    print(df_clean.isnull().sum())
    print(df_clean.head())
    # print(df_clean['ano'].unique())
    # print(df_clean[df_clean.isnull().any(axis= 1)])
def show_seniority_distribution():
    df_clean['senioridade'].value_counts().plot(kind='bar', title='Distribuição de Sênioridade')
    plt.show()
def show_salary_bar(base):
    param = base.groupby('senioridade')['usd'].mean().sort_values(ascending=False).index
    plt.figure(figsize=(8, 5))
    sns.barplot(data=base, x='senioridade', y='usd', order=param)
    plt.title('Salário Médio por Sênioridade')
    plt.xlabel('Sênioridade')
    plt.ylabel('Salário médio anual (U$D)')
    plt.show()
def show_salary_histogram(base):
    plt.figure(figsize=(8, 6))
   # sns.histplot(data=base, x='usd', bins=50, kde=True)
    sns.histplot(base['usd'], bins=150, kde=True)
    plt.title('Distribuição dos Salários anuais')
    plt.xlabel('Salário (U$D)')
    plt.ylabel('Frequência')
    plt.show()
def show_salary_boxplot(base):
   # print(base['senioridade'].value_counts().unique())
    order = ['Júnior', 'Pleno', 'Sênior', 'Executivo']
    plt.figure(figsize=(8, 6))
    #, showfliers=False tira os outliers
    sns.boxplot(data=base, x='senioridade', y='usd', order=order,palette='Set2',hue='senioridade')
    plt.title('Distribuição dos Salários por Sênioridade')
    plt.xlabel('Sênioridade')
    plt.ylabel('Salário (U$D)')
    plt.show()
def show_salary_plotly(base):
    # Calcula a média salarial por senioridade
    df_mean = base.groupby('senioridade', as_index=False)['usd'].mean()

    # Ordena na ordem desejada
    ordem = ['Júnior', 'Pleno', 'Sênior', 'Executivo']
    df_mean['senioridade'] = pd.Categorical(df_mean['senioridade'], categories=ordem, ordered=True)
    df_mean = df_mean.sort_values('senioridade')

    # Cria o gráfico interativo
    fig = px.bar(
        df_mean,
        x='senioridade',
        y='usd',
        text='usd',
        title='Média Salarial por Sênioridade',
        labels={'senioridade': 'Sênioridade', 'usd': 'Salário Médio (USD)'},
        color='senioridade',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Ajusta exibição dos valores no topo das barras
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Ajusta layout
    fig.update_layout(
        xaxis_title='Sênioridade',
        yaxis_title='Salário Médio (USD)',
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    fig.show()
def show_contract_pie(base):
    # Calcula a porcentagem de contratos por tipo
    count_contract = base['contrato'].value_counts().reset_index()
    count_contract.columns = ['Tipo de Trabalho', 'Quantidade']
    count_contract['porcentagem'] = count_contract['Quantidade'] / count_contract['Quantidade'].sum() * 100
    count_contract = count_contract.sort_values('Quantidade', ascending=False)
    # Cria o gráfico de pizza
    fig = px.pie(
        count_contract,
        names='Tipo de Trabalho',
        values='Quantidade',
        title='Distribuição de Tipos de Trabalho',
        hole=0.5,)
    fig.update_traces( textinfo='percent+label')
    fig.show()
def create_iso3_reference(base):
    # Criar nova coluna com código ISO-3
    base['residencia_iso3'] = base['residencia'].apply(iso2_to_iso3)
    return base
def show_map_country(base):
    # Calcular média salarial por país (ISO-3)
    df_ds = base[base['cargo'] == 'Data Scientist']
    media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()

    # Gerar o mapa
    fig = px.choropleth(media_ds_pais,
                        locations='residencia_iso3',
                        color='usd',
                        color_continuous_scale='rdylgn',
                        title='Salário médio de Cientista de Dados por país',
                        labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})

    fig.show()
def iso2_to_iso3(code):
    """
    Converte o código ISO 2 para ISO 3
    :param code: codigo ISO 2
    :return: codigo ISO 3
    """
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None



df = rename_columns(df)
df = rename_categories(df)
df_clean = clean_data(df)
df_clean = create_iso3_reference(df_clean)
show_map_country(df_clean)
#df_clean.to_csv('base_salaries_clean.csv', index=False)






