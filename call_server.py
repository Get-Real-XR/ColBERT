import requests
import json
from time import time

def search_api(query, k=2):
    base_url = "http://localhost:8893/api/search"
    params = {
                'query': query,
                    'k': k
                    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        results = json.loads(response.text)
        query_result = results.get("query")
        topk_results = results.get("topk")
        
        print(f"Query: {query_result}\n")
        for rank, result in enumerate(topk_results, 1):
            pid = result.get("pid")
            prob = result.get("prob")
            score = result.get("score")
            text = result.get("text")
            print(f"Rank {rank}: (PID: {pid}, Probability: {prob}, Score: {score})\n{text}\n")
        else:
            print(f"reponse: {response.status_code}")


if __name__ == "__main__":
    num = input("k: ")
    while True:
        query = input("Query: ")
        search_api(query, k=num)


