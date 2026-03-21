import cv2
import numpy as np

def extrair_respostas(caminho_imagem):
    img = cv2.imread(caminho_imagem)

    if img is None:
        raise Exception("Erro ao carregar imagem")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    altura, largura = gray.shape

    num_questoes = 8
    num_alternativas = 4

    # 🔥 remove bordas
    margem_y = int(altura * 0.03)
    margem_x = int(largura * 0.03)

    gray = gray[margem_y:altura-margem_y, margem_x:largura-margem_x]

    altura, largura = gray.shape

    altura_linha = altura / num_questoes   # 🔥 agora float

    largura_coluna = largura // num_alternativas

    respostas = []
    alternativas = ["A", "B", "C", "D"]

    for i in range(num_questoes):
        y1 = int(i * altura_linha)
        y2 = int((i + 1) * altura_linha)

        linha = gray[y1:y2, :]

        intensidades = []

        for j in range(num_alternativas):
            x1 = j * largura_coluna
            x2 = (j + 1) * largura_coluna

            celula = linha[:, x1:x2]

            h, w = celula.shape

            roi = celula[int(h*0.35):int(h*0.65), int(w*0.35):int(w*0.65)]

            _, binaria = cv2.threshold(roi, 170, 255, cv2.THRESH_BINARY_INV)

            total = cv2.countNonZero(binaria)

            intensidades.append(total)

        print(f"Linha {i+1}:", intensidades)

        marcado = np.argmax(intensidades)

        respostas.append(alternativas[marcado])

    print("RESPOSTAS DETECTADAS:", respostas)

    return respostas