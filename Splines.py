import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def cria_matriz_A(y, h):
    '''
    Cria a matriz A

    y = lista de valores de y
    h = lista de espaçamento entre pontos
    '''
    n = len(y)
    matriz = np.zeros((n, n), dtype=float) # Cria a matriz apenas com zeros inicialmente

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
    '''
    n = len(y)
    matriz = np.zeros((n, 1), dtype=float) # Cria a matriz apenas com zeros inicialmente

    for i in range(n):
        if (i != 0 and i != n-1): # Garante que a primeira e última linha permaneçam apenas com 0
            matriz[i][0] = (3 * ((y[i+1] - y[i]) / h[i])) - \
                (3 * ((y[i] - y[i-1])/h[i-1]))

    return (matriz)


def spline_cubica(x, y, n):
    '''
    Realiza o cálculo da spline cúbica natural

    x = lista de valores de y
    y = lista de valores de y
    n = número de pontos a serem adicionados em cada espaçamentos
    '''
    h = []

    # Loop para calcular cada valor de h - o intervalo entre x[k] e x[k+1]
    for i in range(len(x)-1):
        h.append(x[i+1] - x[i])

    matriz_A = cria_matriz_A(y, h)
    matriz_b = cria_matriz_B(y, h)

    g = np.linalg.solve(matriz_A, matriz_b) # Usa-se o numpy para resolução da matriz g

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


if __name__ == "__main__":
    cotas = pd.read_excel(r"cotas.xlsx") # O programa é iniciado lendo o arquivo de cotas
    cotas.reset_index(drop=True)
    
    writer = pd.ExcelWriter('cotas_splined.xlsx') # Definição do escritor do objeto excel com a tabela final
    
    n = 20 # Definição do número de pontos intermediários

    is_x = True
    y_temp = []
    for column in cotas:
        if is_x: # A primeira coluna da tabela serão os valores X das balizas
            x = cotas[column].to_numpy()
            is_x = False
            
        else:
            y = cotas[column].to_numpy()
            lista_x, lista_y = spline_cubica(x, y, n)

            y_temp.append(lista_y)
            plt.plot(lista_x, lista_y, "k")

    plt.axis("equal")
    plt.savefig("boat.png", transparent=False, dpi=120)
    
    matriz_y = {}
    labels = list(cotas.columns)[1:]
    
    i = 0
    for lista in y_temp:
        matriz_y[ labels[i] ] = lista
        i += 1
            
    novas_cotas = pd.DataFrame(data=matriz_y, index=lista_x) # Gera o arquivo onde serão inseridos os pontos intermediários
    novas_cotas.to_excel(writer)
    writer.save()
