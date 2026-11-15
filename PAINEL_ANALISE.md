# Análise dos casos pela aplicação

Inicie na raiz do repositório:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\painel-pesquisa.ps1
```

Abra `http://127.0.0.1:8000/admin/analise`. O script usa o banco consolidado
local e o ambiente `.venv`. Para outro banco ou porta, use `-Banco caminho.sqlite`
e `-Porta 8001`. As revisões ficam no banco escolhido; não há sincronização automática.

1. Filtre casos por CNJ, sede do órgão, assunto, ano e estado da revisão.
2. Abra o processo e escolha uma peça no seletor. Publicações do Comunica
   também podem ser lidas quando existirem.
3. Use a busca textual para localizar expressões. Selecione um trecho do
   documento e clique em **Citar seleção** para anexar evidência.
4. Registre responsável, síntese natural, motivo da judicialização, lacunas
   e decisão de inclusão. Salve um rascunho ou conclua a revisão.
5. Confira a interpretação da IA, os dados de capa e a linha do tempo nas
   outras abas. Citações documentais da IA levam à versão do texto citada.
6. Consulte o histórico para comparar revisões anteriores. Cada salvamento
   acrescenta uma versão; o resultado original da IA é preservado.

A fila padrão seleciona candidatos TRF1 de Brasília/Formosa/Luziânia com
documentos. Ela não é o manifesto congelado de 200 casos. Desmarque o recorte
e/ou o filtro documental para explorar o cadastro completo. Assuntos e sede
não confirmam concessão inicial ou residência.

O painel lê extrações IA já armazenadas; não dispara a IpeaIA. Quando não há
resultado, mostra essa ausência. A revisão humana funciona independentemente
de haver análise automática. O nome do responsável é declarado, não um login.

Os textos e a revisão são acessados pelo endereço local `127.0.0.1` ou
`localhost`. A tabela `revisoes_caso` é criada ao iniciar a API e integra a
exportação portátil. Em PostgreSQL existe migração aditiva `20261103_0009`.
Antes de consolidar bancos distintos, adaptar o remapeamento dos IDs nas
evidências humanas, conforme o contrato.

## Verificação da entrega

Testes de backend cobrem persistência, histórico, conflitos de edição,
rejeição de citações inventadas, documentos de outro processo, hashes errados
e restrição de acesso local. Teste de navegador usa exclusivamente dados
sintéticos e percorre leitura, seleção de citação, rascunho, conclusão,
histórico e estado sem IA. Layout verificado em 1512 px e 390 px.

Integração conferida no banco real: 871 candidatos com documentos vinculados
na fila padrão, abertura de documento com texto e nenhuma revisão sintética
gravada nos processos reais. A quantidade difere dos 843 casos PJe porque a
fila também aceita documentos de outras fontes com vínculo CNJ explícito.

## Auditoria de interface

Escopo: código da tela anterior e nova tela renderizada em desktop/mobile,
incluindo estados preenchido e sem extração IA. Não foram avaliados usuários reais.

| Prioridade | Classe | Evidência anterior | Correção |
| --- | --- | --- | --- |
| P0 | Defeito de qualidade | Documentos PJe apareciam com texto retido na listagem comum | Leitor local com texto e controle de origem |
| P1 | Defeito de qualidade | Seção de revisão apenas dizia que não havia ação disponível | Formulário persistente, conclusão e histórico |
| P1 | Defeito de qualidade | `renderDetail` colocava capa e longa timeline antes dos documentos | Leitura como aba inicial e capa/timeline sob demanda |
| P1 | Defeito de qualidade | `loadStats` priorizava registros e movimentos no espaço de análise | Fila filtrada e caso selecionado como foco da nova página |
| P2 | Defeito de qualidade | Evidências e origem exigiam navegação entre seções longas | Leitor ao lado da revisão e ação de conferir citação |

A hierarquia visual prioriza processo, documento e revisão; informações técnicas
e JSON permanecem sob demanda. A maior correção é disponibilizar o documento
e o registro de interpretação no mesmo fluxo.

Skills usadas: `visual-hierarchy` orientou posição, contraste e prioridade de leitura;
`audit-ai-design-slop` fundamentou as correções acima. O template solicitado
`artifact-template-analytics-dashboard` é uma planilha Excel para KPIs comerciais;
foi inspecionado, mas seu arquivo não foi alterado e ele não foi convertido em painel web.
