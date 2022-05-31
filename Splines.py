import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def cria_matriz_A(y, h):
    '''
    Cria a matriz A

    y = lista de valores de y
    h = lista de espaçamento entre pontos
    
    matriz = retorna a matriz A calculada
    '''
    n = len(y)
    # Cria a matriz apenas com zeros inicialmente
    matriz = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            # Calcula os valores da diagonal principal - 1 na primeira e última linha e 2 * (h[k+1] + h[k]) nas demais
            if (i == j):
                if (i == 0 or i == n - 1):
                    matriz[i][j] = 1

                else:
                    matriz[i][j] = 2 * (h[i-1] + h[i])

            # Calcula os valores da diagonal acima principal - 0 última linha e [k+1] nas demais
            elif (i - j == -1):
                if (i == 0):
                    matriz[i][j] = 0

                else:
                    matriz[i][j] = h[i]

            # Calcula os valores da diagonal abaixo principal - 0 na primeira linha e h[k] nas demais
            elif (i - j == 1):
                if (i == n - 1):
                    matriz[i][j] = 0

                else:
                    matriz[i][j] = h[i-1]

    return matriz


def cria_matriz_B(y, h):
    '''
    Cria a matriz B

    y = lista de valores de x
    h = lista de espaçamento entre pontos
    
    matriz = retorna a matriz b calculada
    '''
    n = len(y)
    # Cria a matriz apenas com zeros inicialmente
    matriz = np.zeros((n, 1), dtype=float)

    for i in range(n):
        if (i != 0 and i != n-1):  # Garante que a primeira e última linha permaneçam apenas com 0
            matriz[i][0] = (3 * ((y[i+1] - y[i]) / h[i])) - \
                (3 * ((y[i] - y[i-1])/h[i-1]))

    return matriz


def spline_cubica(x, y, n):
    '''
    Realiza o cálculo da spline cúbica natural

    x = lista de valores de y
    y = lista de valores de y
    n = número de pontos a serem adicionados em cada espaçamentos
    
    lista_x = retorna os valores de x apos a spline
    lista_y = retorna os valores de y apos a spline
    '''
    h = []

    # Loop para calcular cada valor de h - o intervalo entre x[k] e x[k+1]
    for i in range(len(x)-1):
        h.append(x[i+1] - x[i])

    matriz_A = cria_matriz_A(y, h)
    matriz_b = cria_matriz_B(y, h)

    # Usa-se o numpy para resolução da matriz g
    g = np.linalg.solve(matriz_A, matriz_b)

    lista_x = []
    lista_y = []

    x_i = x[0]

    for k in range(len(g)-1):  # Loop para gerar cada uma das funções S; k vai até n-1
        # É calculado cada coeficiente dentro do loop
        a = ((g[k+1] - g[k]) / (3 * h[k]))
        b = g[k]
        c = (1 / h[k]) * (y[k + 1] - y[k]) - (h[k] / 3) * (2 * g[k] + g[k+1])
        d = y[k]

        # Segundo loop para calcular os pontos intermediários no intervalo da função
        while (x_i <= x[k+1]):
            y_i = a * ((x_i - x[k]) ** 3) + b * \
                ((x_i - x[k]) ** 2) + c * (x_i - x[k]) + d

            lista_y.append(y_i[0])
            lista_x.append(x_i)

            x_i += h[k]/(n+1)

    return (lista_x, lista_y)


def itera_tabela(cotas):
    '''
    Realiza a spline para cada par de listas

    cotas = dataframe das cotas
    
    lista_x = retorna os valores de x apos a spline
    lista_y = retorna os valores de y apos a spline
    matriz_y = lista com as listas de valores y
    '''
    x = cotas.index.values
    matriz_y = []

    for column in cotas:
        y = cotas[column].to_numpy()
        lista_x, lista_y = spline_cubica(x, y, n)

        matriz_y.append(lista_y)

    return lista_x, lista_y, matriz_y


def atualiza_xlsx(cotas, matriz_y, lista_x):
    '''
    Atualiza o arquivo com as cotas e pontos intermediários

    cotas = dataframe das cotas
    matriz_y = lista com as listas de valores y
    
    novas_cotas = dataframe atualizado
    '''
    dict_y = {}
    labels = list(cotas.columns)

    i = 0
    for lista in matriz_y:  # Cria um dicionário com as labels de chaves a partir da matriz de y
        dict_y[labels[i]] = lista
        i += 1

    # Gera o arquivo onde serão inseridos os pontos intermediários
    novas_cotas = pd.DataFrame(data=dict_y, index=lista_x)
    novas_cotas.to_excel(writer)
    writer.save()

    return novas_cotas


if __name__ == "__main__":
    # O programa é iniciado lendo o arquivo de cotas
    cotas = pd.read_excel("cotas.xlsx", index_col=0)

    # Definição do escritor do objeto excel com a tabela final
    writer = pd.ExcelWriter('cotas_splined.xlsx')

    n = 20  # Definição do número de pontos intermediários

    plt.axis("equal")  # Definição dos eixos dos gráficos como iguais entre si

    # Calcula os pontos intermediários das balizas
    lista_x, lista_y, matriz_y = itera_tabela(cotas)
    novas_cotas = atualiza_xlsx(cotas, matriz_y, lista_x)

    # Transpõe a tabela de cotas para calcular o outro eixo
    cotas_transpostas = pd.DataFrame(data=novas_cotas).T

    # Calcula os pontos intermediários das linhas d'água
    lista_x_t, lista_y_t, matriz_y_t = itera_tabela(cotas_transpostas)
    novas_cotas = atualiza_xlsx(cotas_transpostas, matriz_y_t, lista_x_t)

    # Transpõe novamente a tabela de cotas para voltar a configuração inicial
    novas_cotas = pd.DataFrame(data=novas_cotas).T
    novas_cotas.to_excel(writer)
    writer.save()
