from datetime import datetime
import httpx
from fastapi import HTTPException
from backend.utils.cnpj_validator import clean_cnpj

BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

def format_date_and_calculate_age(date_str: str) -> tuple[str, str]:
    """
    Converte a data de YYYY-MM-DD para DD/MM/YYYY e calcula o tempo de atividade.
    """
    if not date_str or date_str == "Não informado":
        return "Não informado", "Não informado"
    
    try:
        # A BrasilAPI retorna a data no formato YYYY-MM-DD
        opening_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        formatted_date = opening_date.strftime("%d/%m/%Y")
        
        # Cálculo do tempo de atividade (anos e meses)
        today = datetime.now().date()
        years = today.year - opening_date.year
        months = today.month - opening_date.month
        
        if months < 0:
            years -= 1
            months += 12
            
        if years > 0 and months > 0:
            age_str = f"{years} anos e {months} meses"
        elif years > 0:
            age_str = f"{years} anos"
        elif months > 0:
            age_str = f"{months} meses"
        else:
            age_str = "Menos de 1 mês"
            
        return formatted_date, age_str
    except ValueError:
        return date_str, "Não informado"

async def fetch_cnpj_data(cnpj: str) -> dict:
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
            
            # Formatação de data e tempo de atividade
            raw_date = data.get("data_inicio_atividade")
            formatted_date, tempo_atividade = format_date_and_calculate_age(raw_date)
            
            return {
                "cnpj": clean_num,
                "razao_social": data.get("razao_social") or "Não informado",
                "nome_fantasia": data.get("nome_fantasia") or "Não informado",
                "situacao": data.get("descricao_situacao_cadastral") or "Não informado",
                "data_abertura": formatted_date,
                "tempo_atividade": tempo_atividade,
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