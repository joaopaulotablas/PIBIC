# Auditoria e amostragem inicial

O plano pretende estudar ações de concessão de BPC no TRF1 e suas características, com tratamento local de dados pessoais e validação humana. O banco oferece candidatos por assuntos e sede, não comprova pedido inicial de concessão, residência nem resultados; o PJe público fornece documentos disponíveis, não autos completos. O plano cita e-Proc/TRF1 e pressupõe acesso amplo; os contratos atuais descrevem consulta pública PJe limitada e revisão de privacidade pendente. As fontes jurisprudenciais são complementares, não documentos próprios da amostra.

A unidade é o processo único; documentos PJe com vínculo CNJ explícito e CNJ conferido em numeros_cnj são anexados por ID e hash. Seleção por assunto 6114 e descendentes TPU disponíveis, TRF1, grau G1/JE, sem sigilo informado ou nível zero, sede Brasília/Formosa/Luziânia. A ausência de sigilo informado não comprova publicidade. O primeiro registro ordenado por ID define sede e ano quando há vários registros elegíveis; assuntos são unidos. Presença de decisão considera rótulos sentença, decisão ou acórdão e não representa resultado. Despacho isolado conta como ausência desse rótulo. Todos são candidatos e revisão humana pendente.

Banco: {'assuntos': 140, 'coleta_registros_datajud': 20590, 'coletas': 24417, 'comunicacoes_pje': 302, 'consultas_pje': 1241, 'documento_chunks': 0, 'documento_processos': 2508, 'documentos_publicos': 41353, 'extracoes_ia': 0, 'indicadores_bpc_municipio': 124, 'indicadores_inss_concessoes': 185, 'indicadores_inss_indeferimentos': 467, 'indicadores_suas_municipio': 8557, 'movimentos': 907521, 'processos': 16737, 'recursos_externos': 454, 'referencias_tpu': 6177, 'registro_assuntos': 18842, 'registros_datajud': 16796, 'tarefas_painel': 6}. Documentos por fonte: {'cjf_trf1': 18535, 'pje_trf1': 2281, 'stj': 425, 'tnu': 766, 'trf1_arquivo': 7, 'trf2_jurisprudencia': 3111, 'trf4_jurisprudencia': 5518, 'trf5_jurisprudencia': 1351, 'trf6_jurisprudencia': 9359}. Candidatos: 3823; elegíveis com documento próprio: 843; selecionados: 200; déficit: 0. A cópia SQLite foi feita por backup do original aberto em modo ro; consultas ocorreram em modo ro na cópia.

Semente 20261007: processos ordenados por CNJ; shuffle Python Random de processos, sedes e estratos; round-robin por sede e, dentro desta, assunto, ano, presença de decisão e combinação de tipos; sem reposição. A subamostra de até 40 é selecionada entre os 200 com semente 20261008. Quotas são realizadas pelo rodízio e não quotas populacionais. Coberturas completas e contagens por assunto, sede, ano, presença e combinações de tipos estão em auditoria.json; JSON/CSV guardam IDs e hashes sem texto dos documentos.

Sedes elegíveis: {'Brasília/DF': 245, 'Formosa/GO': 318, 'Luziânia/GO': 280}; selecionadas: {'Brasília/DF': 67, 'Formosa/GO': 66, 'Luziânia/GO': 67}. Assuntos elegíveis: {'11946': 724, '11947': 118, '6114': 1}; selecionados: {'11946': 141, '11947': 59}. Presença de decisão elegível: {'False': 25, 'True': 818}; selecionada: {'False': 11, 'True': 189}.

Trata-se de amostra de conveniência condicionada à coleta e disponibilidade documental, com grande desigualdade por ano, assunto e tipo. Não há base para inferir representatividade populacional, prevalência, procedência ou concessão. A distribuição por sede não identifica domicílio. Privacidade e anotação humana permanecem pendentes; nenhum texto foi enviado a IA externa.

Execução: `.venv/Scripts/python.exe scripts/sample_initial.py --database data/amostragem-inicial/auditoria-backup.sqlite --output data/amostragem-inicial`. O backup é arquivo local potencialmente sensível; não publicar manifesto individual sem revisão de privacidade.

## Inventário de leitura Markdown (29 arquivos)

Leitura integral de bytes UTF-8; submódulos incluídos, diretórios de dependências e caches excluídos. Caminho, bytes e SHA-256 identificam o conteúdo lido. Este relatório é excluído do próprio inventário para evitar autorreferência.

