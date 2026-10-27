"""Bounded official archive download and reproducible local text sampling."""
from pathlib import Path
import hashlib
import json
import re
import urllib.request
import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer

ARCHIVES = [
 'CCDB_Export_5_September_2023_through_March_2024.zip',
 'CCDB_Export_6_April_2024_through_July_2024.zip',
]

def normalize(text):
    text = re.sub(r'\bx+\b', ' REDACTED ', str(text).lower())
    text = re.sub(r'\d+', ' NUM ', text)
    return re.sub(r'\s+', ' ', text).strip()

def english_like(text):
    # A transparent screening heuristic, not a validated language detector.
    words = set(re.findall(r'[a-z]+', str(text).lower()))
    return len(words & {'the','and','my','was','have','with','that','this','from','not','for'}) >= 3

def download(config, raw):
    """Read only two official historical archives; retain a tiny stable hash sample."""
    import csv, io, zipfile
    from datetime import datetime, timezone
    raw = Path(raw); raw.mkdir(parents=True, exist_ok=True)
    selected = {}; manifest = []
    for name in ARCHIVES:
        url = 'https://files.consumerfinance.gov/f/documents/' + name
        path = raw / name
        if not path.exists():
            temporary = path.with_suffix('.partial')
            urllib.request.urlretrieve(url, temporary)
            temporary.replace(path)
        counts = {'archive_rows': 0, 'scope_rows': 0, 'missing_or_short': 0,
                  'too_long': 0, 'english_heuristic_excluded': 0}
        with zipfile.ZipFile(path) as archive:
            members = [n for n in archive.namelist() if n.endswith('.csv')]
            if len(members) != 1: raise ValueError('Unexpected archive contents')
            with archive.open(members[0]) as source:
                reader = csv.DictReader(io.TextIOWrapper(source, encoding='utf-8-sig'))
                for row in reader:
                    counts['archive_rows'] += 1
                    date = row['Date received']
                    if not re.match(r'\d{4}-\d{2}-\d{2}', date):
                        date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
                    category = row['Product']; month = date[:7]
                    if month not in config['months'] or category not in config['categories']: continue
                    counts['scope_rows'] += 1
                    text = row['Consumer complaint narrative'].strip()
                    if len(text) < config['min_characters']:
                        counts['missing_or_short'] += 1; continue
                    if len(text) > config['max_characters']:
                        counts['too_long'] += 1; continue
                    if not english_like(text):
                        counts['english_heuristic_excluded'] += 1; continue
                    record = {'id': str(row['Complaint ID']), 'date': date,
                              'category': category, 'text': text}
                    key = (month, category)
                    rank = hashlib.sha256((str(config['seed']) + ':' + record['id']).encode()).hexdigest()
                    bucket = selected.setdefault(key, [])
                    bucket.append((rank, record))
                    bucket.sort(key=lambda pair: pair[0])
                    del bucket[config['per_product_month']:]
        manifest.append({'url': url, 'bytes': path.stat().st_size,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'retrieved_utc': datetime.now(timezone.utc).isoformat(), **counts})
    records = [record for key in sorted(selected) for _, record in selected[key]]
    return pd.DataFrame(records), manifest

def clean(frame, config):
    audit = {'downloaded_rows': len(frame)}
    frame = frame.sort_values(['date', 'id']).drop_duplicates('id').copy()
    audit['duplicate_ids_removed'] = audit['downloaded_rows'] - len(frame)
    valid = frame.text.fillna('').str.len() >= config['min_characters']
    audit['missing_or_short_removed'] = int((~valid).sum())
    frame = frame[valid].copy()
    frame['normalized'] = frame.text.map(normalize)
    before = len(frame); frame = frame.drop_duplicates('normalized')
    audit['exact_normalized_duplicates_removed'] = before - len(frame)
    frame = frame.reset_index(drop=True)
    # A fixed, nonlearned representation removes near copies across all time splits.
    # Keep the earliest representative, so future examples never replace training rows.
    vector = HashingVectorizer(analyzer='char_wb', ngram_range=(3,5), n_features=2**18, alternate_sign=False)
    features = vector.transform(frame.normalized)
    retained = []
    for i in range(len(frame)):
        similarities = features[i] @ features[retained].T if retained else None
        if similarities is None or similarities.max() < config['near_duplicate_cosine']:
            retained.append(i)
    audit['near_duplicates_removed'] = len(frame) - len(retained)
    frame = frame.iloc[retained].copy()
    frame['split'] = 'development'
    frame.loc[frame.date < config['train_before'], 'split'] = 'train'
    frame.loc[frame.date >= config['test_from'], 'split'] = 'test'
    audit['retained_rows'] = len(frame)
    audit['split_counts'] = frame.groupby(['split','category']).size().unstack(fill_value=0).to_dict('index')
    for split in ['train', 'development', 'test']:
        if set(frame[frame.split == split].category) != set(config['categories']):
            raise ValueError(f'Insufficient category coverage in {split}; do not fabricate data')
    return frame, audit
