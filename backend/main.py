import sqlite3
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
from ocr import extrair_respostas

app = FastAPI()

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 CRIA BANCO AUTOMATICAMENTE
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS provas (
    id TEXT PRIMARY KEY,
    nome TEXT,
    gabarito TEXT,
    respostas TEXT,
    nota INTEGER,
    total INTEGER
)
""")

conn.commit()


# 🔹 CRIAR PROVA
@app.post("/criar-prova/")
def criar_prova(nome: str, gabarito: str):
    prova_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO provas (id, nome, gabarito, respostas, nota, total)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (prova_id, nome, gabarito, "", 0, 0))

    conn.commit()

    return {"prova_id": prova_id}


# 🔹 CORRIGIR PROVA
@app.post("/corrigir/{prova_id}")
async def corrigir(prova_id: str, file: UploadFile = File(...)):

    caminho = "temp.png"

    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    respostas = extrair_respostas(caminho)

    # 🔥 BUSCA PROVA
    cursor.execute("SELECT gabarito FROM provas WHERE id = ?", (prova_id,))
    resultado_db = cursor.fetchone()

    if not resultado_db:
        return {"erro": "Prova não encontrada"}

    gabarito = resultado_db[0].split(",")

    score = 0
    resultado = []

    for i in range(len(gabarito)):
        if i < len(respostas) and respostas[i] == gabarito[i]:
            resultado.append(True)
            score += 1
        else:
            resultado.append(False)

    # 🔥 SALVA RESULTADO
    cursor.execute("""
        UPDATE provas
        SET respostas = ?, nota = ?, total = ?
        WHERE id = ?
    """, (",".join(respostas), score, len(gabarito), prova_id))

    conn.commit()

    return {
        "nota": score,
        "total": len(gabarito),
        "resultado": resultado,
        "respostas_detectadas": respostas
    }


# 🔹 LISTAR PROVAS
@app.get("/provas/")
def listar_provas():
    cursor.execute("SELECT * FROM provas")
    dados = cursor.fetchall()

    provas = []

    for p in dados:
        provas.append({
            "id": p[0],
            "nome": p[1],
            "gabarito": p[2],
            "respostas": p[3],
            "nota": p[4],
            "total": p[5]
        })

    return provas