- `GUIA_TRANSFERENCIA_BPC_CONSOLIDADO.md` — 4840 bytes — SHA-256 `acaa1608381828902a704b9481e461892648d4352939232aa3e4fa4f56c2ebd2`
- `PENDENCIA_AUTOMACAO_CRPS.md` — 1696 bytes — SHA-256 `c4cbfacbd65a2b826e8ae84961a581a6e3211118e36b51871615c658b3653f7f`
- `PLANO_COLETA_E_CONSOLIDACAO_LUNA.md` — 18970 bytes — SHA-256 `18e8498f20d5747ca1a47d2756ba7c4aaa1aa8b83441678b651d4146ba690c4f`
- `PROMPT_LUNA_AMPLIAR_COMUNICA.md` — 6248 bytes — SHA-256 `ff684592ece5e519b458d99c901fb66e1d7fe5d236e9018085e3939161548f88`
- `PROMPT_REVISAO_IPEAIA.md` — 13979 bytes — SHA-256 `91887287279a4b00a2c44336504783707cd608232e11c124d7b34de15f17d12e`
- `README.md` — 12698 bytes — SHA-256 `7798e1f766b2290d262b72a855996f958fd3e73de8d0636f82efcd3c4f57904b`
- `RELATORIO_AMPLIACAO_COMUNICA_20261008.md` — 21455 bytes — SHA-256 `13b92d75de21f2838a678e4a2f633f4fe8f8999b5bc911170f93861feb216266`
- `RELATORIO_COLETA_AUTONOMA_20261008.md` — 3039 bytes — SHA-256 `c2946fb41b9e1f96a979ffe46a43f2b081134495da560d47a25f22d8576d1498`
- `RELATORIO_COLETA_COMUNICA_DIARIOS_LUNA.md` — 17139 bytes — SHA-256 `e215b0de87f21282960e5e2182d78796abde96f104014671c24568c3f9352696`
- `RELATORIO_CORRECOES_E_FONTES_20261008.md` — 2954 bytes — SHA-256 `9862630456dc0b5bbee8e69f94adda9c4e6381716e56b45a88b14dc4e3a347ee`
- `RELATORIO_EXECUCAO_COLETA_LUNA.md` — 17500 bytes — SHA-256 `3b6a4fafaaf7a801337a862d2f3d138898286e87ba2beee6e46d8b252bce6db1`
- `RELATORIO_PJE_PUBLICO_20261008.md` — 14651 bytes — SHA-256 `c3d1b09da2f666e080aa07a1c51bbb5d218264f66a2d588895d2a41bd9c660ed`
- `RELATORIO_STATUS_PROJETO_20261014.md` — 13009 bytes — SHA-256 `9897039648cdc112552cd289707395fe38cfb34a94147c187012540e874e2109`
- `RESTAURAR_BANCO.md` — 2528 bytes — SHA-256 `49e70b6b6de964d064f32c17796289d54fcda6aae26faf1a26f37ffa717ae602`
- `REVISAO_E_AMPLIACAO_FONTES_20261008.md` — 9390 bytes — SHA-256 `c08ce70f5fee52e217a5291434e114d016fedc9ac63271d146185c3c2b9cf569`
- `SEM_DOCKER.md` — 14457 bytes — SHA-256 `52ef765fefda84dec9599d6a934bfe3aa76f7c66ed1dce16ffbc3d8afe463744`
- `data/revisao_piloto_luna.md` — 3978 bytes — SHA-256 `94bd7c5d94b27c05de4520d80ec41ced4012467d3be9bf1b1b170eef2b446ed7`
- `datajud/datajud/Readme.md` — 11164 bytes — SHA-256 `5ed03786b79dad7c9d6a1e98f8e42f78d795a247869edb9aa9eae66dd29b8f7e`
- `docs/ARQUITETURA.md` — 1814 bytes — SHA-256 `4a52abc67dedffffe3a7dae099d2fdf5522d93f9c7609c6a9641b5751f7896a7`
- `docs/CONTRATOS.md` — 90273 bytes — SHA-256 `f9a2766a349a3002354f7883f28c69d6bee731c0c296830ed20309498fcf3176`
- `docs/ESCOPO_PESQUISA.md` — 7865 bytes — SHA-256 `b66e9fd999cf2aa449921d3adc27474cfdf18d2fb420e7ba9587bf6d7aaae6ff`
- `docs/FONTES_ABERTAS.md` — 117022 bytes — SHA-256 `7293dcea0bbe5b71d5083e157fc5e99439b92fe7740c915de3e6bf752005e210`
- `docs/ONDAS_AMOSTRAGEM_INICIAL.md` — 5463 bytes — SHA-256 `7f7609fb29e0dbc325573dd37a4682f2152ec5cd0f384a82bbeb51877af6382c`
- `docs/RASCUNHOS_SOLICITACAO_ACESSO.md` — 2703 bytes — SHA-256 `dbf77b086cb8d7482a36feeb1de9de96d1f7b58ede464c7a7a6aaa189d1d4c29`
- `ingestion/README.md` — 888 bytes — SHA-256 `2260523b189a12937fa3df394937e2800c839b336e042d9db769d27b3dd66e80`
- `jeferson/bpc-loas/api_demo_requests.md` — 2914 bytes — SHA-256 `f4a4c01b5c73743cd20ae2f983a209b18449f06b6324276ad5f0247975fd05af`
- `jeferson/bpc-loas/demo.md` — 1324 bytes — SHA-256 `5b56ad14a64268f106a2190f8e93fa5b8ab56bf1de4b41330273b24308d22ce1`
- `jeferson/bpc-loas/literatura_base_tecnica.md` — 13788 bytes — SHA-256 `8f016254021eb4c59fe71dc03108a84ff6f4f846fb85de7d86e089227dc14db8`
- `jeferson/bpc-loas/readme.md` — 21370 bytes — SHA-256 `b11aed227192dd642fb6adc9583b0612490a598b59d724e0cb3a0782cb1106b7`

## Falhas de leitura

Nenhuma.
