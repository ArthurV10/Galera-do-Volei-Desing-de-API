# Em routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
import schemas

# --- BIBLIOTECAS PARA UMA IMPLEMENTAÇÃO REAL ---
# - Hashing de senhas: passlib
# - Geração/validação de Tokens JWT: python-jose

# --- CONSTANTES ---
# Define o tempo de expiração do token de acesso
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cria o router específico para autenticação
router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


# ===================================================================
#           LÓGICA DE AUTENTICAÇÃO (ESQUELETO)
# ===================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha em texto plano com a senha 'hasheada' do banco."""
    print("Verificando senha...")
    # Lógica real usaria: return pwd_context.verify(plain_password, hashed_password)
    return plain_password == hashed_password

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Cria um token JWT."""
    print(f"Criando token para: {data}")
    return f"fake-jwt-token-for-{data.get('sub')}"

# ===================================================================
#                           ENDPOINTS
# ===================================================================

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(login_request: schemas.LoginRequest):
    """
    Endpoint de Login. Recebe email e senha, retorna um Token JWT.
    """
    print(f"Tentativa de login para o email: {login_request.email}")
    
    # Se o usuário não existe OU a senha está incorreta, retorna erro
    if login_request.email != "arthur@email.com" or not verify_password(login_request.senha, "senha123"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Se a autenticação for bem-sucedida, criar o token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_request.email}, expires_delta=access_token_expires
    )

    # Retornar o token
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=schemas.StatusResponse)
def forgot_password(request: schemas.ForgotPasswordRequest):
    """
    Endpoint para iniciar a recuperação de senha.
    """
    print(f"Solicitação de recuperação de senha para: {request.email}")
    
    return {"mensagem": "Se um usuário com este e-mail estiver cadastrado, um link para recuperação de senha foi enviado."}


@router.post("/reset-password", response_model=schemas.StatusResponse)
def reset_password(request: schemas.ResetPasswordRequest):
    """
    Endpoint para finalizar a recuperação de senha com o token recebido.
    """
    print(f"Tentativa de resetar senha com o token: {request.token}")

    if request.token != "token_valido_recebido_por_email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado."
        )
    
    return {"mensagem": "Senha alterada com sucesso."}