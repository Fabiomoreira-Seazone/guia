# Guia do Centro: plano de implementação

> **Para agentes:** use superpowers:subagent-driven-development ou superpowers:executing-plans. Os passos usam checkbox (`- [ ]`).

**Objetivo:** construir um site estático, em 3 idiomas, com o guia do centro de Florianópolis e uma página por imóvel, publicado no GitHub Pages.

**Arquitetura:** o conteúdo fica em arquivos JSON (`site/data/`). Um único `app.js` lê esses arquivos e monta as páginas no navegador. Cada imóvel tem uma pasta `site/<CODIGO>/index.html`, que só carrega o `app.js` com o código do imóvel. Um script de validação em Node garante que todo texto existe nos 3 idiomas, que todo lugar tem link do Maps e que **nenhuma senha** foi parar nos dados.

**Tecnologia:** HTML, CSS e JS puro (sem framework e sem build). Os testes rodam com Node (`node --test`). A hospedagem é o GitHub Pages.

**Spec:** `GUIA_CENTRO/docs/2026-11-16-guia-centro-design.md`

## Restrições globais
- Idiomas: `pt`, `es`, `en`. Todo texto voltado ao hóspede é um objeto `{pt, es, en}`.
- Proibido nos dados e no HTML: senhas da porta e do Wi-Fi. O validador barra chaves ou textos com `senha|password|contraseña|wifi|wi-fi`, exceto a frase fixa da UI "a senha é enviada pelo WhatsApp".
- Todo lugar e todo evento tem `maps_url` começando com `https://www.google.com/maps/` ou `https://maps.app.goo.gl/`.
- Mobile first: funciona em 360px de largura, sem rolagem horizontal.
- Endereço do imóvel: `/<CODIGO>/` (ex.: `/TVT303/`).

## Pontos de atenção na revisão
1. **Idioma inicial:** usar o idioma do celular (`navigator.language`): `es*` → es, `pt*` → pt, qualquer outro → en. A escolha manual fica salva em `localStorage`, com try/catch.
2. **Evento que já passou:** eventos com `data_fim` anterior a hoje não aparecem. Se o mês não tiver nenhum evento, mostrar "Agenda em atualização".
3. **Código de imóvel inexistente** (`/XYZ/`): mostrar o guia do centro com um aviso, não uma página quebrada.
4. **Texto faltando num idioma:** o validador falha. Isso não pode ser descoberto pelo hóspede.
5. **Senha colada por engano nos dados:** o validador falha (teste dedicado na Task 1).

---

### Task 1: Formato dos dados e validador

**Arquivos:**
- Criar: `GUIA_CENTRO/tools/validar.mjs`, `GUIA_CENTRO/tools/validar.test.mjs`
- Criar (vazios, válidos): `GUIA_CENTRO/site/data/guia.json`, `eventos.json`, `imoveis.json`, `ui.json`

**Interfaces (produz):**
- `guia.json`: `{ categorias: [{ id, titulo:{pt,es,en}, itens:[{ id, nome, descricao:{pt,es,en}, endereco, maps_url }] }] }`. As categorias são `pontos`, `comer`, `servicos`.
- `eventos.json`: `{ atualizado_em:"YYYY-MM-DD", eventos:[{ nome:{pt,es,en}, data_inicio, data_fim, horario, local, maps_url, descricao:{pt,es,en}, link? }] }`
- `imoveis.json`: `{ imoveis:[{ codigo, nome, endereco, maps_url, checkin, checkout, como_chegar:{pt,es,en}, estacionamento:{pt,es,en}, regras:[{pt,es,en}], contato_whatsapp }] }`
- `ui.json`: `{ "<chave>": {pt,es,en} }`
- `validar(dados) -> string[]` (lista de erros; vazia quando está tudo certo). A CLI `node tools/validar.mjs` encerra com código 1 se houver erro e também confere se existe `site/<codigo>/index.html` para cada imóvel.

- [ ] **Passo 1: testes que falham**, em `validar.test.mjs`:
  - `aceita dados mínimos válidos` → `validar(ok)` retorna `[]`
  - `rejeita texto sem idioma` → removendo `en` de uma descrição, aparece um erro contendo `"en"`
  - `rejeita maps_url inválido` → `"http://x.com"` gera erro
  - `rejeita senha nos dados` → `regras:[{pt:"Senha da porta 1234",...}]` gera erro contendo `senha`; a chave `wifi` também gera erro
  - `rejeita evento com data_fim < data_inicio`
- [ ] **Passo 2:** `node --test tools/` → FAIL
- [ ] **Passo 3:** implementar `validar` + CLI
- [ ] **Passo 4:** `node --test tools/` → PASS
- [ ] **Passo 5:** commit `feat: formato dos dados e validador`

### Task 2: Renderizador, visual e troca de idioma

