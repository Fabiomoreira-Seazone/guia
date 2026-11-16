/* Guia do Centro: monta a página a partir de data/*.json.
   window.BASE = caminho até a raiz do site ("./" ou "../"); window.IMOVEL = código ou undefined. */
(function () {
  "use strict";
  var IDIOMAS = ["pt", "es", "en"];

  function escolherIdioma(navLang, salvo) {
    if (IDIOMAS.indexOf(salvo) >= 0) return salvo;
    var l = String(navLang || "").toLowerCase();
    if (l.indexOf("es") === 0) return "es";
    if (l.indexOf("pt") === 0) return "pt";
    return "en";
  }

  function eventosVisiveis(eventos, hojeISO) {
    return (eventos || [])
      .filter(function (e) { return e.data_fim >= hojeISO; })
      .sort(function (a, b) { return a.data_inicio < b.data_inicio ? -1 : 1; });
  }

  function hojeLocalISO() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function lerSalvo() { try { return localStorage.getItem("guia-idioma"); } catch (e) { return null; } }
  function salvar(l) { try { localStorage.setItem("guia-idioma", l); } catch (e) { /* sem storage */ } }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function dataCurta(iso, lang) {
    var p = iso.split("-");
    var d = new Date(+p[0], +p[1] - 1, +p[2]);
    var loc = { pt: "pt-BR", es: "es-AR", en: "en-US" }[lang];
    return d.toLocaleDateString(loc, { day: "numeric", month: "short" });
  }

  function botaoMaps(url, ui, lang, rotulo) {
    return '<a class="maps" href="' + esc(url) + '" target="_blank" rel="noopener">' +
      '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>' +
      esc((rotulo || ui.abrir_maps)[lang]) + "</a>";
  }

  function htmlFoto(f, lang) {
    if (!f) return "";
    return '<figure class="foto"><img src="' + esc(srcFoto(f.src)) + '" alt="' + esc(f.alt[lang]) + '" loading="lazy">' +
      (f.credito ? "<figcaption>" + esc(f.credito) + "</figcaption>" : "") + "</figure>";
  }

  function srcFoto(src) {
    return (window.FOTOS && window.FOTOS[src]) || (window.BASE || "./") + src;
  }

  function htmlGaleria(g, ui, lang) {
    if (!g || !g.length) return "";
    var multi = g.length > 1;
    return '<div class="galeria-wrap"><div class="galeria" tabindex="0" aria-label="Fotos">' + g.map(function (f, i) {
      return '<img src="' + esc(srcFoto(f.src)) + '" alt="' + esc(f.alt[lang]) + '"' + (i ? ' loading="lazy"' : "") + ">";
    }).join("") + "</div>" +
      (multi ? '<button type="button" class="seta ant" aria-label="' + esc(ui.foto_anterior[lang]) + '" disabled>&#8249;</button>' +
        '<button type="button" class="seta prox" aria-label="' + esc(ui.proxima_foto[lang]) + '">&#8250;</button>' +
        '<div class="pontos" aria-hidden="true">' + g.map(function (_, i) { return "<span" + (i ? "" : ' class="ativo"') + "></span>"; }).join("") + "</div>" : "") +
      "</div>";
  }

  // Liga setas e pontinhos: as setas rolam uma foto por vez; os pontos seguem a rolagem (mouse, toque ou teclado).
  function ligarGaleria() {
    var wrap = document.querySelector(".galeria-wrap");
    if (!wrap) return;
    var trilho = wrap.querySelector(".galeria");
    var fotos = trilho.querySelectorAll("img");
    var ant = wrap.querySelector(".ant"), prox = wrap.querySelector(".prox");
    var pontos = wrap.querySelectorAll(".pontos span");
    if (!prox) return;
    function passo() { return fotos.length > 1 ? fotos[1].offsetLeft - fotos[0].offsetLeft : trilho.clientWidth; }
    function atual() { return Math.round(trilho.scrollLeft / passo()); }
    function atualizar() {
      var i = atual();
      var fim = trilho.scrollLeft + trilho.clientWidth >= trilho.scrollWidth - 2;
      if (fim) i = fotos.length - 1;
      Array.prototype.forEach.call(pontos, function (p, j) { p.className = j === i ? "ativo" : ""; });
      ant.disabled = trilho.scrollLeft <= 2;
      prox.disabled = fim;
    }
    function ir(d) {
      var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      trilho.scrollTo({ left: (atual() + d) * passo(), behavior: reduz ? "auto" : "smooth" });
    }
    ant.addEventListener("click", function () { ir(-1); });
    prox.addEventListener("click", function () { ir(1); });
    trilho.addEventListener("scroll", atualizar, { passive: true });
    trilho.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); ir(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); ir(-1); }
    });
    atualizar();
  }

  function htmlAreas(lista, ui, lang) {
    if (!lista || !lista.length) return "";
    return "<h3>" + esc(ui.areas_comuns[lang]) + '</h3><ul class="areas">' + lista.map(function (a) {
      return "<li>" + (a.foto ? '<img src="' + esc(srcFoto(a.foto.src)) + '" alt="' + esc(a.foto.alt[lang]) + '" loading="lazy">' : "") +
        "<div><strong>" + esc(a.nome[lang]) + "</strong><p>" + esc(a.texto[lang]) + "</p></div></li>";
    }).join("") + "</ul>";
  }

  function botaoContato(tipo, numero, titulo, desc, lang) {
    return '<a class="contato ' + tipo + '" href="https://wa.me/' + esc(numero) + '" target="_blank" rel="noopener"><strong>' +
      esc(titulo[lang]) + "</strong><span>" + esc(desc[lang]) + "</span></a>";
  }

  function htmlImovel(im, ui, lang) {
    if (!im) return '<section class="card aviso">' + esc(ui.imovel_nao_encontrado[lang]) + "</section>";
    var regras = (im.regras || []).map(function (r) { return "<li>" + esc(r[lang]) + "</li>"; }).join("");
    return '<section class="card imovel' + (im.galeria && im.galeria.length ? " com-galeria" : "") + '">' + htmlGaleria(im.galeria, ui, lang) +
      '<p class="eyebrow">' + esc(ui.seu_imovel[lang]) + "</p>" +
      "<h2>" + esc(im.nome) + "</h2>" +
      (im.apartamento ? '<p class="apto">' + esc(ui.apartamento[lang]) + " " + esc(im.apartamento[lang]) + "</p>" : "") +
      '<p class="endereco">' + esc(im.endereco) + "</p>" +
      botaoMaps(im.maps_url, ui, lang) +
      '<div class="horarios"><div><span>' + esc(ui.checkin[lang]) + "</span><strong>" + esc(ui.a_partir[lang]) + " " + esc(im.checkin) + "</strong></div>" +
      "<div><span>" + esc(ui.checkout[lang]) + "</span><strong>" + esc(ui.ate[lang]) + " " + esc(im.checkout) + "</strong></div></div>" +
      '<p class="flex">' + esc(ui.early_late[lang]) + ' <a href="https://wa.me/' + esc(ui.atendimento_numero.pt.replace(/\D/g, "")) +
        '" target="_blank" rel="noopener">' + esc(ui.atendimento_numero[lang]) + "</a></p>" +
      '<p class="nota">' + esc((im.reconhecimento_facial ? ui.aviso_senha_facial : ui.aviso_senha)[lang]) + "</p>" +
      (im.malas ? "<h3>" + esc(ui.chegou_cedo[lang]) + "</h3><p>" + esc(im.malas[lang]) + "</p>" : "") +
      (im.acesso ? "<h3>" + esc(ui.acesso[lang]) + "</h3><p>" + esc(im.acesso[lang]) + "</p>" : "") +
      htmlAreas(im.areas_comuns, ui, lang) +
      "<h3>" + esc(ui.como_chegar[lang]) + "</h3><p>" + esc(im.como_chegar[lang]) + "</p>" +
      "<h3>" + esc(ui.estacionamento[lang]) + "</h3>" + htmlFoto(im.estacionamento_foto, lang) +
      (im.vaga ? '<p class="vaga">' + esc(ui.sua_vaga[lang]) + " " + esc(im.vaga[lang]) + "</p>" : "") +
      "<p>" + esc(im.estacionamento[lang]) + "</p>" +
      (im.estacionamento_maps_url ? botaoMaps(im.estacionamento_maps_url, ui, lang, ui.garagem_maps) : "") +
      (im.lixo ? "<h3>" + esc(ui.lixo[lang]) + "</h3><p>" + esc(im.lixo[lang]) + "</p>" : "") +
      (regras ? "<h3>" + esc(ui.regras[lang]) + "</h3><ul>" + regras + "</ul>" : "") +
      "<h3>" + esc(ui.contato[lang]) + '</h3><div class="contatos">' +
      (im.contato_whatsapp ? botaoContato("anfitriao", im.contato_whatsapp, ui.contato_anfitriao, ui.contato_anfitriao_desc, lang) : "") +
      botaoContato("seazone", ui.atendimento_numero.pt.replace(/\D/g, ""), ui.contato_seazone, ui.contato_seazone_desc, lang) +
      "</div>" +
      "</section>";
  }

  function htmlEventos(ev, ui, lang) {
    var lista = eventosVisiveis(ev.eventos, hojeLocalISO());
    var corpo = lista.length ? lista.map(function (e) {
      var quando = e.data_inicio === e.data_fim ? dataCurta(e.data_inicio, lang)
        : dataCurta(e.data_inicio, lang) + " – " + dataCurta(e.data_fim, lang);
      return '<article class="item evento"><p class="quando">' + esc(quando) + (e.horario ? " · " + esc(e.horario) : "") + "</p>" +
        "<h3>" + esc(e.nome[lang]) + "</h3><p>" + esc(e.descricao[lang]) + "</p>" +
        '<p class="endereco">' + esc(e.local) + "</p>" +
        '<div class="acoes">' + botaoMaps(e.maps_url, ui, lang) +
        (e.link ? '<a class="link" href="' + esc(e.link) + '" target="_blank" rel="noopener">' + esc(ui.mais_info[lang]) + "</a>" : "") +
        "</div></article>";
    }).join("") : '<p class="vazio">' + esc(ui.sem_eventos[lang]) + "</p>";
    return '<section id="agenda"><h2>' + esc(ui.eventos[lang]) + "</h2>" + corpo +
      '<p class="atualizado">' + esc(ui.atualizado[lang]) + " " + esc(dataCurta(ev.atualizado_em, lang)) + "</p></section>";
  }

  function htmlGuia(guia, ui, lang) {
    var nav = guia.categorias.map(function (c) { return '<a href="#' + esc(c.id) + '">' + esc(c.titulo[lang]) + "</a>"; }).join("");
    return '<h2 class="secao">' + esc(ui.guia[lang]) + '</h2><nav class="atalhos"><a href="#agenda">' + esc(ui.eventos[lang]) + "</a>" + nav + "</nav>";
  }

  function render(d, lang) {
    document.documentElement.lang = { pt: "pt-BR", es: "es", en: "en" }[lang];
    Array.prototype.forEach.call(document.querySelectorAll("[data-lang]"), function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
    });
    var im = null;
    if (window.IMOVEL) {
      im = d.imoveis.imoveis.filter(function (x) { return x.codigo === window.IMOVEL; })[0] || null;
      if (im && im.predio) {
        var p = (d.predios.predios || []).filter(function (x) { return x.id === im.predio; })[0] || {};
        im = Object.assign({}, p, im); // o imóvel sobrescreve o prédio
      }
    }
    var titulo = im ? d.ui.bem_vindo[lang] + " " + im.nome : d.ui.titulo[lang];
    document.title = titulo;
    document.getElementById("titulo").textContent = titulo;
    document.getElementById("subtitulo").textContent = (im ? d.ui.subtitulo_imovel : d.ui.subtitulo)[lang];
    var guiaCats = d.guia.categorias.map(function (c) {
      return '<section id="' + esc(c.id) + '"><h2>' + esc(c.titulo[lang]) + "</h2>" +
        c.itens.map(function (it) {
          return '<article class="item"><h3>' + esc(it.nome) + "</h3><p>" + esc(it.descricao[lang]) + "</p>" +
            '<p class="endereco">' + esc(it.endereco) + "</p>" + botaoMaps(it.maps_url, d.ui, lang) + "</article>";
        }).join("") + "</section>";
    }).join("");
    document.getElementById("conteudo").innerHTML =
      (window.IMOVEL ? htmlImovel(im, d.ui, lang) : "") +
      htmlGuia(d.guia, d.ui, lang) + htmlEventos(d.eventos, d.ui, lang) + guiaCats;
    ligarGaleria();
  }

  function iniciar() {
    var base = window.BASE || "./";
    var nomes = ["ui", "guia", "eventos", "imoveis", "predios"];
    var carregar = window.DADOS ? Promise.resolve(nomes.map(function (n) { return window.DADOS[n]; }))
      : Promise.all(nomes.map(function (n) {
        return fetch(base + "data/" + n + ".json", { cache: "no-cache" }).then(function (r) { return r.json(); });
      }));
    carregar.then(function (r) {
      var d = { ui: r[0], guia: r[1], eventos: r[2], imoveis: r[3], predios: r[4] || { predios: [] } };
      var lang = escolherIdioma(navigator.language, lerSalvo());
      render(d, lang);
      Array.prototype.forEach.call(document.querySelectorAll("[data-lang]"), function (b) {
        b.addEventListener("click", function () {
          lang = b.getAttribute("data-lang");
          salvar(lang);
          render(d, lang);
        });
      });
    }).catch(function () {
      document.getElementById("conteudo").innerHTML = '<p class="vazio">Erro ao carregar / Error loading.</p>';
    });
  }

  window.Guia = { escolherIdioma: escolherIdioma, eventosVisiveis: eventosVisiveis };
  if (document.getElementById("conteudo")) iniciar();
})();
