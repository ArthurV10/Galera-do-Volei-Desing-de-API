from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date

import schemas
from routers.jogadores import get_current_user_mock

router = APIRouter(
    prefix="/partidas",
    tags=["Partida e Inscrições"]
)

# ===================================================================
#           BANCO DE DADOS FALSO (MOCK)
# ===================================================================
# Para este esqueleto, vamos simular nosso banco de dados com uma lista
mock_db_partidas = []
mock_db_inscricoes = []

# Criando alguns dados iniciais para teste
organizador_id_mock = uuid4()
partida_id_mock = uuid4()

mock_db_partidas.append(
    schemas.Partida(
        id=partida_id_mock,
        titulo="Vôlei de Segunda em Teresina",
        id_local=uuid4(),
        data_hora=datetime(2025, 9, 15, 19, 0, 0),
        duracao_estimada_min=90,
        tipo="Mista",
        categoria="Amador",
        max_jogadores=18,
        custo_por_jogador=10.0,
        descricao="Jogo amistoso, nível intermediário.",
        id_organizador=organizador_id_mock,
        status="AbertaParaAdesao",
        jogadores_confirmados_count=5
    )
)

# ===================================================================
#                     ENDPOINTS DE PARTIDA
# ===================================================================

@router.post("/", response_model=schemas.Partida, status_code=status.HTTP_201_CREATED)
def criar_partida(
    partida_data: schemas.PartidaCreate,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Cria uma nova partida na plataforma. O usuário logado é definido como o organizador.
    """
    print(f"Usuário '{current_user.email}' está criando a partida '{partida_data.titulo}'")
    
    nova_partida = schemas.Partida(
        id=uuid4(),
        id_organizador=current_user.id,
        **partida_data.dict()
    )
    
    # Lógica de DB: Salvar a nova_partida no banco de dados
    mock_db_partidas.append(nova_partida)
    
    return nova_partida

@router.get("/", response_model=List[schemas.Partida])
def listar_partidas(cidade: Optional[str] = None, data: Optional[date] = None):
    """
    Lista as partidas disponíveis, com suporte a filtros.
    Em um app real, os filtros seriam feitos na query do banco de dados.
    """
    # Lógica de DB: Buscar partidas no banco, aplicando os filtros
    print("Listando todas as partidas disponíveis...")
    return mock_db_partidas

@router.get("/{partida_id}", response_model=schemas.Partida)
def ler_partida(partida_id: UUID):
    """
    Obtém todos os detalhes de uma partida específica.
    """
    # Lógica de DB: Buscar a partida pelo ID
    for partida in mock_db_partidas:
        if partida.id == partida_id:
            return partida
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida não encontrada")

@router.put("/{partida_id}", response_model=schemas.Partida)
def atualizar_partida(
    partida_id: UUID,
    update_data: schemas.PartidaUpdate,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Atualiza os dados de uma partida. Ação restrita ao organizador.
    """
    partida_existente = None
    for p in mock_db_partidas:
        if p.id == partida_id:
            partida_existente = p
            break
            
    if not partida_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida não encontrada")

    # REGRA DE NEGÓCIO: Apenas o organizador pode editar
    if partida_existente.id_organizador != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o organizador pode editar a partida")

    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(partida_existente, key, value)
        
    return partida_existente


# ===================================================================
#                   ENDPOINTS DE INSCRIÇÃO
# ===================================================================

@router.post("/{partida_id}/inscricoes", response_model=schemas.Inscricao, status_code=status.HTTP_202_ACCEPTED)
def solicitar_inscricao(
    partida_id: UUID,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Um jogador solicita a entrada em uma partida ("Puxar Partida").
    """
    # Lógica para verificar se a partida existe, se não está lotada, etc.
    partida = ler_partida(partida_id) # Reutiliza a função que já busca a partida
    if partida.status != "AbertaParaAdesao":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta partida não está aceitando inscrições.")

    nova_inscricao = schemas.Inscricao(
        id=uuid4(),
        id_partida=partida_id,
        id_jogador=current_user.id,
        status="Pendente"
    )
    mock_db_inscricoes.append(nova_inscricao)
    return nova_inscricao

@router.get("/{partida_id}/inscricoes", response_model=List[schemas.Inscricao])
def listar_inscricoes(
    partida_id: UUID,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Lista as solicitações de inscrição para uma partida. Ação restrita ao organizador.
    """
    partida = ler_partida(partida_id)
    if partida.id_organizador != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o organizador pode ver a lista de inscrições.")

    inscricoes_da_partida = [insc for insc in mock_db_inscricoes if insc.id_partida == partida_id]
    return inscricoes_da_partida

@router.put("/{partida_id}/inscricoes/{inscricao_id}", response_model=schemas.Inscricao)
def gerenciar_inscricao(
    partida_id: UUID,
    inscricao_id: UUID,
    update_data: schemas.InscricaoUpdate,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    O organizador aprova ou rejeita uma solicitação de inscrição.
    """
    partida = ler_partida(partida_id)
    if partida.id_organizador != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o organizador pode gerenciar inscrições.")

    for insc in mock_db_inscricoes:
        if insc.id == inscricao_id and insc.id_partida == partida_id:
            insc.status = update_data.status
            # Lógica de negócio: Se aprovado, incrementar o contador na partida
            if update_data.status == "Confirmada":
                partida.jogadores_confirmados_count += 1
            return insc
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada")

@router.delete("/{partida_id}/inscricoes/me", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_inscricao(
    partida_id: UUID,
    current_user: schemas.Jogador = Depends(get_current_user_mock)
):
    """
    Um jogador que já foi aceito desiste da partida.
    """
    inscricao_para_remover = None
    for insc in mock_db_inscricoes:
        if insc.id_partida == partida_id and insc.id_jogador == current_user.id:
            inscricao_para_remover = insc
            break

    if not inscricao_para_remover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Você não possui inscrição nesta partida.")

    mock_db_inscricoes.remove(inscricao_para_remover)
    # Lógica de negócio: Decrementar o contador na partida
    partida = ler_partida(partida_id)
    if partida.jogadores_confirmados_count > 0:
        partida.jogadores_confirmados_count -= 1
        
    return