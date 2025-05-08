import concurrent.futures
import time
from concurrent.futures import Future

import requests
from requests import Response


def concurrent_requests(n: int):
    """
    并发请求 n 次
    :param n:
    :return:
    """
    target_url = "http://match.oryjk.cn/ticket-member/match/current/fP1wWS9c?licence_key=fP1wWS9c"
    print(f"并发请求{target_url} 共 {n} 次")
    start_time = time.time()
    max_worker = 30
    results:list[Response] = []
    futures: list[Future] = []

    with concurrent.futures.ThreadPoolExecutor(max_worker) as executor:
        futures = [executor.submit(requests.get, target_url) for i in range(n)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())


    end_time = time.time()
    duration = end_time - start_time
    print(f"并发请求{target_url} 共 {n} 次，耗时{duration}秒")
    print(f"成功请求次数 {sum(1 for r in results if r.status_code == 200)}")
    for result in results:
        print(result.json())

if __name__ == '__main__':
    concurrent_requests(100)
