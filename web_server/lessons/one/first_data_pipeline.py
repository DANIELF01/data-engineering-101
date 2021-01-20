import requests
import argparse as ap
import json
import datetime
import typing as t
import os

HACKERNEWS_ITEM_ENDPOINT = 'https://hacker-news.firebaseio.com/v0/item/'
HACKERNEWS_MAX_ITEM_ENDPOINT = 'https://hacker-news.firebaseio.com/v0/maxitem.json'
DATA_DIR = 'data'


def get_hackernews_maxitem() -> int:
    max_item = requests.get(HACKERNEWS_MAX_ITEM_ENDPOINT)
    max_item.raise_for_status()
    return max_item.json()


def get_pipeline_bounds() -> t.Tuple[int, int]:
    # Look for past extractions in data folder.
    print('Looking in data folder for last ID...')
    live_hn_max = get_hackernews_maxitem()
    if os.path.exists(DATA_DIR) and (batches := sorted(os.listdir(DATA_DIR))):
        pipeline_max = int(batches[-1].split('_')[2])
        return pipeline_max, live_hn_max
    else:
        print('First extraction, falling back to API for max item.')
        return live_hn_max, live_hn_max


def configure():
    parser = ap.ArgumentParser()
    parser.add_argument('--start', type=int,
                        help='HackerNews Item number to begin extraction from. If not supplied will look for max in data folder and then revert to:\n\tCURRENT_MAX')
    parser.add_argument('--batch_size', type=int, default=100, help='Number of HackerNews items to extract.')
    return parser.parse_args()


def extract(previous_max_id: int, max_id: int, batch_size: int) -> t.Tuple[t.List[t.Dict], int, int]:
    print(f'Previous last ID: {previous_max_id}\nCurrent max ID: {max_id}')
    items = []
    if previous_max_id == max_id:
        print('No new items.')
        return items, previous_max_id, max_id
    previous_max_id += 1  # Shift to the the next unextracted row
    print(f'Beginning extraction from: max_id = {previous_max_id}')
    for current_id in range(previous_max_id, min(max_id + 1, max_id + batch_size)):
        print(f'Extracting item {current_id}')
        item = requests.get(HACKERNEWS_ITEM_ENDPOINT + f'{current_id}.json')
        item.raise_for_status()
        if not item.json():
            print(f'Failed to extract {current_id}')
        items.append(item.json())
    return items, previous_max_id, current_id


def save(items: t.List[t.Dict], min_id: int, max_id: int) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    ts = datetime.datetime.utcnow().isoformat()
    filename = f'{DATA_DIR}/{ts}_{min_id}_{max_id}_items_hackernews.jsonl'  # Carefully structured filename to be consisten with lexicographic sorting
    with open(filename, 'w') as fh:
        for item in items:
            line = json.dumps(item)
            # JSONL format is a collection of JSON strings separated by newlines
            fh.write(f'{line}\n')


def main():
    args = configure()
    previous_max_id, max_id = get_pipeline_bounds()
    data, min_id, max_id = extract(previous_max_id, max_id, args.batch_size)
    save(data, min_id, max_id)


if __name__ == '__main__':
    main()
