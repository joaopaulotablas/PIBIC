"""Read all project Markdown and record the inventory without copying its contents."""
import hashlib
import json
import os
from pathlib import Path

excluded = {'.git','.venv','venv','node_modules','__pycache__','.pytest_cache','.cache','.next','.turbo','dist','build','coverage','.mypy_cache','.ruff_cache'}
files = []
errors = []
for root, dirs, names in os.walk('.', onerror=lambda error: errors.append(str(error))):
    dirs[:] = sorted(d for d in dirs if d not in excluded and not d.endswith('.egg-info'))
    for name in sorted(names):
        if name.lower().endswith('.md'):
            path = Path(root) / name
            if path.as_posix() == 'docs/AMOSTRAGEM_INICIAL.md':
                continue
            try:
                data = path.read_bytes()
                data.decode('utf-8-sig')
                files.append((path.as_posix(),len(data),hashlib.sha256(data).hexdigest()))
            except (OSError, UnicodeError) as e:
                errors.append(f'{path}: {e}')
a = json.loads(Path('data/amostragem-inicial/auditoria.json').read_text(encoding='utf-8'))
lines = ['# Auditoria e amostragem inicial', '',
'O plano pretende estudar ações de concessão de BPC no TRF1 e suas características, com tratamento local de dados pessoais e validação humana. O banco oferece candidatos por assuntos e sede, não comprova pedido inicial de concessão, residência nem resultados; o PJe público fornece documentos disponíveis, não autos completos. O plano cita e-Proc/TRF1 e pressupõe acesso amplo; os contratos atuais descrevem consulta pública PJe limitada e revisão de privacidade pendente. As fontes jurisprudenciais são complementares, não documentos próprios da amostra.', '',
'A unidade é o processo único; documentos PJe com vínculo CNJ explícito e CNJ conferido em numeros_cnj são anexados por ID e hash. Seleção por assunto 6114 e descendentes TPU disponíveis, TRF1, grau G1/JE, sem sigilo informado ou nível zero, sede Brasília/Formosa/Luziânia. A ausência de sigilo informado não comprova publicidade. O primeiro registro ordenado por ID define sede e ano quando há vários registros elegíveis; assuntos são unidos. Presença de decisão considera rótulos sentença, decisão ou acórdão e não representa resultado. Despacho isolado conta como ausência desse rótulo. Todos são candidatos e revisão humana pendente.', '',
f"Banco: {a['auditoria']['contagens_tabelas']}. Documentos por fonte: {a['auditoria']['fontes_documentais']}. Candidatos: {a['candidatos']}; elegíveis com documento próprio: {a['elegiveis']}; selecionados: {a['selecionados']}; déficit: {a['deficit']}. A cópia SQLite foi feita por backup do original aberto em modo ro; consultas ocorreram em modo ro na cópia.", '',
f"Semente {a['semente']}: {a['algoritmo']}. A subamostra de até 40 é selecionada entre os 200 com semente 20261008. Quotas são realizadas pelo rodízio e não quotas populacionais. Coberturas completas e contagens por assunto, sede, ano, presença e combinações de tipos estão em auditoria.json; JSON/CSV guardam IDs e hashes sem texto dos documentos.", '',
f"Sedes elegíveis: {a['cobertura_elegivel']['sede']}; selecionadas: {a['cobertura_selecionada']['sede']}. Assuntos elegíveis: {a['cobertura_elegivel']['assunto_estrato']}; selecionados: {a['cobertura_selecionada']['assunto_estrato']}. Presença de decisão elegível: {a['cobertura_elegivel']['presenca_decisao']}; selecionada: {a['cobertura_selecionada']['presenca_decisao']}.", '',
'Trata-se de amostra de conveniência condicionada à coleta e disponibilidade documental, com grande desigualdade por ano, assunto e tipo. Não há base para inferir representatividade populacional, prevalência, procedência ou concessão. A distribuição por sede não identifica domicílio. Privacidade e anotação humana permanecem pendentes; nenhum texto foi enviado a IA externa.', '',
'Execução: `.venv/Scripts/python.exe scripts/sample_initial.py --database data/amostragem-inicial/auditoria-backup.sqlite --output data/amostragem-inicial`. O backup é arquivo local potencialmente sensível; não publicar manifesto individual sem revisão de privacidade.', '',
f'## Inventário de leitura Markdown ({len(files)} arquivos)', '',
'Leitura integral de bytes UTF-8; submódulos incluídos, diretórios de dependências e caches excluídos. Caminho, bytes e SHA-256 identificam o conteúdo lido. Este relatório é excluído do próprio inventário para evitar autorreferência.', '']
for path,size,digest in files:
    if path != 'docs/AMOSTRAGEM_INICIAL.md':
        lines.append(f'- `{path}` — {size} bytes — SHA-256 `{digest}`')
lines += ['', '## Falhas de leitura', '', *(errors or ['Nenhuma.'])]
Path('docs/AMOSTRAGEM_INICIAL.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'markdown={len(files)} erros={len(errors)}')
