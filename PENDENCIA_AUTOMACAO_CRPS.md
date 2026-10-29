# Pendência: coleta assistida do CRPS

Registrada em 08/10/2026 a pedido do pesquisador. Não implementada.

Criar automação local com Playwright, abrindo navegador próprio. O pesquisador
faz o login gov.br manualmente; não coletar senha, exportar credenciais nem
contornar CAPTCHA. Pausar quando houver bloqueio ou sessão expirada.

Começar com dez decisões: percorrer resultados e capturar ementa, voto,
decisório e metadados de protocolo, acórdão, unidade julgadora, data e URL.
Preservar texto original local e registrar hash para evitar duplicatas.
Usar períodos de até 90 dias, conforme limite observado pelo pesquisador.
Diversificar unidades, períodos, BPC idoso/PcD e resultados recursais.

Antes da persistência, atualizar docs/CONTRATOS.md com o contrato específico.
Manter corpus administrativo separado: não criar processos judiciais nem
atribuir motivos a casos DataJud sem vínculo individual explícito.
Revisar dados pessoais antes de publicação ou envio à IA. Os quatro arquivos
em protocolos/ são material local de referência, não autorizações de divulgação.

## Frentes independentes do login

- Ampliar jurisprudência publicada TNU/TRF2/TRF4/TRF5/TRF6 pelos coletores
  existentes, com lotes limitados e deduplicação. Corpus complementar, não
  ampliação automática da amostra judicial DF/RIDE.
- Verificar recuperação do Comunica e então retomar os CNJs pendentes,
  respeitando interrupção por falhas/bloqueios. Prioridade para textos da amostra.
- Ampliar cobertura temporal dos agregados INSS já suportados, sem atribuir
  motivos agregados a processos individuais.

Esta nota não representa nova coleta nem alteração do banco.
