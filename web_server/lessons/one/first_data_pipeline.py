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
    # Check for two things:
    #    Does the 'data' directory exist -> This is a good indication that the pipeline has executed at least once before. 
    #    Are there files in the data directory -> This means that pipe has definitively been executed before. 
    if os.path.exists(DATA_DIR) and (batches := sorted(os.listdir(DATA_DIR))):
	# Refer to the `save` method for filename conventions.  
        # 
        # Importantly,  ISO8061 dates sort lexicographically. In plain english this 
        # means that a simple sort avaialble in a wide variety of tools will provide consistent access 
        # to the file created by the last execution of the pipeline.
        #
        # Likewise by including the ID bounds in the file name we now have a very effective means
        # of finding the last ID.   
        pipeline_max = int(batches[-1].split('_')[2])
        # Thus for this execution the pipeline should extract the all the items after the
        # previous max until the current HackerNews max. 
        return pipeline_max, live_hn_max
    else:
        # If it is indeed the first time the pipeline has exectuted then return a range = 0.
        # This works around the cold start problem when we are performing a backfill. If
        # the pipeline began from the live max then there a two likely outcomes: 
        #    Nothing will be found as no new items have been created since the MAX_ID was requested
        #    Something with an ID > MAX_ID will be found and the pipeline will continue until nothing found
        # In either scenario our exraction method will be forced to run until failure. With this method 
        # the first execution will be empty but every execution after will use clearly defined upper and lower
        # bounds ( pipeline_max < ID <= MAX_ID). Having clear bounds is beneficial as it means that we do not
        # use WHILE construcuts with brittle exit conditions.     
        print('First extraction, falling back to API for max item.')
        return live_hn_max, live_hn_max


def extract(lower_bound: int, upper_bound: int, batch_size: int) -> t.Tuple[t.List[t.Dict], int, int]:
    items = []
    if lower_bound == upper_bound:
        print('No new items.')
        return items, lower_bound, upper_bound
    lower_bound += 1  # Shift to the the next unextracted row
    print(f'Extracting {lower_bound} -> {upper_bound}')
    for current_id in range(lower_bound, min(upper_bound + 1, upper_bound + batch_size)):
        print(f'Extracting {current_id}')
        item = requests.get(HACKERNEWS_ITEM_ENDPOINT + f'{current_id}.json')
        item.raise_for_status()
        if not item.json():
            print(f'Failed to extract {current_id}')
        items.append(item.json())
    return items, lower_bound, current_id


def save(items: t.List[t.Dict], min_id: int, max_id: int) -> None:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    ts = datetime.datetime.utcnow().isoformat()
    filename = f'{DATA_DIR}/hackernews_items_{ts}_{min_id}_{max_id}.jsonl'  # Carefully structured filename to be consisten with lexicographic sorting
    with open(filename, 'w') as fh:
        for item in items:
            line = json.dumps(item)
            # JSONL format is a collection of JSON strings separated by newlines
            fh.write(f'{line}\n')


def configure():
    parser = ap.ArgumentParser()
    parser.add_argument('--start', type=int,
                        help='HackerNews Item number to begin extraction from. If not supplied will look for max in data folder and then revert to:\n\tCURRENT_MAX')
    parser.add_argument('--batch_size', type=int, default=100, help='Number of HackerNews items to extract.')
    return parser.parse_args()



def main():
    args = configure()
    previous_max_id, max_id = get_pipeline_bounds()
    # Args.start will be None if not set.
    data, min_id, max_id = extract(args.start or previous_max_id, max_id, args.batch_size)
    save(data, min_id, max_id)


if __name__ == '__main__':
    main()
