import numpy as np
import matplotlib.pyplot as plt

def cria_matriz_A(y, h):
    '''
    Cria a matriz A, com 4h na diagonal principal e h nas imediatas lateirais,
    considerando espaçamento uniforme de pontos (hk = h)

    y = lista de valores de y
    h = espaçamento entre pontos
    '''
    n = len(y) - 2
    matriz = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if (i == j):
                matriz[i][j] = 4*h

            elif (i - j == 1 or j - i == 1):
                matriz[i][j] = h

    return matriz


def cria_matriz_B(y, h):
    '''
    Cria a matriz B, considerando espaçamento uniforme de pontos (hk = h)

    y = lista de valores de x
    h = espaçamento entre pontos
    '''   
    matriz = np.array([(6/h) * (y[2] - 2*y[1] + y[0]),
                       (6/h) * (y[3] - 2*y[2] + y[1]),
                       (6/h) * (y[4] - 2*y[3] + y[2]),
                       ])

    return (matriz, h)


def spline_cubica(x, y, n):
    '''
    Realiza o cálculo da spline cúbica natural

    x = lista de valores de y
    y = lista de valores de y
    n = número de pontos a serem adicionados em cada espaçamentos
    '''
    h = x[2] - x[1]
    
    matriz_A = cria_matriz_A(y, h)
    matriz_b, h = cria_matriz_B(y, h)
    
    g = np.linalg.solve(matriz_A, matriz_b)
    g = np.insert(g, [0, g.size], [0, 0]) # insere os 0 para S0 e Sn, uma vez que a spline é natural
   
    lista_x = []
    lista_y = []
    
    x_i = x[0]
    
    for k in range(len(g)-1): # loop para gerar cada uma das funções S; k vai até n-1
        x_temp = []
        y_temp = []
            
        a = (g[k+1] - g[k]) / (6*h)
        b = g[k+1]/2
        c = ((y[k+1] - y[k]) / h) + ((2*h*g[k+1] + g[k]*h) / 6)
        d = y[k+1]
    
        while (x_i <= x[k+1]): # loop para calcular os pontos intermediários no intervalo da função q
            y_i = a * ((x[k] - x_i) **3) + b * ((x[k] - x_i) **2) + c * (x[k] - x_i) + d
            
            y_temp.append(y_i)
            lista_x.append(x_i)
            
            x_i += h/(n+1)

        lista_y.extend(y_temp[::-1])
    
    return (lista_x, lista_y)
            

if __name__ == "__main__":
    n = int(input("Quantidade de pontos a serem criados entre cada espaçamento: "))

    y = np.array([0, 0.375, 0, -0.375, 0])
    x = np.array([0, 0.5, 1, 1.5, 2])

    lista_x, lista_y = spline_cubica(x, y, n)
    
    plt.plot(x, y, 'ro')
    plt.plot(lista_x, lista_y)
    plt.show()
