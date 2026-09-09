"""Offline Canon interpretation; no network, credentials or writes to source data."""
import argparse
import copy
import datetime as dt
import json
import math
from pathlib import Path
import re
import sys

REF = Path(__file__).resolve().parents[1] / 'references'
MAPPING = json.loads((REF / 'mappings.json').read_text())


def label(value):
    if not isinstance(value, str):
        return value
    match = re.fullmatch(r'\[((?:\\.|[^\]])*)\]\(https?://[^\s]*\)', value.strip())
    return re.sub(r'\\([\\\[\]])', r'\1', match[1]) if match else value.strip()


def present(value):
    return value is not None and value != '' and value != []


def first(row, names):
    return next((label(row[n]) for n in names if n in row and present(row[n])), None)


def put(target, path, value):
    bits = path.split('.')
    for bit in bits[:-1]:
        target = target.setdefault(bit, {})
    target[bits[-1]] = value


def date_value(value):
    if not isinstance(value, str):
        raise ValueError('date is not a string')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return dt.date.fromisoformat(value).isoformat()
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp timezone missing')
    return parsed.isoformat()


def codes(value):
    if isinstance(value, list):
        values = [label(v) for v in value]
    elif isinstance(value, str):
        # Keep returned Library codes, not pieces of a Markdown URL.
        links = re.findall(r'\[([^\]]+)\]\(https?://[^\s]*\)', value)
        values = links or re.split(r'[,;|\s]+', value.strip())
    else:
        values = []
    return list(dict.fromkeys(str(v).upper().strip() for v in values if present(v)))


def normalize_record(tool, row):
    definition = MAPPING['tools'][tool]
    dataset = MAPPING['datasets'][definition['dataset_id']]
    warnings = []
    record_id = first(row, dataset['record_keys'])
    grain = definition.get('record_granularity', 'award_summary' if tool == 'search_awards' else 'source_record')
    if grain != 'source_record':
        record_id = None
        warnings.append('aggregate_not_a_transaction; retain source metrics and grouping')
    if dataset['dataset_id'] == 'acquisition_forecasts':
        record_id = json.dumps([label(row.get('source')), record_id], separators=(',', ':')) if row.get('source') and record_id else None
    out = {
        'dataset_id': dataset['dataset_id'], 'record_type': dataset['record_type'],
        'record_id': str(record_id) if record_id is not None else None,
        'source_record_id': first(row, ['source_record_id', 'notice_id', 'opportunity_id']),
        'source_name': dataset['source_name'] or row.get('source'),
        'record_granularity': grain, 'source_record': copy.deepcopy(row),
        'identifiers': {}, 'organizations': {}, 'agencies': {}, 'classifications': {},
        'dates': {}, 'financials': {}, 'locations': {}, 'acquisition': {},
        'evidence': {'warnings': warnings},
    }
    if record_id is None:
        warnings.append('stable_record_id_missing_or_aggregate')
    for path, aliases in {**dataset['fields'], **definition.get('fields', {})}.items():
        value = first(row, aliases)
        if value is None:
            continue
        try:
            if path.endswith('.uei') or path.endswith('.cage'):
                value = str(value).upper()
                size = 12 if path.endswith('.uei') else 5
                if not re.fullmatch('[A-Z0-9]{%d}' % size, value):
                    raise ValueError('invalid identifier')
            elif path == 'dates.fiscal_year':
                if not re.fullmatch(r'\d{4}', str(value)):
                    raise ValueError('invalid fiscal year')
                value = int(value)
            elif path.startswith('dates.') or path == 'source_updated_at':
                value = date_value(value)
            elif path.startswith('financials.'):
                if isinstance(value, bool):
                    raise ValueError('boolean amount')
                value = float(value)
                if not math.isfinite(value):
                    raise ValueError('nonfinite amount')
            put(out, path, value)
        except (TypeError, ValueError):
            warnings.append('unmapped_value:' + path)
    for role, organization in out['organizations'].items():
        organization['relationship_type'] = 'source_role'
        organization['relationship_evidence'] = {'role': role, 'dataset_id': dataset['dataset_id']}
    for family in ('naics', 'psc'):
        raw = row.get(family + '_getwab_links')
        values = [item.get('code') for item in raw if isinstance(item, dict)] if isinstance(raw, list) else first(row, [family + '_codes', 'primary_' + family, 'top_' + family, family, family + '_code'])
        normalized = codes(values)
        if normalized:
            out['classifications'][family] = [{'code': c, 'role': 'primary' if row.get('primary_' + family) else 'reported'} for c in normalized]
    if tool == 'search_gsa_contracts' and present(row.get('category')):
        out['classifications']['gsa_sin'] = [{'code': label(row['category'])}]
    if present(row.get('set_aside')) or present(row.get('set_aside_code')):
        out['classifications']['set_aside'] = {'code': label(row.get('set_aside_code')), 'name': label(row.get('set_aside'))}
    if 'amount_is_plausible' in row:
        out['financials']['amount_plausibility'] = row['amount_is_plausible']
    # Explicit geography scopes prevent entity address/POP confusion.
    for scope, prefixes in [('place_of_performance', ['pop_']), ('entity', ['recipient_', '']), ('office', ['office_'])]:
        if scope == 'entity' and tool not in ('search_entities', 'search_exclusions', 'search_gsa_contracts', 'search_assistance_subawards'):
            continue
        for dest, sources in {'address':['address', 'address_1'], 'city':['city'], 'state':['state'], 'postal_code':['zip'], 'country':['country']}.items():
            value = first(row, [p + s for p in prefixes for s in sources])
            if value is not None:
                put(out, 'locations.' + scope + '.' + dest, value)
    return out


