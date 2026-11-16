import copy
import unittest

from validar import validar

T = {"pt": "a", "es": "a", "en": "a"}
OK = {
    "guia": {"categorias": [{"id": "pontos", "titulo": T, "itens": [
        {"id": "mercado", "nome": "Mercado Público", "descricao": T, "endereco": "Rua X",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=Mercado"}]}]},
    "eventos": {"atualizado_em": "2026-11-16", "eventos": [
        {"nome": T, "data_inicio": "2026-11-20", "data_fim": "2026-11-21", "horario": "20h",
         "local": "Teatro", "maps_url": "https://maps.app.goo.gl/abc", "descricao": T}]},
    "imoveis": {"imoveis": [
        {"codigo": "TVT303", "nome": "Apto", "endereco": "Rua Y",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=Y",
         "checkin": "15h", "checkout": "11h", "como_chegar": T, "estacionamento": T,
         "regras": [T], "contato_whatsapp": "5548999999999"}]},
    "ui": {"titulo": T},
}


class TestValidar(unittest.TestCase):
    def d(self):
        return copy.deepcopy(OK)

    def test_aceita_dados_minimos_validos(self):
        self.assertEqual(validar(self.d()), [])

    def test_rejeita_texto_sem_idioma(self):
        d = self.d()
        del d["guia"]["categorias"][0]["itens"][0]["descricao"]["en"]
        erros = validar(d)
        self.assertTrue(any('"en"' in e for e in erros), erros)

    def test_rejeita_maps_url_invalido(self):
        d = self.d()
        d["guia"]["categorias"][0]["itens"][0]["maps_url"] = "http://x.com"
        self.assertTrue(validar(d))

    def test_rejeita_senha_nos_dados(self):
        d = self.d()
        d["imoveis"]["imoveis"][0]["regras"] = [{"pt": "Senha da porta 1234", "es": "x", "en": "x"}]
        self.assertTrue(any("senha" in e.lower() for e in validar(d)))

    def test_rejeita_chave_wifi(self):
        d = self.d()
        d["imoveis"]["imoveis"][0]["wifi"] = "rede123"
        self.assertTrue(validar(d))

    def test_rejeita_evento_com_fim_antes_do_inicio(self):
        d = self.d()
        d["eventos"]["eventos"][0]["data_fim"] = "2026-11-19"
        self.assertTrue(validar(d))


if __name__ == "__main__":
    unittest.main()
