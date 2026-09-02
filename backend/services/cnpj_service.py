import httpx
from fastapi import HTTPException
from backend.utils.cnpj_validator import clean_cnpj

BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

async def fetch_cnpj_data(cnpj: str) -> dict:
    # Garante que o valor utilizado na URL e no retorno seja apenas numérico (ex: 49574772000126)
    clean_num = clean_cnpj(cnpj)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BRASIL_API_URL.format(cnpj=clean_num), timeout=10.0)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="CNPJ não encontrado na base de dados.")
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Limite de requisições atingido. Tente novamente mais tarde.")
            elif response.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro ao comunicar com o serviço de consulta.")
                
            data = response.json()
            
            return {
                # AQUI: Retorna sempre o CNPJ apenas com os 14 dígitos numéricos
                "cnpj": clean_num,
                "razao_social": data.get("razao_social") or "Não informado",
                "nome_fantasia": data.get("nome_fantasia") or "Não informado",
                "situacao": data.get("descricao_situacao_cadastral") or "Não informado",
                "data_abertura": data.get("data_inicio_atividade") or "Não informado",
                "inscricao_estadual": "Não informado",
                "natureza_juridica": data.get("natureza_juridica") or "Não informado",
                "porte": data.get("porte") or "Não informado",
                "endereco": f"{data.get('logradouro', '')}, {data.get('numero', '')} {data.get('complemento', '')}".strip() or "Não informado",
                "municipio": data.get("municipio") or "Não informado",
                "estado": data.get("uf") or "Não informado",
                "cep": data.get("cep") or "Não informado",
                "telefone": data.get("ddd_telefone_1") or "Não informado",
                "email": data.get("email") or "Não informado"
            }
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Serviço de consulta indisponível no momento.")