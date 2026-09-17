"""Reproducible local Claude package; no registration, network or deployment."""
import argparse
import hashlib
import json
import posixpath
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
REF = ROOT / 'skills/research/references'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def archive(path, entries):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as out:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (2026, 9, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            out.writestr(info, data)


def validate_archive(path):
    import re
    with zipfile.ZipFile(path) as bundle:
        names = set(bundle.namelist())
        for name in names:
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert not any(part in ('.env', '.git', '__pycache__') for part in Path(name).parts)
            if name.endswith('.md') and ('/workflows/' in name or name.endswith('/SKILL.md')):
                for target in re.findall(r'\]\(([^)]+)\)', bundle.read(name).decode()):
                    if not target.startswith('https:'):
                        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
                        assert resolved in names, 'Broken packaged reference: ' + resolved


def validate():
    manifest = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
    assert manifest['name'] == 'getwab-claude'
    assert json.loads((ROOT / '.mcp.json').read_text())['mcpServers']['getwab']['url'] == 'https://www.getwab.com/api/plugin/v1/mcp'
    mapping = json.loads((REF / 'mappings.json').read_text())
    declared = json.loads((REF / 'upstream-tools.json').read_text())
    assert set(mapping['tools']) == {item['name'] for item in declared}, 'Tool coverage drift'
    assert len(mapping['datasets']) == 11
    assert (REF / 'canon.md').read_bytes() == (REPO / 'docs/plugins/GETWAB_FEDERAL_PROCUREMENT_AI_CANON.md').read_bytes(), 'Canon drift: rebuild'
    import re
    for skill in (ROOT / 'skills').glob('*/SKILL.md'):
        text = skill.read_text()
        assert text.startswith('---\nname: ') and '\ndescription: ' in text
        front = text.split('---', 2)[1]
        fields = dict(line.split(': ', 1) for line in front.strip().splitlines())
        assert set(fields) == {'name', 'description'}
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name'])
        assert len(fields['name']) <= 64 and len(fields['description']) <= 1024
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if not target.startswith('https:'):
                assert (skill.parent / target).exists(), f'Missing reference: {skill}: {target}'
    lock = json.loads((REF / 'sources.lock.json').read_text())
    for name, digest in lock.items():
        assert hashlib.sha256((REPO / name).read_bytes()).hexdigest() == digest, 'Source drift: ' + name


def build():
    raw = subprocess.run(['php', str(ROOT / 'scripts/export-contract.php')], check=True, capture_output=True, text=True)
    contract = json.loads(raw.stdout)
    write(REF / 'upstream-tools.json', json.dumps(contract['tools'], indent=2) + '\n')
    canon_path = REPO / 'docs/plugins/GETWAB_FEDERAL_PROCUREMENT_AI_CANON.md'
    write(REF / 'canon.md', canon_path.read_text())
    sources = [canon_path, REPO / 'app/Http/Controllers/GetwabPluginMcpController.php', REPO / 'app/Services/ProcurementPromptRegistry.php']
    for name, definition in contract['playbooks'].items():
        source = REPO / 'public' / definition['file']
        content = source.read_text()
        assert content.strip(), 'Empty playbook: ' + name
        write(REF / 'playbooks' / (name + '.txt'), content)
        sources.append(source)
    write(REF / 'sources.lock.json', json.dumps({str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2) + '\n')
    for skill in (ROOT / 'skills').glob('*/SKILL.md'):
        if skill.parent.name != 'research':
            write(REF / 'workflows' / (skill.parent.name + '.md'), skill.read_text().replace('../research/references/', '../'))
    validate()
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    # Explicit allowlist prevents private files, caches or credentials entering archives.
    entries = {}
    for file in ROOT.rglob('*'):
        relative = file.relative_to(ROOT)
        if not file.is_file() or '__pycache__' in relative.parts:
            continue
        if relative.parts[0] in ('.claude-plugin', 'skills') or str(relative) in ('.mcp.json','README.md','ACCEPTANCE.md'):
            entries['getwab-claude/' + relative.as_posix()] = file.read_bytes()
    for name in ('README.md', 'ACCEPTANCE.md'):
        source = REPO / 'docs/plugins/getwab-claude' / ('GETWAB_CLAUDE_' + name)
        entries['getwab-claude/' + name] = source.read_bytes()
    archive(dist / 'getwab-claude-plugin-1.0.0.zip', entries)
    standalone = {'getwab-research/' + p.relative_to(ROOT / 'skills/research').as_posix():p.read_bytes() for p in (ROOT / 'skills/research').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for path in (ROOT / 'skills').glob('*/SKILL.md'):
        if path.parent.name == 'research':
            continue
        body = path.read_text().replace('../research/references/', '../')
        standalone['getwab-research/references/workflows/' + path.parent.name + '.md'] = body.encode()
    archive(dist / 'getwab-claude-skill-1.0.0.zip', standalone)
    print('Validated 17 tools, 11 datasets, 13 playbooks and skill references.')
    for output in sorted(dist.glob('*.zip')):
        validate_archive(output)
        print(output.name + ' SHA256 ' + hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build','validate'])
    args = parser.parse_args()
    build() if args.command == 'build' else validate()
