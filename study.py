import concurrent.futures
import time
from concurrent.futures import Future

import requests
from requests import Response


def concurrent_requests(n: int)->list[Response]:
    """
    并发请求 n 次
    :param n:
    :return:
    """
    params = {"licence_key": "fP1wWS9c"}
    target_url = "http://match.oryjk.cn/ticket-member/match/current/fP1wWS9c"
    print(f"并发请求{target_url} 共 {n} 次")

    max_worker = 30

    with concurrent.futures.ThreadPoolExecutor(max_worker) as executor:
        futures = [
            executor.submit(requests.get, target_url, params=params) for i in range(n)
        ]
        completed_results = [ future.result() for future in concurrent.futures.as_completed(futures)]

    return completed_results

def print_result(results):
    for result in results:
        print(result.json())

if __name__ == "__main__":
    n=100
    start_time = time.time()
    completed_results = concurrent_requests(n)
    end_time = time.time()
    duration = end_time - start_time
    print_result(completed_results)
    print(f"成功请求次数 {sum(1 for r in completed_results if r.status_code == 200)}")
    print(f"并发请求共 {n} 次，耗时{duration}秒")
