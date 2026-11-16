"""Valida os dados do guia. Uso: python3 tools/validar.py  (sai com código 1 se houver erro)."""
import json
import re
import sys
from pathlib import Path

IDIOMAS = ("pt", "es", "en")
# "Wi-Fi grátis" (rede pública do térreo) é liberado; qualquer outra menção a Wi-Fi continua bloqueada.
PROIBIDO = re.compile(r"senha|password|contraseña|(?<!free )wi-?fi(?!\s+(grátis|gratis|gratuit[oa]))", re.I)
MAPS = ("https://www.google.com/maps/", "https://maps.app.goo.gl/")
# Única chave da UI autorizada a falar de senha ("a senha é enviada pelo WhatsApp").
UI_LIBERADA = {"aviso_senha", "aviso_senha_facial"}
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


def _foto(f, onde, erros):
    if not re.fullmatch(r"img/[\w.-]+\.(jpg|jpeg|png|webp)", str(f.get("src", ""))):
        erros.append(f"{onde}: src deve ser img/<arquivo> ({f.get('src')!r})")
    _texto(f.get("alt"), f"{onde}.alt", erros)


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
    for nome in ("guia", "eventos", "imoveis", "predios"):
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

    predios = {p.get("id"): p for p in dados.get("predios", {}).get("predios", [])}
    for im in dados.get("imoveis", {}).get("imoveis", []):
        onde = f"imoveis.{im.get('codigo')}"
        if not re.fullmatch(r"[A-Z0-9]+", str(im.get("codigo", ""))):
            erros.append(f"{onde}: código inválido")
        base = {}
        if "predio" in im:
            if im["predio"] not in predios:
                erros.append(f"{onde}: prédio {im['predio']!r} não existe em predios.json")
            base = predios.get(im["predio"], {})
        ef = dict(base, **im)  # o imóvel sobrescreve o prédio
        if not ef.get("nome"):
            erros.append(f"{onde}: falta nome")
        _maps(ef.get("maps_url"), onde, erros)
        for campo in ("como_chegar", "estacionamento"):
            _texto(ef.get(campo), f"{onde}.{campo}", erros)
        for campo in ("acesso", "lixo", "apartamento", "vaga", "malas"):
            if campo in ef:
                _texto(ef[campo], f"{onde}.{campo}", erros)
        if "areas_comuns" in ef:
            if not isinstance(ef["areas_comuns"], list):
                erros.append(f"{onde}.areas_comuns: deveria ser uma lista de itens {{nome, texto, foto?}}")
            else:
                for j, a in enumerate(ef["areas_comuns"]):
                    _texto(a.get("nome"), f"{onde}.areas_comuns[{j}].nome", erros)
                    _texto(a.get("texto"), f"{onde}.areas_comuns[{j}].texto", erros)
                    if "foto" in a:
                        _foto(a["foto"], f"{onde}.areas_comuns[{j}].foto", erros)
        if "estacionamento_foto" in ef:
            _foto(ef["estacionamento_foto"], f"{onde}.estacionamento_foto", erros)
        for j, f in enumerate(ef.get("galeria", [])):
            _foto(f, f"{onde}.galeria[{j}]", erros)
        if "estacionamento_maps_url" in ef:
            _maps(ef["estacionamento_maps_url"], f"{onde}.estacionamento", erros)
        for j, r in enumerate(im.get("regras", [])):
            _texto(r, f"{onde}.regras[{j}]", erros)
    return erros


def main():
    site = Path(__file__).resolve().parent.parent / "site"
    dados = {n: json.loads((site / "data" / f"{n}.json").read_text("utf-8"))
             for n in ("guia", "eventos", "imoveis", "ui", "predios")}
    erros = validar(dados)
    for im in dados["imoveis"].get("imoveis", []):
        if not (site / im["codigo"] / "index.html").exists():
            erros.append(f"falta a página site/{im['codigo']}/index.html")
    for p in dados["predios"].get("predios", []) + dados["imoveis"].get("imoveis", []):
        areas = p.get("areas_comuns") if isinstance(p.get("areas_comuns"), list) else []
        fotos = [p.get("estacionamento_foto") or {}] + p.get("galeria", []) + [a.get("foto") or {} for a in areas]
        for src in filter(None, (f.get("src") for f in fotos)):
            if not (site / src).exists():
                erros.append(f"falta o arquivo de foto site/{src}")
    for e in erros:
        print("ERRO:", e)
    print("OK" if not erros else f"{len(erros)} erro(s)")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
