#!/usr/bin/env bash
set -euo pipefail

sha=${1:?commit SHA required}
archive=${2:?asset archive required}
[[ $sha =~ ^[0-9a-f]{40}$ && $archive == "/home/frappe/crm-assets-$sha.tgz" ]] || exit 2

bench=/home/frappe/.local/bin/bench
bench_dir=/home/frappe/frappe-crm/summon-bench
app=$bench_dir/apps/crm
site=crm.localhost

cd "$app"
test -z "$(git status --porcelain)"
test "$(git remote get-url upstream)" = 'https://github.com/withsummon/crm-summon.git'
git fetch --no-tags upstream main:refs/remotes/upstream/main
test "$(git rev-parse upstream/main)" = "$sha"
git merge-base --is-ancestor HEAD "$sha"
tar -tzf "$archive" >/dev/null

cd "$bench_dir"
"$bench" --site "$site" backup

requirements=$(./env/bin/python - "$app" "$sha" <<'PY'
import re
import subprocess
import sys
import tomllib

app, sha = sys.argv[1:]
def dependencies(rev):
    content = subprocess.check_output(['git', '-C', app, 'show', f'{rev}:pyproject.toml'])
    return tomllib.loads(content.decode())['project']['dependencies']

def name(requirement):
    return re.split(r'[<=>!~;\[]', requirement, maxsplit=1)[0].strip().lower().replace('_', '-')

old = {name(requirement): requirement for requirement in dependencies('HEAD')}
print('\n'.join(requirement for requirement in dependencies(sha) if old.get(name(requirement)) != requirement))
PY
)
if [[ -n $requirements ]]; then
  while IFS= read -r requirement; do
    "$bench" pip install "$requirement"
  done <<< "$requirements"
fi

cd "$app"
git checkout --detach "$sha"
tar -xzf "$archive" -C "$app" crm/public/frontend crm/www/crm.html
cd "$bench_dir"
"$bench" --site "$site" migrate
"$bench" --site "$site" clear-cache
pm2 restart summon-crm-bench

asset=$(grep -oE '/assets/crm/frontend/assets/index-[^" ]+\.js' "$app/crm/www/crm.html" | head -n 1)
test -n "$asset"
curl -fsS --retry 12 --retry-delay 5 --retry-all-errors -o /dev/null https://crm.withsummon.com/login
curl -fsS -o /dev/null "https://crm.withsummon.com$asset"
rm -f "$archive"
echo "Deployed CRM $sha"
