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

    def com_predio(self):
        d = self.d()
        d["predios"] = {"predios": [{"id": "tvt", "nome": "Top Vision Tower", "endereco": "Rua Y",
            "maps_url": "https://www.google.com/maps/search/?api=1&query=Y",
            "como_chegar": T, "acesso": T, "estacionamento": T,
            "estacionamento_maps_url": "https://www.google.com/maps/search/?api=1&query=Z"}]}
        im = d["imoveis"]["imoveis"][0]
        for k in ("nome", "endereco", "maps_url", "como_chegar", "estacionamento"):
            del im[k]
        im["predio"] = "tvt"
        return d

    def test_aceita_imovel_que_herda_do_predio(self):
        self.assertEqual(validar(self.com_predio()), [])

    def test_rejeita_predio_inexistente(self):
        d = self.com_predio()
        d["imoveis"]["imoveis"][0]["predio"] = "xxx"
        self.assertTrue(any("xxx" in e for e in validar(d)))

    def test_rejeita_texto_do_predio_sem_idioma(self):
        d = self.com_predio()
        del d["predios"]["predios"][0]["acesso"]["es"]
        self.assertTrue(any('"es"' in e for e in validar(d)))

    def test_rejeita_lixo_sem_idioma(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["lixo"] = {"pt": "G1", "es": "G1"}
        self.assertTrue(any('"en"' in e for e in validar(d)))

    def foto(self):
        return {"src": "img/tvt-garagem.jpg", "alt": T, "credito": "Google Street View"}

    def test_aceita_foto_da_garagem(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["estacionamento_foto"] = self.foto()
        self.assertEqual(validar(d), [])

    def test_rejeita_foto_sem_texto_alternativo(self):
        d = self.com_predio()
        f = self.foto(); f["alt"] = {"pt": "portão"}
        d["predios"]["predios"][0]["estacionamento_foto"] = f
        self.assertTrue(any("alt" in e for e in validar(d)))

    def test_rejeita_foto_fora_da_pasta_img(self):
        d = self.com_predio()
        f = self.foto(); f["src"] = "https://x.com/a.jpg"
        d["predios"]["predios"][0]["estacionamento_foto"] = f
        self.assertTrue(validar(d))

    def area(self):
        return {"nome": T, "texto": T, "foto": {"src": "img/tvt-piscina.jpg", "alt": T}}

    def test_aceita_areas_comuns_em_lista(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["areas_comuns"] = [self.area(), {"nome": T, "texto": T}]
        self.assertEqual(validar(d), [])

    def test_rejeita_areas_comuns_sem_idioma(self):
        d = self.com_predio()
        a = self.area(); a["texto"] = {"pt": "Piscina 8h–22h", "es": "Piscina 8h–22h"}
        d["predios"]["predios"][0]["areas_comuns"] = [a]
        self.assertTrue(any("areas_comuns" in e and '"en"' in e for e in validar(d)))

    def test_rejeita_areas_comuns_que_nao_e_lista(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["areas_comuns"] = T
        self.assertTrue(any("areas_comuns" in e for e in validar(d)))

    def test_rejeita_foto_da_area_comum_sem_alt(self):
        d = self.com_predio()
        a = self.area(); a["foto"]["alt"] = {"pt": "x"}
        d["predios"]["predios"][0]["areas_comuns"] = [a]
        self.assertTrue(any("areas_comuns" in e and "alt" in e for e in validar(d)))

    def test_galeria_do_imovel_substitui_a_do_predio(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["galeria"] = [{"src": "img/a.jpg", "alt": T}]
        d["imoveis"]["imoveis"][0]["galeria"] = [{"src": "img/b.jpg", "alt": {"pt": "b"}}]
        erros = validar(d)
        self.assertTrue(any("galeria[0]" in e and '"es"' in e for e in erros), erros)

    def test_aceita_galeria(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["galeria"] = [{"src": "img/tvt-piscina.jpg", "alt": T}]
        self.assertEqual(validar(d), [])

    def test_rejeita_foto_da_galeria_sem_alt(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["galeria"] = [{"src": "img/a.jpg", "alt": {"pt": "a", "en": "a"}}]
        self.assertTrue(any("galeria" in e and '"es"' in e for e in validar(d)))

    def test_rejeita_galeria_com_link_externo(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["galeria"] = [{"src": "https://a0.muscache.com/x.jpg", "alt": T}]
        self.assertTrue(validar(d))

    def test_rejeita_maps_da_garagem_invalido(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["estacionamento_maps_url"] = "http://x"
        self.assertTrue(validar(d))

    def test_rejeita_imovel_sem_endereco_nem_predio(self):
        d = self.d()
        del d["imoveis"]["imoveis"][0]["maps_url"]
        self.assertTrue(validar(d))

    def test_rejeita_senha_no_predio(self):
        d = self.com_predio()
        d["predios"]["predios"][0]["acesso"] = {"pt": "senha 1234", "es": "x", "en": "x"}
        self.assertTrue(validar(d))

    def test_rejeita_evento_com_fim_antes_do_inicio(self):
        d = self.d()
        d["eventos"]["eventos"][0]["data_fim"] = "2026-11-19"
        self.assertTrue(validar(d))


if __name__ == "__main__":
    unittest.main()
