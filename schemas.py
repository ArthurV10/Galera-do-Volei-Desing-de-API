# Em schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

# ==================
#      JOGADOR
# ==================

# Schema base com os campos em comum
class JogadorBase(BaseModel):
    nome: str
    email: EmailStr
    sexo: str
    data_nascimento: date

# Schema para a criação de um jogador (recebido pela API)
class JogadorCreate(JogadorBase):
    senha: str = Field(..., min_length=8)
    token_convite: str

# Schema para a atualização de um jogador (todos os campos são opcionais)
class JogadorUpdate(BaseModel):
    nome: Optional[str] = None
    nivel_habilidade: Optional[str] = None
    posicoes_preferidas: Optional[List[str]] = None

# Schema para representar um jogador em respostas da API (enviado pela API)
class Jogador(JogadorBase):
    id: UUID
    nivel_habilidade: str = "Iniciante"
    posicoes_preferidas: List[str] = []

    class Config:
        orm_mode = True

# Schema simplificado para ser usado dentro de outras respostas (ex: em Avaliação)
class JogadorPublico(BaseModel):
    id: UUID
    nome: str

    class Config:
        orm_mode = True

# ==================
#      PARTIDA
# ==================

class PartidaBase(BaseModel):
    titulo: str
    id_local: UUID
    data_hora: datetime
    duracao_estimada_min: int
    tipo: str
    categoria: str
    max_jogadores: int
    custo_por_jogador: float
    descricao: Optional[str] = None

class PartidaCreate(PartidaBase):
    pass

class PartidaUpdate(BaseModel):
    titulo: Optional[str] = None
    id_local: Optional[UUID] = None
    data_hora: Optional[datetime] = None
    duracao_estimada_min: Optional[int] = None
    max_jogadores: Optional[int] = None
    custo_por_jogador: Optional[float] = None
    descricao: Optional[str] = None
    status: Optional[str] = None

class Partida(PartidaBase):
    id: UUID
    id_organizador: UUID
    status: str
    jogadores_confirmados_count: int

    class Config:
        orm_mode = True

# ==================
#    INSCRIÇÃO
# ==================

class Inscricao(BaseModel):
    id: UUID
    id_partida: UUID
    id_jogador: UUID
    status: str

    class Config:
        orm_mode = True

class InscricaoUpdate(BaseModel):
    status: str # Ex: "Confirmada" ou "Rejeitada"

# ==================
#     AVALIAÇÃO
# ==================

class AvaliacaoBase(BaseModel):
    id_partida: UUID
    alvo_tipo: str
    id_alvo: UUID
    nota_organizacao: Optional[int] = Field(None, ge=1, le=5)
    nota_pontualidade: Optional[int] = Field(None, ge=1, le=5)
    nota_fair_play: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None

class AvaliacaoCreate(AvaliacaoBase):
    pass

class Avaliacao(AvaliacaoBase):
    id: UUID
    id_avaliador: UUID
    data_avaliacao: datetime
    # Retorna o perfil público de quem avaliou, (Lembrar que é útil no front-end   >:D)
    avaliador: JogadorPublico

    class Config:
        orm_mode = True

# ==================
#       LOCAL
# ==================

class LocalBase(BaseModel):
    nome: str
    endereco: Optional[str] = None
    cidade: str
    estado: str
    tipo_quadra: Optional[str] = None

class LocalCreate(LocalBase):
    pass

class Local(LocalBase):
    id: UUID

    class Config:
        orm_mode = True

# ==================
#      CONVITE
# ==================

class ConviteCreate(BaseModel):
    email_convidado: EmailStr

class Convite(ConviteCreate):
    id: UUID
    id_convidou: UUID
    status: str
    data_envio: datetime

    class Config:
        orm_mode = True

# ==================
#    AUTENTICAÇÃO
# ==================

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=8)

# ==================
#  RESPOSTA GENÉRICA
# ==================

class StatusResponse(BaseModel):
    mensagem: str