"""Local, deterministic sample of processes with their own public PJe documents."""
import argparse
import csv
import hashlib
import json
import random
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from create_pilot_manifest import subject_codes

SEED = 20261007
PLACES = {743: 'Brasília/DF', 1798: 'Formosa/GO', 2788: 'Luziânia/GO'}


def select(rows, limit, seed):
    """Round robin over observed strata, shuffled locally; one row per process."""
    if limit < 0:
        raise ValueError('limit must be non-negative')
    strata = defaultdict(list)
    seen = set()
    for row in sorted(rows, key=lambda x: x['cnj']):
        if row['cnj'] in seen:
            raise ValueError('duplicate CNJ')
        seen.add(row['cnj'])
        strata[(row['sede'], row['assunto_estrato'], row['ano'], row['presenca_decisao'], row['tipos'])].append(row)
    rng = random.Random(seed)
    keys = sorted(strata)
    for key in keys:
        rng.shuffle(strata[key])
    # Rotate sites and their strata independently to avoid lexical cut-off bias.
    by_site = defaultdict(list)
    for key in keys:
        by_site[key[0]].append(key)
    for site_keys in by_site.values():
        rng.shuffle(site_keys)
    sites = sorted(by_site)
    rng.shuffle(sites)
    result = []
    while sites and len(result) < limit:
        for site in list(sites):
            if len(result) >= limit:
                break
            site_keys = by_site[site]
            key = site_keys.pop(0)
            result.append(strata[key].pop())
            if strata[key]:
                site_keys.append(key)
            if not site_keys:
                sites.remove(site)
    return result


def load(c):
    codes = subject_codes(c)
    placeholders = ','.join('?' for _ in codes)
    sql = f'''SELECT p.id,p.numero_processo,r.id,r.grau,r.orgao_codigo,r.orgao_nome,
       CAST(json_extract(r.payload,'$.orgaoJulgador.codigoMunicipioIBGE') AS INTEGER),
       r.data_ajuizamento,a.codigo,a.nome
       FROM processos p JOIN registros_datajud r ON r.processo_id=p.id
       JOIN registro_assuntos ra ON ra.registro_id=r.id JOIN assuntos a ON a.codigo=ra.assunto_codigo
       WHERE r.tribunal='TRF1' AND r.grau IN ('G1','JE') AND (r.nivel_sigilo=0 OR r.nivel_sigilo IS NULL)
       AND CAST(json_extract(r.payload,'$.orgaoJulgador.codigoMunicipioIBGE') AS INTEGER) IN (743,1798,2788)
       AND a.codigo IN ({placeholders}) ORDER BY p.numero_processo,r.id,a.codigo'''
    items = {}
    for pid,cnj,rid,grau,orgcode,org,place,date,code,name in c.execute(sql, sorted(codes)):
        item = items.setdefault(pid, dict(processo_id=pid,cnj=cnj,registro_datajud_id=rid,grau=grau,
            orgao_codigo=orgcode,orgao=org,municipio_codigo_datajud=place,sede=PLACES[place],
            ano=(date or '')[:4] or 'sem_data',assuntos={},documentos=[]))
        item['assuntos'][str(code)] = name
    for pid,docid,origin,hashvalue,kind,numbers in c.execute('''SELECT dp.processo_id,d.id,d.documento_id,d.hash_conteudo,d.tipo_documento,d.numeros_cnj
       FROM documento_processos dp JOIN documentos_publicos d ON d.id=dp.documento_id
       WHERE dp.criterio='cnj_explicito' AND d.fonte='pje_trf1' ORDER BY dp.processo_id,d.id'''):
        item = items.get(pid)
        if item and item['cnj'] in json.loads(numbers or '[]'):
            item['documentos'].append(dict(id=docid,documento_id=origin,hash_conteudo=hashvalue,tipo=kind))
    eligible = []
    for item in items.values():
        if not item['documentos']:
            continue
        item['assunto_estrato'] = next((str(x) for x in (11946,11947,6114) if str(x) in item['assuntos']), sorted(item['assuntos'])[0])
        types = sorted({d['tipo'] or 'não informado' for d in item['documentos']})
        item['tipos'] = ' | '.join(types)
        # Presence is a document descriptor, never an inferred legal outcome.
        item['presenca_decisao'] = any(any(x in t.lower() for x in ('decis', 'senten', 'acórd', 'acord')) for t in types)
        item['revisao_humana'] = 'pendente'
        eligible.append(item)
    return items, eligible, sorted(codes)


def coverage(rows):
    return {field: dict(sorted(Counter(str(r[field]) for r in rows).items())) for field in
            ('sede','ano','assunto_estrato','presenca_decisao','tipos')}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--database', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seed', type=int, default=SEED)
    p.add_argument('--limit', type=int, default=200)
    args = p.parse_args()
    c = sqlite3.connect(args.database.resolve().as_uri() + '?mode=ro', uri=True)
    all_items, eligible, codes = load(c)
    chosen = select(eligible, args.limit, args.seed)
    review = select(chosen, min(40,len(chosen)), args.seed + 1)
    tables = [x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    audit = {'schema': {t: [dict(zip(('cid','nome','tipo','notnull','default','pk'), col)) for col in c.execute('PRAGMA table_info("'+t+'")')] for t in tables},
        'contagens_tabelas': {t:c.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in tables},
        'fontes_documentais': dict(c.execute('SELECT fonte,COUNT(*) FROM documentos_publicos GROUP BY fonte').fetchall()),
        'tipos_documentais_pje': dict(c.execute("SELECT COALESCE(tipo_documento,'não informado'),COUNT(*) FROM documentos_publicos WHERE fonte='pje_trf1' GROUP BY tipo_documento").fetchall())}
    c.close()
    meta = dict(versao='amostragem_inicial_v1',semente=args.seed,algoritmo='processos ordenados por CNJ; shuffle Python Random de processos, sedes e estratos; round-robin por sede e, dentro desta, assunto, ano, presença de decisão e combinação de tipos; sem reposição',
        fonte_db=str(args.database),codigos_tpu=codes,candidatos=len(all_items),elegiveis=len(eligible),selecionados=len(chosen),deficit=max(0,args.limit-len(chosen)),
        cobertura_elegivel=coverage(eligible),cobertura_selecionada=coverage(chosen),auditoria=audit,
        observacao='Amostra de disponibilidade, não representativa. Sede do órgão não comprova residência. Assunto não confirma concessão. Decisão é rótulo documental, não resultado. Revisão humana pendente.')
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('manifesto',chosen),('revisao_humana_40',review)]:
        (args.output / (name+'.json')).write_text(json.dumps({'metadados':meta,'processos':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        with (args.output / (name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
            fields=list(rows[0]) if rows else ['processo_id','cnj','documentos','revisao_humana']
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for row in rows:
                w.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    (args.output/'auditoria.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'candidatos':len(all_items),'elegiveis':len(eligible),'selecionados':len(chosen),'revisao_pendente':len(review),'deficit':meta['deficit']},ensure_ascii=False))


if __name__ == '__main__':
    main()
