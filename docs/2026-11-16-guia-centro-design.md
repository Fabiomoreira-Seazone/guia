# Guia do Centro de Florianópolis para hóspedes: design

Data: 2026-11-16 · Status: **aprovado pelo Fabio**

## Intenção
Hoje as instruções de check-in vão como um texto no WhatsApp. A ideia é mandar, junto com esse texto, um link para uma página online com o guia do centro (pontos turísticos, eventos do mês e links do Google Maps) e as informações do imóvel. Uma página online é mais dinâmica que um PDF.

## Objetivos
- Ter um site gratuito no GitHub Pages, pensado para celular.
- Ter três idiomas: **português, espanhol e inglês**, com um botão para trocar de idioma (há muitos hóspedes argentinos e também estrangeiros de fora da América Latina).
- **Guia do centro** (o mesmo para todos): pontos turísticos, onde comer e beber, serviços úteis (mercado, farmácia, hospital, transporte) e **eventos do mês**. Cada item com o link "Abrir no Google Maps".
- **Uma página por imóvel** (ex.: `/TVT303`): endereço com mapa, horários de check-in e check-out, como chegar e estacionar, regras da casa e contato. Cada página tem um link para o guia.
- Eventos atualizados todo mês: o Claude pesquisa e atualiza. Isso pode virar uma tarefa agendada depois.
- Novo modelo de mensagem do WhatsApp: saudação + senha da porta + Wi-Fi + link do imóvel.

## Anti-objetivos (o que não pode acontecer)
- **Nenhuma senha na página**: nem da porta, nem do Wi-Fi. O repositório é público e o histórico de alterações também. As senhas vão só no WhatsApp.

## Fora do escopo
- Link personalizado por reserva ou com prazo de validade.
- Integração automática com o Sapron.

## Abordagens consideradas
1. **GitHub Pages (escolhida):** grátis, sem limite de atualizações. O Fabio cria a conta.
2. Lovable: publica com facilidade, mas cada alteração gasta créditos.
3. Artifact do Claude: rápido, mas é privado e talvez não abra sem conta. Usado só como **rascunho** para aprovar o conteúdo e o visual.

Também foi descartado colocar a senha da porta na página a cada check-in: o repositório é público, o histórico guarda as senhas antigas e o link continua funcionando depois do checkout.

## Fontes de dados
- Lista de imóveis e endereços: Sapron (tools da franquia). O que faltar (estacionamento, regras específicas) é perguntado ao Fabio.
- Pontos turísticos e eventos: pesquisa na web, com conferência dos endereços.

## Decisões deixadas para quem constrói
- Visual, tipografia e organização das seções.
- Estrutura técnica do site estático (HTML/CSS/JS simples, sem framework, para facilitar a manutenção).
