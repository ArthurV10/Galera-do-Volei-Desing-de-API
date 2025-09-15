# Importa o FastAPI
from fastapi import FastAPI

# Importa TODOS os módulos de rotas da pasta /routers
# Depois colocar avaliacoes e locais
from routers import auth, jogadores, convites, partidas

# Cria a instância principal do aplicativo FastAPI
app = FastAPI(
    title="API Galera do Vôlei",
    description="API completa para a comunidade online de praticantes de vôlei. Gerencie jogadores, partidas, inscrições e muito mais.",
    version="1.0.0"
)

# Inclui os routers no aplicativo principal
print("Registrando routers...")
app.include_router(auth.router)
app.include_router(jogadores.router)
app.include_router(convites.router)
# app.include_router(locais.router)
app.include_router(partidas.router)
# app.include_router(avaliacoes.router)
print("Routers registrados com sucesso.")

# 5. Cria um endpoint raiz ("/")
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API Galera do Vôlei! Acesse /docs para ver a documentação interativa."}