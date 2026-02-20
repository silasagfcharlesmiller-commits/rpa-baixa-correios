from supabase import create_client
from src.config.settings import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_supabase():
    response = supabase.table("RASTREIO").select("*").execute()
    return response.data

def excluir_supabase(codigo):
    supabase.table("RASTREIO").delete().eq("codigo_rastreio", codigo).execute()         