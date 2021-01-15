import requests
import argparse as ap
import json
import datetime
import typing as t

HACKERNEWS_ITEM_ENDPOINT = 'https://hacker-news.firebaseio.com/v0/item/'

def configure():
    parser = ap.ArgumentParser()
    parser.add_argument('--start', type=int, default=1, help='HackerNews Item number to begin extraction from.')
    parser.add_argument('--batch_size', type=int,  default=500, help='Number of HackerNews items to extract.')
    return parser.parse_args()


def extract(start : int, batch_size : int) -> t.List[t.Dict] :
    end = start + batch_size - 1 # Remember item {START} will be retrieved
    items = []
    for i in range(start, end):
        item = requests.get(HACKERNEWS_ITEM_ENDPOINT + f'{i}.json')
        items.append(item.json())
    return items


def save(items : t.List[t.Dict]) -> None:
    ts = datetime.datetime.utcnow().isoformat()
    filename = f'{ts}-items_hackernews.jsonl'
    with open(filename, 'w') as fh:
        for item in items:
            line = json.dumps(item)
            # JSONL format is a collection of JSON strings separated by newlines
            fh.write(f'{line}\n')



def main():
    args = configure()
    data = extract(args.start, args.batch_size)
    save(data)



if __name__ == '__main__':
    main()

