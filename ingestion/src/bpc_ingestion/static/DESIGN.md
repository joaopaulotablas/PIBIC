# Dossiê de pesquisa BPC Jud

## 1. Produto
Pesquisadores conferem origem, documentos e limitações dos candidatos BPC/LOAS. Sucesso significa localizar a evidência e perceber a ausência de validação humana. Não inferir residência da sede, concessão de assunto ou revisão humana de status automático.

## 2. Design Read
Superfície read/operate em HTML, CSS e JavaScript nativos. Linguagem documental, alinhada à esquerda. V3 M1 D6.

## 3. Direção
Manter o verde do painel. Lista compacta à esquerda, dossiê amplo à direita. Sem imagens decorativas, cards aninhados ou métricas inventadas.

## 4. Cores
`--ink: #17212b`, `--muted: #52636d`, `--accent: #155e63`, `--border: #ccd6d8`, `--paper: #fff`, `--canvas: #f3f6f7`, `--warning: #705018`. O accent identifica ações e seleção; aviso amarelo indica limitação real.

## 5. Tipografia
Fonte system-ui na operação; fontes Georgia e Times New Roman na leitura jurídica, 18px/1.75 e medida máxima 72ch. Títulos 20/28/36px, números tabulares. Sem downloads de fontes.

## 6. Espaçamento e layout
Escala principal 4/8/12/16/24/32px. Dossiê ocupa a maior coluna. Abaixo de 900px, lista e dossiê empilham; seleção move foco ao dossiê, com link para voltar à lista. Alvos de 44px.

## 7. Componentes
Controles e painéis com radius 4px, sem sombras. Avisos e seleção usam borda lateral como estado. Timeline usa linha neutra para sequência; citações usam borda para distinguir evidência de narrativa. Textos extensos abrem em details, sem janela interna curta.

## 8. Movimento
Sem animações; foco e rolagem nativos, sem smooth scroll obrigatório.

## 9. Conteúdo
Somente contratos FastAPI existentes. Resumos documentais e trechos ficam ocultos por padrão, com solicitação local explícita. Texto de origem é textContent, nunca HTML executável. Links aceitam HTTP(S).

## 10. Limites
Explicitar indisponibilidade e ausência. Nunca tratar confiança, status automático ou coincidência textual como validação jurídica ou humana. A comparação de intervalo Unicode verifica apenas o texto recebido.

## 11. Decisões
2026-10-29: CSS nativo preservado, pois não existe pipeline Tailwind. Sem dependência ou CDN. Skills aura-asset-images, visual-hierarchy, tailwindcss, responsive-design e antiwebslop consultadas; imagens não servem à tarefa de leitura.

## 12. Referências
docs/CONTRATOS.md, docs/ESCOPO_PESQUISA.md, plano.txt. Este arquivo documenta apenas a superfície estática do painel.
