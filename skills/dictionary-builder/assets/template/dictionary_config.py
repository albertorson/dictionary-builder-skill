"""项目配置：数据位置、领域和文件名不再写死在渲染器里。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'dictionary_config.json').read_text(encoding='utf-8-sig'))
for key in ('name', 'slug', 'version'):
    if not isinstance(CONFIG.get(key), str) or not CONFIG[key].strip():
        raise ValueError(f'配置缺少非空字符串：{key}')
for key in ('slug', 'version'):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', CONFIG[key]):
        raise ValueError(f'{key} 只能包含英文字母、数字、下划线、点和连字符')
if not isinstance(CONFIG.get('domains'), dict) or not CONFIG['domains']:
    raise ValueError('domains 必须是领域标识到显示名称的非空映射')
if any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip() for k, v in CONFIG['domains'].items()):
    raise ValueError('领域标识和显示名称必须是非空字符串')


def output_name(kind, suffix):
    return f"{CONFIG['slug']}_{kind}_v{CONFIG['version']}{suffix}"
