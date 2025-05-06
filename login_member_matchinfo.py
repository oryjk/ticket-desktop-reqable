# API Docs: https://reqable.com/docs/capture/addons
import json
from typing import Tuple

import requests
from reqable import HttpRequest, HttpResponse, Context


def onRequest(context: Context, request: HttpRequest):
    request_url = context.url
    if "/Login/index" in request_url:
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        env_info = {
            "host": host,
            "licence_key": licence_key,
        }
        context.shared = env_info
        pass
        # return handle_get_match_info(context, request, host, licence_key)

    elif "/MiniApp/getMatchInfo" in request_url:
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        env_info = {
            "host": host,
            "licence_key": licence_key,
        }
        context.shared = env_info
        return handle_get_match_info(context, request, host, licence_key)

    elif "Open/matchList" in request_url:
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        env_info = {
            "host": host,
            "licence_key": licence_key,
        }
        context.shared = env_info
        return request

    return request


def onResponse(context: Context, response: HttpResponse):
    request_url = context.url
    if "/Login/index" in request_url:
        # host, licence_key = get_config_info(context)
        # print(f"host {host}, licence_key {licence_key}")
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        pass
        # return handle_get_match_info(context, request, host, licence_key)

    elif "/MiniApp/getMatchInfo" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_get_match_info_response(context, response)
    elif "Open/matchList" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_match_list_response(context, response, host, licence_key)
    return response


def handle_match_list_response(context: Context, response: HttpResponse, host, licence_key):
    response.body.jsonify()
    current_match_info = get_current_match(host, licence_key)
    if current_match_info.status_code == 200:
        match_data = current_match_info.json()
        match_id = match_data.get("match_id")

        if 'data' in response.body and 'match_list' in response.body['data'] and response.body['data']['match_list']:
            # 将 status 字段设置为 1
            print(response.body['data']['match_list'][0][0])
            response.body['data']['match_list'][0][0]['id'] = match_id
            print("已将 data.status 字段修改为 1")
        else:
            print("match_list为空，目前还没有比赛，赋予默认值")
            response.body = json.loads(match_list_json)
        return response
    else:
        print(f"获取比赛ID失败，状态码: {current_match_info.status_code}")
        return response


def get_current_match(host: str, licence_key: str):
    url = f"{host}/ticket-member/match/current/{licence_key}"
    print(f"获取当前比赛信息: {url}")
    current_match_info = requests.get(url)
    return current_match_info


def handle_get_match_info(context: Context, request: HttpRequest, host: str, licence_key: str):
    try:
        current_match_info = get_current_match(host, licence_key)
        if current_match_info.status_code == 200:
            match_data = current_match_info.json()
            match_id = match_data.get("match_id")

            if match_id:
                # Process the JSON body of the original request
                request.body.jsonify()
                print("match_id = " + match_id)
                request.body['id'] = match_id
                print(f"设置了比赛的id: {match_id}")
            else:
                print("API响应中没有找到id字段")
        else:
            print(f"获取比赛ID失败，状态码: {current_match_info.status_code}")

    except Exception as e:
        print(f"获取比赛ID时出错: {str(e)}")

    return request


def get_config_info(context: Context) -> Tuple[str, str]:
    host = context.env.get('host', 'http://localhost:8000')
    license_file = context.env.get('license', 'd:/license.txt')
    licence_key = get_license(license_file)
    print(f"Resolved host = {host}")  # 示例：可以保留一些关键的解析结果日志
    print(f"Resolved license_file path = {license_file}")  # 示例：可以保留一些关键的解析结果日志
    return host, licence_key


def handle_get_match_info_response(context: Context, response: HttpResponse):
    response.body.jsonify()
    if 'data' in response.body and 'sale' in response.body['data']:
        # 将 status 字段设置为 1
        response.body['data']['sale'] = 1
        print("已将 data.status 字段修改为 1")
    else:
        print("未找到 data.status 字段，无法修改")
    return response


def get_license(file_path="/Users/carlwang/temp/license.txt", default_license=None):
    """
    从本地文件读取 license key
    
    参数:
        file_path (str): license 文件路径，默认为当前目录下的 license.txt
        default_license (str): 当文件不存在或读取失败时的默认 license
    
    返回:
        str: 读取到的 license key 或默认值
    """
    try:
        with open(file_path, 'r') as file:
            license_key = file.read().strip()
            if license_key:  # 确保读取到的内容不为空
                return license_key
    except FileNotFoundError:
        print(f"License 文件 {file_path} 不存在，使用默认值")
    except Exception as e:
        print(f"读取 license 时出错: {e}")

    return default_license


match_list_json = """
{
    "code": 1,
    "data": {
        "ad": {
            "img": "",
            "href": ""
        },
        "match_list": [
            [
                {
                    "id": 44,
                    "team1_color": "rgba(202, 21, 29, 1)",
                    "team1_id": 42,
                    "team1_logo": "https://fcscdn3.k4n.cc/upload/a30/png/2024229/1.png",
                    "team1_name": "成都蓉城",
                    "team2_color": "rgba(28, 45, 103, 1)",
                    "team2_id": 50,
                    "team2_logo": "https://ss0.baidu.com/6ONWsjip0QIZ8tyhnq/it/u=3714174967,1210934582&fm=58&app=10&f=PNG?w=100&h=100&s=0300F804576004A21680299903001096",
                    "team2_name": "梅州客家",
                    "time_e": 1727616900,
                    "time_s": 1727609700,
                    "sale": 1,
                    "line_s_time": 1727416800,
                    "line_e_time": 1726292100
                }
            ]
        ]
    },
    "msg": "success",
    "page": {
        "count": 1,
        "currentPage": 1,
        "pageSize": 6
    }
}
"""
