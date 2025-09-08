import json
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Dict, Any

import streamlit as st
import pandas as pd


BASE_DIR = Path("data")
BASE_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = BASE_DIR / "controle.json"

# --- Uso de Lambda ---
agora = lambda: datetime.now().strftime("%H:%M:%S %d/%m/%Y") 

def carregar_transacoes(db: Path = DB_FILE) -> List[Dict[str, Any]]:
    """Lê o banco JSON e retorna a lista de transações."""
    if db.exists():
        try:
            return json.loads(db.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []

def salvar_transacoes(transacoes: List[Dict[str, Any]], db: Path = DB_FILE) -> None:
    """Salva as transações no arquivo JSON."""
    db.write_text(json.dumps(transacoes, ensure_ascii=False, indent=2), encoding="utf-8")

# --- Uso do Closure ---
def gerar_id(transacoes: List[Dict[str, Any]]) -> Callable[[], int]:
    atual = max((t.get("id", 0) for t in transacoes), default=0)
    def proximo() -> int:
        nonlocal atual
        atual += 1
        return atual
    return proximo

# --- Função de Alta Ordem + List Comprehension ---
def selecionar(transacoes: List[Dict[str, Any]], criterio: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
    return [t for t in transacoes if criterio(t)]

def calcular_saldo(transacoes: List[Dict[str, Any]]) -> float:
    return sum(t["valor"] if t["tipo"] == "receita" else -t["valor"] for t in transacoes)

def ordenar(transacoes: List[Dict[str, Any]], campo: str, desc: bool) -> List[Dict[str, Any]]:
    def chave(t: Dict[str, Any]):
        v = t.get(campo, "")
        if campo in ("valor", "id"):
            try:
                return float(v)
            except Exception:
                return 0.0
        return v
    return sorted(transacoes, key=lambda t: chave(t), reverse=desc)

def garantir_existencia(id_transacao: int, transacoes: List[Dict[str, Any]]) -> Dict[str, Any]:
    for t in transacoes:
        if t["id"] == id_transacao:
            return t
    raise ValueError(f"Transação {id_transacao} não encontrada.")

def adicionar_transacao(tipo: str, valor: float, descricao: str, categoria: str) -> Dict[str, Any]:
    transacoes = carregar_transacoes()
    prox_id = gerar_id(transacoes)
    nova = {
        "id": prox_id(),
        "tipo": tipo.lower(),
        "valor": float(valor),
        "descricao": descricao.strip(),
        "categoria": categoria.strip(),
        "created_at": agora(),
    }
    salvar_transacoes(transacoes + [nova])
    return nova

def editar_transacao(id_transacao: int, descricao: str | None, categoria: str | None, valor: float | None) -> bool:
    transacoes = carregar_transacoes()
    try:
        t = garantir_existencia(id_transacao, transacoes)
        if descricao and descricao.strip():
            t["descricao"] = descricao.strip()
        if categoria and categoria.strip():
            t["categoria"] = categoria.strip()
        if valor is not None and valor > 0:
            t["valor"] = float(valor)
        salvar_transacoes(transacoes)
        return True
    except ValueError:
        return False

def excluir_transacao(id_transacao: int) -> bool:
    transacoes = carregar_transacoes()
    antes = len(transacoes)
    transacoes = [t for t in transacoes if t["id"] != id_transacao]
    if len(transacoes) == antes:
        return False
    salvar_transacoes(transacoes)
    return True

def formatar_tabela(transacoes: List[Dict[str, Any]]) -> pd.DataFrame:
    linhas = [
        {
            "ID": t["id"],
            "Tipo": "Receita" if t["tipo"] == "receita" else "Despesa",
            "Valor": float(t["valor"]),
            "Descrição": t["descricao"],
            "Categoria": t["categoria"],
            "Data": str(t["created_at"]),
        }
        for t in transacoes
    ]
    return pd.DataFrame(linhas, columns=["ID", "Tipo", "Valor", "Descrição", "Categoria", "Data"])


# Interface com Streamlit

st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="wide")

st.title("💰 Controle Financeiro Pessoal")


transacoes = carregar_transacoes()


total_rec = sum(t["valor"] for t in transacoes if t["tipo"] == "receita")
total_desp = sum(t["valor"] for t in transacoes if t["tipo"] == "despesa")
saldo = calcular_saldo(transacoes)

c1, c2, c3 = st.columns(3)
c1.metric("Receitas", f"R${total_rec:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Despesas", f"R${total_desp:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Saldo", f"R${saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()


st.sidebar.header("🔍 Filtros e Ordenação")
tipo_filtro = st.sidebar.multiselect("Tipo", ["receita", "despesa"], format_func=lambda x: "Receita" if x=="receita" else "Despesa",
placeholder="Transação")
cat_filtro = st.sidebar.text_input("Categoria contém", "")
campo_ord = st.sidebar.selectbox("Ordenar por", ["created_at","valor","id","categoria","descricao","tipo"], index=0,
    format_func=lambda f: {"created_at":"Data","valor":"Valor","id":"ID","categoria":"Categoria","descricao":"Descrição","tipo":"Tipo"}[f])
ordem_desc = st.sidebar.toggle("Ordem decrescente", value=True)

def gerar_pred(tipo_sel: List[str], cat_txt: str) -> Callable[[Dict[str, Any]], bool]:
    cat = (cat_txt or "").lower().strip()
    def criterio(t: Dict[str, Any]) -> bool:
        return (not tipo_sel or t["tipo"] in tipo_sel) and (cat == "" or cat in t["categoria"].lower())
    return criterio

filtradas = selecionar(transacoes, gerar_pred(tipo_filtro, cat_filtro))
ordenadas = ordenar(filtradas, campo_ord, ordem_desc)


st.subheader("➕ Nova Transação")
with st.form("form_add", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo", ["receita", "despesa"], index=1, format_func=lambda x: "Receita" if x=="receita" else "Despesa")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f")
    with col2:
        desc = st.text_input("Descrição")
        cat = st.text_input("Categoria")
    enviar = st.form_submit_button("Adicionar")
    if enviar:
        if valor <= 0:
            st.error("O valor deve ser maior que zero.")
        elif not desc.strip() or not cat.strip():
            st.error("Descrição e categoria são obrigatórias.")
        else:
            nova = adicionar_transacao(tipo, valor, desc, cat)
            st.success(f"Transação {nova['id']} adicionada.")
            st.rerun()


st.subheader("📄 Transações Registradas")
df = formatar_tabela(ordenadas)
df["Data"] = df["Data"].astype(str)
st.dataframe(df, use_container_width=True, hide_index=True)


col1, col2 = st.columns(2)
with col1:
    st.download_button("Exportar CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="transacoes.csv", mime="text/csv")
with col2:
    st.download_button("Exportar JSON", data=json.dumps(ordenadas, ensure_ascii=False, indent=2).encode("utf-8"),
                       file_name="transacoes.json", mime="application/json")


st.subheader("✏️ Editar / Excluir")
ids = [t["id"] for t in ordenadas]

if not ids:
    st.info("Nenhuma transação encontrada.")
else:
    col_sel, col_edit = st.columns([1, 3])
    with col_sel:
        id_sel = st.selectbox("ID", ids)
        tx_sel = next((t for t in transacoes if t["id"] == id_sel), None)

    with col_edit:
        with st.form("form_edit"):
            novo_desc = st.text_input("Descrição", value=tx_sel["descricao"] if tx_sel else "")
            novo_cat = st.text_input("Categoria", value=tx_sel["categoria"] if tx_sel else "")
            novo_valor = st.number_input(
                "Novo Valor (R$)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                value=float(tx_sel["valor"]) if tx_sel else 0.0
            )

            b1, b2 = st.columns(2)

            with b1:
                ok = st.form_submit_button("💾 Salvar alterações")
            with b2:
                excluir = st.form_submit_button("🗑️ Excluir")

            if ok:
                if editar_transacao(id_sel, novo_desc, novo_cat, novo_valor):
                    st.success(f"Transação {id_sel} atualizada.")
                    st.rerun()
                else:
                    st.error("Falha ao atualizar.")

            if excluir:
                if excluir_transacao(id_sel):
                    st.success(f"Transação {id_sel} excluída.")
                    st.rerun()
                else:
                    st.error("Erro ao excluir.")