**Arquivos:**
- Criar: `site/index.html` (guia), `site/assets/app.js`, `site/assets/style.css`, `site/_modelo-imovel/index.html` (stub que define `window.IMOVEL="<CODIGO>"` e carrega `../assets/app.js`)

**Interfaces:**
- Consome: os JSON da Task 1.
- Produz: `escolherIdioma(navLang, salvo) -> "pt"|"es"|"en"` e `eventosVisiveis(eventos, hojeISO) -> evento[]`, exportados também para teste (o arquivo funciona como módulo ES).

- [ ] **Passo 1: testes que falham**, em `tools/app.test.mjs`:
  - `escolherIdioma("es-AR",null)` === `"es"`; `("de-DE",null)` === `"en"`; `("pt-BR","en")` === `"en"`
  - `eventosVisiveis` remove o evento com `data_fim` = `"2026-11-15"` quando hoje é `"2026-11-16"` e mantém o que termina hoje
- [ ] **Passo 2:** rodar → FAIL
- [ ] **Passo 3:** implementar o `app.js`:
  - montar o guia (categorias em cards, botão "Abrir no Google Maps" em cada item) e a seção de eventos;
  - na página do imóvel, mostrar o bloco do imóvel antes do guia;
  - código inexistente → aviso + guia;
  - seletor PT | ES | EN fixo no topo.
- [ ] **Passo 4:** rodar → PASS. Abrir `site/` com `python3 -m http.server` no navegador em 360px, nos 3 idiomas.
- [ ] **Passo 5:** commit `feat: renderizador e visual do guia`

### Task 3: Conteúdo do guia do centro

**Arquivos:** modificar `site/data/guia.json` e `site/data/ui.json`

- [ ] **Passo 1:** pesquisar e preencher. `pontos`: ~10 itens (Mercado Público, Catedral Metropolitana, Praça XV e Figueira, Ponte Hercílio Luz, Museu Histórico/Palácio Cruz e Sousa, Casa da Alfândega, Beira-Mar Norte, Largo da Alfândega, Rua Victor Meirelles/Centro Histórico, Mirante do Morro da Cruz). `comer`: ~8. `servicos`: mercado, farmácia 24h, hospital/UPA, terminal TICEN, ponto de táxi. Cada item com endereço conferido e `maps_url`.
- [ ] **Passo 2:** `node tools/validar.mjs` → sem erros
- [ ] **Passo 3:** commit `content: guia do centro`

### Task 4: Eventos (novembro e dezembro de 2026)

**Arquivo:** modificar `site/data/eventos.json`

- [ ] **Passo 1:** pesquisar a agenda do centro (prefeitura/turismo de Florianópolis, Mercado Público, Teatro Álvaro de Carvalho, CIC, eventos de Natal e Réveillon). Só entram eventos com data, local e fonte confirmados.
- [ ] **Passo 2:** validar → sem erros
- [ ] **Passo 3:** commit `content: eventos nov-dez 2026`

### Task 5: Páginas dos imóveis

**Arquivos:** modificar `site/data/imoveis.json` e criar `site/<CODIGO>/index.html` para cada imóvel

- [ ] **Passo 1:** listar os imóveis e endereços pelo Sapron (`listar_imoveis` / `detalhar_imovel`). **Não copiar nenhum campo de senha.**
- [ ] **Passo 2:** perguntar ao Fabio, numa mensagem só, o que faltar: estacionamento, regras específicas, horários diferentes do padrão e o WhatsApp de contato.
- [ ] **Passo 3:** preencher e criar as pastas a partir de `_modelo-imovel`
- [ ] **Passo 4:** validar → sem erros
- [ ] **Passo 5:** commit `content: páginas dos imóveis`

### Task 6: Rascunho para aprovação

- [ ] **Passo 1:** publicar uma versão de uma página só (guia + 1 imóvel, dados embutidos) como Artifact privado e mandar o link ao Fabio.
- [ ] **Passo 2:** aplicar os ajustes pedidos nos JSON e no CSS e rodar o validador.

### Task 7: Publicação e modelo de mensagem

**Arquivos:** criar `GUIA_CENTRO/docs/mensagem-whatsapp.md` (pt/es/en: saudação, senha da porta, Wi-Fi, link `https://<usuario>.github.io/<repo>/<CODIGO>/`) e `.github/workflows/pages.yml` (publica `site/` e roda o validador antes)

- [ ] **Passo 1:** o Fabio cria a conta no GitHub. Criar o repositório público, `git init`, conferir com `git grep -inE "senha|password|wifi"`, que deve trazer só a frase da UI, e fazer o push.
- [ ] **Passo 2:** ativar o Pages (fonte: GitHub Actions). Abrir `/` e `/<CODIGO>/` no celular.
- [ ] **Passo 3:** commit `chore: publicação e modelo de mensagem`
