# API Docs: https://reqable.com/docs/capture/addons
import json
import socket
from typing import Tuple

import requests
from reqable import HttpRequest, HttpResponse, Context  # type: ignore

headers = {"Content-Type": "application/json"}


def onRequest(context: Context, request: HttpRequest):
    request_url = context.url
    if "/Login/index" in request_url:
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        request.body.jsonify()
        env_info = {
            "host": host,
            "licence_key": licence_key,
            "code": request.body["code"],
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
            "lid2": request.queries["lid2"],
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
    elif "getBillRegion" in request_url:
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        env_info = {
            "host": host,
            "licence_key": licence_key,
        }
        context.shared = env_info
        return request

    elif "/MatchCon/createMatchOrder" in request_url:
        print("Detected MatchCon/createMatchOrder path.")
        host, licence_key = get_config_info(context)
        print(f"host {host}, licence_key {licence_key}")
        env_info = {
            "host": host,
            "licence_key": licence_key,
        }
        context.shared = env_info
        return handle_create_match_order_to_deno(context, request)

    return request


def get_auth_header(request):
    """从请求中获取授权头，如果不存在则打印错误日志并返回None"""
    auth_header = request.headers["Authorization"]
    if not auth_header:
        print("错误: 未找到Authorization头，无法继续请求")
        print("请确保原始请求包含有效的Authorization头")
        return None
    return auth_header


def handle_create_match_order_to_deno(context, request):
    # 在这里写处理 /MatchCon/createMatchOrder 请求的逻辑
    print("handle_create_match_order_to_deno 开始执行")

    lid2 = request.queries.toDict()["lid2"]
    auth_header = get_auth_header(request)
    if not auth_header:
        print("错误: 无法获取授权头，停止后续请求")
        return None

    host = context.shared["host"]
    licence_key = context.shared["licence_key"]

    try:
        current_match_info = get_current_match(host, licence_key)
        match_data = current_match_info.json()
        match_id = match_data.get("match_id")

        body = request.body.payload
        body_json = json.loads(body)
        body_json["id"]=match_id
        user_id = str(body_json["users"][0]["id"])
        region = body_json["regions"][0]["name"]
        order_id = user_id + "|" + match_id + "|" + region

        data = {
            "orderPayload": json.dumps(body_json),
            "orderId": order_id,
            "matchId": match_id,
            "userAgent": request.headers["User-Agent"],
            "referer": request.headers["referer"],
        }

        json_data = json.dumps(data)
        url = f"{host}/ticket-member/order/createSimpleOrderByReqable/{lid2}"
        try:
            requests.post(
                url,
                data=json_data,
                headers=headers,
                verify=False,
                params={"licence_key": licence_key},
            )
        except requests.RequestException as e:
            print(f"请求发生错误：{e}")

    except Exception as e:
        print(f"Error processing response body: {e}")
    # return request
    # 请求未支付订单
    # checkout_order_list(lid2, auth_header)
    print("handle_create_match_order 执行完毕")
    return None
    # request


def handle_login_index_response(context, response):
    print("handle_login_index_response 开始执行")
    response.body.jsonify()

    token = response.body["token"]
    print("token:" + token)

    uid = response.body["info"]["id"]
    realname = response.body["info"]["realname"]
    print("uid:" + str(uid))

    code = context.shared["code"]
    print("code:" + code)
    host = context.shared["host"]

    licence_key = context.shared["licence_key"]
    machine_id = socket.gethostname()
    data = {
        "token": token,
        "userId": uid,
        "loginCode": code,
        "machineId": machine_id,
        "licenseKey": licence_key,
        "realname": realname,
    }

    json_data = json.dumps(data)

    try:
        url = f"{host}/ticket-member/order/createUserInfo"
        requests.post(
            url,
            params={"licence_key": licence_key},
            data=json_data,
            headers=headers,
            verify=False,
        )
        print("handle_login_index_response 执行成功！")
    except requests.RequestException as e:
        print(f"handle_login_index_response 请求发生错误：{e}")

    return response


def handle_get_crews_list_response(context, response, host, licence_key):
    print("handle_get_crews_list_response 开始执行")
    try:
        response.body.jsonify()
        data = response.body["data"]
        json_data = json.dumps(data)
        url = f"{host}/ticket-member/order/bindUserMember"
        try:
            # 发送 POST 请求，将 JSON 数据作为请求体发送
            requests.post(
                url,
                params={"licence_key": licence_key},
                data=json_data,
                headers=headers,
                verify=False,
            )
            print("handle_get_crews_list_response 执行成功！")
        except requests.RequestException as e:
            print(f"handle_get_crews_list_response 请求发生错误：{e}")

    except Exception as e:
        print(f"Error processing response body: {e}")
    pass


def onResponse(context: Context, response: HttpResponse):
    request_url = context.url
    if "/Login/index" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_login_index_response(context, response)

    elif "/Member/getCrewsList" in request_url:
        host, licence_key = get_config_info(context)
        handle_get_crews_list_response(context, response, host, licence_key)

    elif "/MiniApp/getMatchInfo" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        lid2 = context.shared["lid2"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_get_match_info_response(
            context, response, host, licence_key, lid2
        )
    elif "Open/matchList" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_match_list_response(context, response, host, licence_key)
    elif "getBillRegion" in request_url:
        host = context.shared["host"]
        licence_key = context.shared["licence_key"]
        print(f"onResponse {request_url} host {host}, licence_key {licence_key}")
        return handle_match_region_response(context, response, host, licence_key)

    return response


def handle_match_list_response(
    context: Context, response: HttpResponse, host, licence_key
):
    current_match_info = get_current_match(host, licence_key)
    if current_match_info.status_code == 200:
        match_data = current_match_info.json()
        match_id = match_data.get("match_id")

        if (
            "data" in response.body
            and "match_list" in response.body["data"]
            and response.body["data"]["match_list"]
        ):
            # 将 status 字段设置为 1
            response.body["data"]["match_list"][0][0]["id"] = match_id
            print("已将 data.status 字段修改为 1")
        else:
            print("match_list为空，目前还没有比赛，赋予默认值")
            url = f"{host}/ticket-member/match/default/matchList"
            current_match_list = requests.get(
                url, params={"licence_key": licence_key}, verify=False
            )
            # print(f"current_match_info: {current_match_list.json()}")
            response.body = current_match_list.json()

        return response
    else:
        print(f"获取比赛ID失败，状态码: {current_match_info.status_code}")
        return response


def handle_match_region_response(
    context: Context, response: HttpResponse, host, licence_key
):
    current_match_info = get_current_match(host, licence_key)
    if current_match_info.status_code == 200:
        if "btn_status" in response.body and response.body["btn_status"] == 1:
            print("可以获取到比赛座位信息，直接返回")
            return response
        else:
            print("region 为空，目前还没有比赛，赋予默认值")
            url = f"{host}/ticket-member/match/default/region"
            region_json = requests.get(
                url, params={"licence_key": licence_key}, verify=False
            )
            if region_json.status_code==200:
                response.body = region_json.json()


        return response
    else:
        print(f"获取比赛ID失败，状态码: {current_match_info.status_code}")
        return response


def get_current_match(host: str, licence_key: str):
    url = f"{host}/ticket-member/match/current/{licence_key}"
    print(f"获取当前比赛信息: {url}")
    current_match_info = requests.get(
        url, params={"licence_key": licence_key}, verify=False
    )
    return current_match_info


def handle_get_match_info(
    context: Context, request: HttpRequest, host: str, licence_key: str
):
    try:
        current_match_info = get_current_match(host, licence_key)
        if current_match_info.status_code == 200:
            match_data = current_match_info.json()
            match_id = match_data.get("match_id")

            if match_id:
                # Process the JSON body of the original request
                request.body.jsonify()
                print("match_id = " + match_id)
                request.body["id"] = match_id
                print(f"设置了比赛的id: {match_id}")
            else:
                print("API响应中没有找到id字段")
        else:
            print(f"获取比赛ID失败，状态码: {current_match_info.status_code}")

    except Exception as e:
        print(f"获取比赛ID时出错: {str(e)}")

    return request


def get_config_info(context: Context) -> Tuple[str, str]:
    host = context.env.get("host", "http://localhost:8000")
    license_file = context.env.get("license", "d:/license.txt")
    licence_key = get_license(license_file)
    print(f"Resolved host = {host}")  # 示例：可以保留一些关键的解析结果日志
    print(
        f"Resolved license_file path = {license_file}"
    )  # 示例：可以保留一些关键的解析结果日志
    return host, licence_key


def handle_get_match_info_response(
    context: Context, response: HttpResponse, host, licence_key, lid2
):
    if response.code != 200:
        url = f"{host}/ticket-member/match/default/matchInfo?lid2={lid2}"
        current_match_info = requests.get(
            url, params={"licence_key": licence_key}, verify=False
        )

        if current_match_info.status_code == 200:
            response.body = current_match_info.json()

        # response.body = json.loads(default_match_info)


    response.body.jsonify()
    if "data" in response.body and "sale" in response.body["data"]:
        # 将 status 字段设置为 1
        response.body["data"]["sale"] = 1
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
        with open(file_path, "r") as file:
            license_key = file.read().strip()
            if license_key:  # 确保读取到的内容不为空
                return license_key
    except FileNotFoundError:
        print(f"License 文件 {file_path} 不存在，使用默认值")
    except Exception as e:
        print(f"读取 license 时出错: {e}")

    return default_license


