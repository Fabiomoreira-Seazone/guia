"""Valida os dados do guia. Uso: python3 tools/validar.py  (sai com código 1 se houver erro)."""
import json
import re
import sys
from pathlib import Path

IDIOMAS = ("pt", "es", "en")
PROIBIDO = re.compile(r"senha|password|contraseña|wi-?fi", re.I)
MAPS = ("https://www.google.com/maps/", "https://maps.app.goo.gl/")
# Única chave da UI autorizada a falar de senha ("a senha é enviada pelo WhatsApp").
UI_LIBERADA = {"aviso_senha"}
TEXTOS = {"titulo", "descricao", "nome_traduzido", "como_chegar", "estacionamento"}


def _texto(v, onde, erros):
    if not isinstance(v, dict):
        erros.append(f"{onde}: deveria ser {{pt,es,en}}")
        return
    for lang in IDIOMAS:
        if not str(v.get(lang, "")).strip():
            erros.append(f'{onde}: falta o idioma "{lang}"')


def _maps(v, onde, erros):
    if not isinstance(v, str) or not v.startswith(MAPS):
        erros.append(f"{onde}: maps_url inválido ({v!r})")


def _sem_senha(v, onde, erros):
    if isinstance(v, dict):
        for k, x in v.items():
            if PROIBIDO.search(k):
                erros.append(f"{onde}.{k}: chave proibida (senha/wifi não vai na página)")
            _sem_senha(x, f"{onde}.{k}", erros)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            _sem_senha(x, f"{onde}[{i}]", erros)
    elif isinstance(v, str) and PROIBIDO.search(v):
        erros.append(f"{onde}: texto menciona senha/wifi ({v[:40]!r})")


def validar(dados):
    erros = []
    ui = dict(dados.get("ui", {}))
    for k, v in ui.items():
        _texto(v, f"ui.{k}", erros)
    _sem_senha({k: v for k, v in ui.items() if k not in UI_LIBERADA}, "ui", erros)
    for nome in ("guia", "eventos", "imoveis"):
        _sem_senha(dados.get(nome, {}), nome, erros)

    for c in dados.get("guia", {}).get("categorias", []):
        _texto(c.get("titulo"), f"guia.{c.get('id')}.titulo", erros)
        for it in c.get("itens", []):
            onde = f"guia.{c.get('id')}.{it.get('id')}"
            if not it.get("nome"):
                erros.append(f"{onde}: falta nome")
            _texto(it.get("descricao"), f"{onde}.descricao", erros)
            _maps(it.get("maps_url"), onde, erros)

    for i, e in enumerate(dados.get("eventos", {}).get("eventos", [])):
        onde = f"eventos[{i}]"
        _texto(e.get("nome"), f"{onde}.nome", erros)
        _texto(e.get("descricao"), f"{onde}.descricao", erros)
        _maps(e.get("maps_url"), onde, erros)
        ini, fim = e.get("data_inicio", ""), e.get("data_fim", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ini) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fim):
            erros.append(f"{onde}: datas devem ser YYYY-MM-DD")
        elif fim < ini:
            erros.append(f"{onde}: data_fim antes de data_inicio")

    for im in dados.get("imoveis", {}).get("imoveis", []):
        onde = f"imoveis.{im.get('codigo')}"
        if not re.fullmatch(r"[A-Z0-9]+", str(im.get("codigo", ""))):
            erros.append(f"{onde}: código inválido")
        _maps(im.get("maps_url"), onde, erros)
        for campo in ("como_chegar", "estacionamento"):
            _texto(im.get(campo), f"{onde}.{campo}", erros)
        for j, r in enumerate(im.get("regras", [])):
            _texto(r, f"{onde}.regras[{j}]", erros)
    return erros


def main():
    site = Path(__file__).resolve().parent.parent / "site"
    dados = {n: json.loads((site / "data" / f"{n}.json").read_text("utf-8"))
             for n in ("guia", "eventos", "imoveis", "ui")}
    erros = validar(dados)
    for im in dados["imoveis"].get("imoveis", []):
        if not (site / im["codigo"] / "index.html").exists():
            erros.append(f"falta a página site/{im['codigo']}/index.html")
    for e in erros:
        print("ERRO:", e)
    print("OK" if not erros else f"{len(erros)} erro(s)")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