def normalize_result(tool, payload):
    if tool not in MAPPING['tools']:
        raise ValueError('Unknown tool')
    result = payload.get('result', payload)
    if 'error' in payload or result.get('isError'):
        # Preserve the native error/challenge intact; never synthesize records.
        return {'canon_version': MAPPING['canon_version'], 'coverage': {'status':'unavailable'}, 'records':[], 'source_result':payload, 'blocked':True}
    data = result.get('structuredContent', result)
    if 'content' in data and 'structuredContent' not in result:
        texts = [item.get('text', '') for item in data['content'] if item.get('type') == 'text']
        if len(texts) == 1:
            try:
                data = json.loads(texts[0])
            except ValueError:
                return {'coverage': {'status':'unavailable'}, 'records':[], 'source_result':payload, 'blocked':True}
    definition = MAPPING['tools'][tool]
    if 'kind' in definition:
        return {'canon_version':MAPPING['canon_version'], 'source_result':data, 'kind':definition['kind']}
    if 'groups' in definition:
        return {'canon_version':MAPPING['canon_version'], 'source_result':data, 'groups':{k:normalize_result(v, data[k]) for k,v in definition['groups'].items() if k in data}}
    records = [normalize_record(tool, row) for row in data.get('records', [])]
    status = data.get('coverage_status', 'partial')
    if data.get('available') is False:
        status = 'unavailable'
    elif data.get('next_page') is not None or data.get('stale') or tool == 'analyze_awards':
        status = 'partial'
    total = data.get('total_matches', data.get('total'))
    if total is not None and total > len(records):
        status = 'partial' if status == 'complete' else status
    out = {'canon_version':MAPPING['canon_version'], 'dataset_id':definition['dataset_id'],
           'coverage':{'status':status, 'total_matches':total, 'returned_records':len(records),
                       'page':data.get('page'), 'page_size':data.get('page_size'), 'next_page':data.get('next_page')},
           'records':records, 'source_result':copy.deepcopy(data)}
    if tool == 'analyze_awards' and 'market' in data:
        out['groups'] = {k:normalize_result(tool, v) for k,v in data['market'].items()}
    if 'fallback_evidence' in data:
        out['fallback_groups'] = {k:normalize_result(v, data['fallback_evidence'][k]) for k,v in MAPPING['fallback_groups'].items() if k in data['fallback_evidence']}
    return out


def translate_input(tool, arguments, schemas=None):
    if schemas is None:
        schemas = json.loads((REF / 'upstream-tools.json').read_text())
    spec = next((s['inputSchema'] for s in schemas if s['name'] == tool), None)
    if spec is None:
        raise ValueError('Unknown tool')
    output = {}
    for key, value in arguments.items():
        key = MAPPING['input_aliases'].get(key, key)
        if key in output:
            raise ValueError('Duplicate alias: ' + key)
        if key in MAPPING['unsupported_filters'].get(tool, []):
            raise ValueError('Upstream does not apply filter: ' + key)
        field = spec['properties'].get(key)
        if field is None:
            raise ValueError('Unsupported filter: ' + key)
        if field.get('type') == 'string' and isinstance(value, list):
            if len(value) != 1:
                raise ValueError('Single-value upstream filter requires separate queries: ' + key)
            value = value[0]
        if field.get('type') == 'array' and isinstance(value, str):
            value = [value]
        typ = field.get('type')
        valid = (typ == 'string' and isinstance(value, str)) or (typ == 'array' and isinstance(value, list) and all(isinstance(x,str) for x in value)) or (typ == 'integer' and isinstance(value,int) and not isinstance(value,bool))
        if not valid:
            raise ValueError('Invalid type: ' + key)
        if 'enum' in field and value not in field['enum']:
            raise ValueError('Invalid enum: ' + key)
        if typ == 'integer' and not field.get('minimum',value) <= value <= field.get('maximum',value):
            raise ValueError('Out of range: ' + key)
        if typ in ('string','array') and len(value) > field.get('maxLength',field.get('maxItems',len(value))):
            raise ValueError('Too long: ' + key)
        if field.get('format') == 'date':
            dt.date.fromisoformat(value)
        if key in ('naics','psc','uei','cage'):
            value = [x.strip().upper() for x in value] if isinstance(value,list) else value.strip().upper()
        output[key] = value
    if any(k not in output for k in spec.get('required', [])):
        raise ValueError('Required arguments missing')
    if tool == 'search_awards' and not any(output.get(k) for k in ('query','naics','psc')):
        raise ValueError('Award search needs query or codes')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['input','result'])
    parser.add_argument('tool')
    parser.add_argument('file', help='JSON file, or - for stdin')
    args = parser.parse_args()
    try:
        payload = json.load(sys.stdin) if args.file == '-' else json.loads(Path(args.file).read_text())
        output = translate_input(args.tool,payload) if args.mode == 'input' else normalize_result(args.tool,payload)
        print(json.dumps(output,ensure_ascii=False,allow_nan=False,indent=2))
    except (ValueError, TypeError, KeyError) as error:
        print(str(error),file=sys.stderr)
        sys.exit(2)
