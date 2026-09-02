import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.utils.cnpj_validator import clean_cnpj, validate_cnpj
from backend.services.cnpj_service import fetch_cnpj_data

app = FastAPI(
    title="API de Consulta de CNPJ",
    description="Backend para validação e consulta de dados cadastrais de empresas brasileiras.",
    version="1.0.0"
)

# Habilita suporte a CORS para chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/cnpj/{raw_cnpj}")
async def get_cnpj_info(raw_cnpj: str):
    """
    Endpoint principal para consulta de CNPJ:
    1. Limpa os caracteres do parâmetro recebido
    2. Valida o formato e os dígitos verificadores
    3. Realiza a busca no serviço externo
    4. Retorna o JSON estruturado
    """
    cleaned_cnpj = clean_cnpj(raw_cnpj)

    if not cleaned_cnpj:
        raise HTTPException(
            status_code=400, 
            detail="O parâmetro CNPJ não pode ser vazio."
        )

    if len(cleaned_cnpj) != 14:
        raise HTTPException(
            status_code=400, 
            detail=f"CNPJ deve possuir exatamente 14 dígitos numéricos. (Enviado: {len(cleaned_cnpj)} dígitos)"
        )

    if not validate_cnpj(cleaned_cnpj):
        raise HTTPException(
            status_code=400, 
            detail="CNPJ inválido. Verifique os números informados."
        )

    # Realiza a consulta na API externa
    return await fetch_cnpj_data(cleaned_cnpj)


# Servir arquivos estáticos do frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))