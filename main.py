import os
import sys
from string import punctuation
from tqdm import tqdm
import re
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Collection
from colbert import Indexer, Searcher
import polars as pl
import csv
from time import time


sys.path.insert(0, "../")
import pandas as pd

os.environ["HF_DATASETS_CACHE"] = os.getcwd() + "/datasets"





def crop_before(text, crop_before=r"\nSee also ?\n"):
    return re.split(crop_before, text)[0]


def docs_from_data(data):
    wiki_heading_body_str = r"(?:(?:\n|^)((?:[A-Z]\S*)(?: \w*)* ?)(?:\n))?(.*?)(?=(?:\n|^)(?:[A-Z]\S*)(?: \w*)* ?(?:\n)|$)"
    pid = 0

    for d in data:
        title = d["title"]
        if "disambiguation" in title.lower():
            continue
        text = d["text"]
        url = d["url"]
        text = crop_before(text)

        pairs = re.findall(
            wiki_heading_body_str, text, re.DOTALL
        )  # re.DOTALL to match multiple paragraphs to the body
        for heading, body in pairs:
            if not body or body.isspace():
                continue

            full_title = f"{title}-{heading}" if heading else title

            if len(body) > 1.5 * len(full_title):
                for b in body.split("\n\n"):
                    yield pid, b, f"{full_title}", url
                    pid += 1



def get_coll(file):
    with open(file, "rb") as f:
        polars_df = (
        pl.read_csv(f.read(), n_threads=64)
        .select(["text", "heading"])
        .with_columns(pl.concat_str([pl.col("heading"), pl.col("text")], separator=" | ").alias("passage"))
        )
        data = polars_df["passage"].to_list()
        print(data[:10])
    return Collection(data = data)


index_name = f"data"


def index_data(collection):
    print(f"Loaded {len(collection):,} passages")


    nbits = 2  # encode each dimension with 2 bits
    # Indexing
    doc_maxlen = 500  # truncate passages at 300 tokens
    checkpoint = "colbert-ir/colbertv2.0"
    with Run().context(
        RunConfig(nranks=8, experiment="notebook")
    ):  # nranks specifies the number of GPUs to use.
        config = ColBERTConfig(doc_maxlen=doc_maxlen, nbits=nbits)

        indexer = Indexer(checkpoint=checkpoint, config=config)
        indexer.index(name=index_name, collection=collection, overwrite=True)
        print(
            indexer.get_index()
        )  # You can get the absolute path of the index, if needed.


def search_data(query, collection):
    print(f"#> {query}")

    with Run().context(RunConfig(experiment="notebook")):
        searcher = Searcher(index=index_name, collection=collection)

    # Find the top-3 passages for this query
    results = searcher.search(query, k=4)

    # Print out the top-k retrieved passages
    for passage_id, passage_rank, passage_score in zip(*results):
        print(
            f"\t [{passage_rank}] \t\t {passage_score:.1f} \t\t {searcher.collection[passage_id]}"
        )


if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except:
        raise Error("no path provided")

    now = time()
    collection = get_coll(path)
    print("loading took", time() - now)
    #index_data(collection)

    print("Searching...")
    now = time()
    while (input_ := input("Question: ")):
        now = time()
        search_data(input_, collection)
        later = time()
        print(later - now)
        now = later
