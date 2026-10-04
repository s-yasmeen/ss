from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')
replacements = {
    'MIN_TRAIN_PER_SIGN=8': 'MIN_TRAIN_PER_SIGN=6',
    'at least <b>8 training samples</b>': 'at least <b>6 training samples</b>',
    '3+ SIGNS • 8+ SAMPLES/SIGN • OFFLINE': '3+ SIGNS • 6+ SAMPLES/SIGN • OFFLINE',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'Missing expected text: {old}')
    text = text.replace(old, new)
index.write_text(text, encoding='utf-8')

sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
old_cache = "const CACHE_NAME = 'silentvoicex-accuracy-offline-v5';"
new_cache = "const CACHE_NAME = 'silentvoicex-accuracy-offline-v6';"
if old_cache in sw_text:
    sw_text = sw_text.replace(old_cache, new_cache)
elif new_cache not in sw_text:
    raise SystemExit('Unexpected service-worker cache name')
sw.write_text(sw_text, encoding='utf-8')
