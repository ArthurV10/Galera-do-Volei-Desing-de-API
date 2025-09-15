from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID, uuid4

# Importa os schemas que definimos
import schemas

# ===================================================================
#           DEPENDÊNCIA DE AUTENTICAÇÃO (MOCK)
# ===================================================================

# Em um projeto real, esta função validaria o token JWT e retornaria
# o usuário correspondente do banco de dados.
def get_current_user_mock() -> schemas.Jogador:
    """Simula a obtenção do usuário logado a partir de um token."""
    return schemas.Jogador(
        id=uuid4(), 
        nome="Arthur Mock Logado", 
        email="arthur@email.com", 
        sexo="Masculino", 
        data_nascimento="1998-05-20"
    )

# ===================================================================
#           LÓGICA DE SENHA (AUXILIAR)
# ===================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha em texto plano com a senha 'hasheada' do banco."""
    # Lógica real usaria uma biblioteca como passlib:
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # return pwd_context.verify(plain_password, hashed_password)
    print(f"Verificando se '{plain_password}' corresponde a '{hashed_password}'")
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    # Lógica real usaria: return pwd_context.hash(password)
    print(f"Gerando hash para a senha '{password}'")
    return f"hashed_{password}"

# ===================================================================
#                           ROUTER
# ===================================================================

router = APIRouter(
    prefix="/jogadores",
    tags=["Jogador"]
)

# ===================================================================
#                           ENDPOINTS
# ===================================================================

@router.post("/", response_model=schemas.Jogador, status_code=status.HTTP_201_CREATED)
def criar_jogador(jogador_data: schemas.JogadorCreate):
    """
    Cria (registra) um novo jogador na plataforma a partir de um convite.
    """
    print(f"Tentando criar jogador: {jogador_data.nome} com o convite '{jogador_data.token_convite}'")
    
    # 1. Verificar se o token de convite é válido
    if jogador_data.token_convite != "token_valido_recebido_por_email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de convite inválido ou expirado."
        )
    
    # Hashear a senha antes de salvar
    senha_hashed = get_password_hash(jogador_data.senha)
    
    # TODO: Salvar o novo jogador no banco de dados
    
    # Retornando um objeto mockado que corresponde ao schema de resposta
    novo_jogador_db = schemas.Jogador(
        id=uuid4(),
        **jogador_data.dict()
    )
    
    return novo_jogador_db

@router.get("/me", response_model=schemas.Jogador)
def ler_jogador_atual(current_user: schemas.Jogador = Depends(get_current_user_mock)):
    """
    Retorna o perfil completo do jogador atualmente autenticado.
    """
    return current_user

@router.put("/me", response_model=schemas.Jogador)
def atualizar_jogador_atual(
    update_data: schemas.JogadorUpdate,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Permite que o usuário logado atualize seu próprio perfil.
    """
    print(f"Usuário '{current_user.email}' está atualizando o perfil com os dados: {update_data.dict(exclude_unset=True)}")
    
    # 1. Obter os dados de atualização enviados pelo usuário
    update_dict = update_data.dict(exclude_unset=True)
    
    # 2. Atualizar o objeto do usuário com os novos dados
    #    (aqui estamos apenas atualizando o objeto mockado)
    for key, value in update_dict.items():
        setattr(current_user, key, value)
        
    # 3. Salvar as alterações no banco de dados
    # db.update_user(user_id=current_user.id, update_data=update_dict)
    
    return current_user

@router.get("/{jogador_id}", response_model=schemas.JogadorPublico)
def ler_jogador_por_id(jogador_id: UUID):
    """
    Busca e retorna o perfil público de um jogador específico pelo seu ID.
    """
    print(f"Buscando perfil público do jogador com ID: {jogador_id}")
    
    # 1. Buscar o jogador no banco de dados pelo ID
    # jogador_db = db.get_user(id=jogador_id)
    # if not jogador_db:
    #     raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    # Retornando dados mockados
    return schemas.JogadorPublico(id=jogador_id, nome="Jogador Encontrado por ID")

@router.post("/me/change-password", response_model=schemas.StatusResponse)
def change_current_user_password(
    password_data: schemas.ChangePasswordRequest, 
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Permite que o usuário autenticado altere sua própria senha.
    """
    print(f"Usuário '{current_user.email}' tentando alterar a senha.")
    
    # 1. Buscar a senha atual (hashed) do usuário no banco de dados
    senha_hashed_do_db = "hashed_senha123" # Placeholder
    
    # 2. Verificar se a "senha_atual" fornecida bate com a do banco
    if not verify_password(password_data.senha_atual, senha_hashed_do_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta."
        )
        
    # 3. Hashear a nova senha e salvar no banco
    nova_senha_hashed = get_password_hash(password_data.nova_senha)
    # db.update_user_password(user_id=current_user.id, new_password=nova_senha_hashed)
    
    print(f"Senha do usuário '{current_user.email}' alterada com sucesso.")
    return {"mensagem": "Sua senha foi alterada com sucesso."}