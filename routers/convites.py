from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import uuid4

# Importa os schemas e a dependência de autenticação mockada
import schemas
from routers.jogadores import get_current_user_mock # Reutilizando nosso mock de jogador logado

# Cria o router específico para convites
router = APIRouter(
    prefix="/convites",
    tags=["Convites"]
)

# ===================================================================
#                           ENDPOINTS
# ===================================================================

@router.post("/", response_model=schemas.Convite, status_code=status.HTTP_201_CREATED)
def criar_convite(
    convite_data: schemas.ConviteCreate,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Gera um novo convite e o associa ao usuário que o criou.
    A API pode se encarregar de enviar o e-mail para o convidado.
    """
    print(f"Usuário '{current_user.email}' está convidando '{convite_data.email_convidado}'")
    
    # 1. Verificar se o e-mail convidado já pertence a um usuário cadastrado
    # user_exists = db.get_user_by_email(email=convite_data.email_convidado)
    # if user_exists:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Este e-mail já pertence a um usuário cadastrado."
    #     )
    
    # 2. Gerar um token de convite único e seguro
    token_de_convite_unico = str(uuid4())
    
    # 3. Salvar o convite no banco de dados, associado a quem convidou (current_user.id)
    # novo_convite_db = db.create_invite(
    #     email_convidado=convite_data.email_convidado,
    #     id_convidou=current_user.id,
    #     token=token_de_convite_unico
    # )
    
    # 4. (Opcional, mas recomendado) Enviar um e-mail para o convidado
    # A lógica de enviar o email com o link de cadastro contendo o token iria aqui.
    print(f"Email de convite seria enviado para {convite_data.email_convidado} com o token {token_de_convite_unico}")
    
    # Retornando um objeto mockado que corresponde ao schema de resposta
    from datetime import datetime
    convite_mockado = {
        "id": uuid4(),
        "email_convidado": convite_data.email_convidado,
        "id_convidou": current_user.id,
        "status": "pendente",
        "data_envio": datetime.now()
    }
    
    return convite_mockado

@router.get("/me", response_model=List[schemas.Convite])
def listar_meus_convites_enviados(
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Lista todos os convites que o usuário autenticado já enviou.
    """
    print(f"Buscando convites enviados por '{current_user.email}'")
    
    # 1. Buscar no banco de dados todos os convites onde 'id_convidou' == current_user.id
    # convites_db = db.get_invites_by_user(user_id=current_user.id)
    
    # Retornando uma lista mockada para demonstração
    from datetime import datetime
    lista_mockada = [
        {
            "id": uuid4(),
            "email_convidado": "amigo1@email.com",
            "id_convidou": current_user.id,
            "status": "aceito",
            "data_envio": datetime.now()
        },
        {
            "id": uuid4(),
            "email_convidado": "amigo2@email.com",
            "id_convidou": current_user.id,
            "status": "pendente",
            "data_envio": datetime.now()
        }
    ]
    
    return lista_mockada