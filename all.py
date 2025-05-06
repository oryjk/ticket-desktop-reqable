# API Docs: https://reqable.com/docs/capture/addons

from reqable import *
import requests
import json
from urllib.parse import urlparse
import uuid
import sys
import socket

# server_url="https://oryjk.cn:82/ticket-monitor/backend/api"
server_url = "http://127.0.0.1:5689/api"


def onRequest(context, request):
    """
    拦截请求并在请求发送前处理。
    根据请求URL路径执行不同的逻辑。
    """

    # 只获取路径部分，通常是 host 后面的部分
    # reqable 的 request 对象也包含 url 属性，它是一个字符串
    request_url = context.url  # request.url 通常是完整的 URL

    # 可以使用 urllib.parse 来更精确地解析 URL 路径
    parsed_url = urlparse(request_url)
    request_path = parsed_url.path  # 获取路径部分，例如 /Login/index

    print(f"Intercepting request to: {request_url}")
    print(f"Request path: {request_path}")

    # 根据路径关键字执行不同的逻辑
    if "/Login/index" in request_path:
        print("Detected Login/index path.")
        handle_login_index(context, request)
    elif "/Member/getCrewsList" in request_path:
        print("Detected Member/getCrewsList path.")
        handle_get_crews_list(context, request)
    elif "/MatchCon/createMatchOrder" in request_path:
        print("Detected MatchCon/createMatchOrder path.")
        return handle_create_match_order(context, request)
    elif "/MiniApp/getMatchInfo" in request_path:
        print("Detected MiniApp/getMatchInfo path.")
        handle_get_match_info(context, request)
    else:
        print(f"Detected other path.{request_url}")
        handle_other_requests(context, request)  # 或者不做任何处理，直接返回 request

    # 最后返回 request 对象，Reqable 会继续发送这个请求
    # 如果你想阻止请求发送，可以返回 None 或抛出异常 (取决于 Reqable 的具体要求)
    return request


def onResponse(context, response):
    """
    拦截响应并在响应发送给客户端前处理。
    根据请求URL路径（或响应内容）执行不同的逻辑。
    """
    # 在 onResponse 中获取请求的路径，可以通过 context.url 或者 context 中存储的属性
    request_url = context.url  # context 在 onResponse 中也可用，包含请求信息
    parsed_url = urlparse(request_url)
    request_path = parsed_url.path

    print(f"Intercepting response for: {request_url}")
    print(f"Request path for this response: {request_path}")

    # 根据请求路径关键字执行不同的响应处理逻辑
    if "/Login/index" in request_path:
        print("onResponse: Detected Login/index path.")
        handle_login_index_response(context, response)
    elif "/Member/getCrewsList" in request_path:
        print("onResponse: Detected Member/getCrewsList path.")
        handle_get_crews_list_response(context, response)
    elif "/MatchCon/createMatchOrder" in request_path:
        print("onResponse: Detected MatchCon/createMatchOrder path.")
        handle_create_match_order_response(context, response)
    elif "/MiniApp/getMatchInfo" in request_path:
        print("onResponse: Detected MiniApp/getMatchInfo path.")
        handle_get_match_info_response(context, response)
    else:
        print(f"onResponse: Detected other path.{request_url}")
        handle_other_responses(context, response)  # 或者不做任何处理，直接返回 response

    # 最后返回 response 对象，Reqable 会继续发送这个响应给客户端
    # 如果你想阻止响应发送，可以返回 None 或抛出异常 (取决于 Reqable 的具体要求)
    return response


# 定义处理不同路径的函数
# 这些函数接收 context 和 request 对象
def handle_login_index(context, request):
    # 在这里写处理 /Login/index 请求的逻辑
    print("handle_login_index 开始执行")
    request.body.jsonify()
    code = request.body["code"]
    context.shared = code
    print("handle_login_index 执行完毕")
    # 例如：修改请求头，修改请求体等
    # request.headers["X-Custom-Header"] = "Login"
    # request.body = b"new login body"
    pass  # 占位符，实际编写你的逻辑


def handle_get_crews_list(context, request):
    print("handle_get_crews_list 开始执行")
    lid2 = request.queries.toDict()["lid2"]
    context.shared = lid2
    print("handle_get_crews_list 执行完毕")
    pass  # 占位符


def get_auth_header(request):
    """从请求中获取授权头，如果不存在则打印错误日志并返回None"""
    auth_header = request.headers["Authorization"]
    if not auth_header:
        print("错误: 未找到Authorization头，无法继续请求")
        print("请确保原始请求包含有效的Authorization头")
        return None
    return auth_header


def fetch_match_order_list(lid2, auth_header, page):
    """请求匹配订单列表"""
    match_order_url = (
        f"https://fccdn1.k4n.cc/fc/wx_api/v1/MatchOrder/matchOrderList?lid2={lid2}"
    )
    match_order_headers = {
        "Host": "fccdn1.k4n.cc",
        "Connection": "keep-alive",
        "xweb_xhr": "1",
        "Authorization": auth_header,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.10(0x13080a11) XWEB/1227",
        "Content-Type": "application/json;charset:utf-8;",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wxffa42ecd6c0e693d/75/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    match_order_data = {
        "page": {"current": page, "currentPage": 1, "pageSize": 6, "status": "loading"}
    }

    try:
        print(f"正在请求匹配订单列表: {match_order_url}")
        match_order_response = requests.post(
            match_order_url,
            json=match_order_data,
            headers=match_order_headers,
            verify=False,
        )

        print(f"匹配订单列表响应状态码: {match_order_response.status_code}")
        if match_order_response.status_code == 200:
            # print(f"匹配订单列表响应内容: {truncate_text(match_order_response.text)}") #如果truncate_text是自定义的，请确认它已定义，或者移除此行
            response_json = match_order_response.json()
            if response_json and "data" in response_json:
                order_data_list = []
                for order in response_json["data"]:
                    order_info = {
                        "order_id": order.get("order_id", "N/A"),
                        "id": order.get("id", "N/A"),
                        "match_id": order.get("match_id", "N/A"),
                        "count_bill": order.get("count_bill", "N/A"),
                        "payable": order.get("payable", "N/A"),
                        "status": order.get("status", "N/A"),
                        "create_time": order.get("create_time", "N/A"),
                    }
                    order_data_list.append(order_info)
                return order_data_list
            else:
                print("响应中没有 'data' 字段或响应为空。")
                return []
        else:
            print(f"获取匹配订单列表失败: {match_order_response.text}")
            return []

    except requests.RequestException as e:
        print(f"请求匹配订单列表时发生错误: {e}")
        return None


def checkout_order_list(lid2, auth_header):
    unpay_order_list = fetch_match_order_list(lid2, auth_header, 2)

    if unpay_order_list:
        print("打印待支付订单列表:")
        for order in unpay_order_list:
            print(
                f"订单ID: {order['order_id']}\n"
                f"ID: {order['id']}\n"
                f"Match ID: {order['match_id']}\n"
                f"Count Bill: {order['count_bill']}\n"
                f"Payable: {order['payable']}\n"
                f"Status: {order['status']}\n"
                f"Create Time: {order['create_time']}"
            )
    else:
        print("未能获取匹配订单数据。")

    pending_order_list = fetch_match_order_list(lid2, auth_header, 3)
    print("打印待完成订单列表:")
    if pending_order_list:
        for order in pending_order_list:
            print(
                f"订单ID: {order['order_id']}\n"
                f"ID: {order['id']}\n"
                f"Match ID: {order['match_id']}\n"
                f"Count Bill: {order['count_bill']}\n"
                f"Payable: {order['payable']}\n"
                f"Status: {order['status']}\n"
                f"Create Time: {order['create_time']}"
            )
    else:
        print("未能获取匹配订单数据。")

    complete_order_list = fetch_match_order_list(lid2, auth_header, 4)
    print("打印已完成订单列表:")
    if complete_order_list:
        for order in complete_order_list:
            print(
                f"订单ID: {order['order_id']}\n"
                f"ID: {order['id']}\n"
                f"Match ID: {order['match_id']}\n"
                f"Count Bill: {order['count_bill']}\n"
                f"Payable: {order['payable']}\n"
                f"Status: {order['status']}\n"
                f"Create Time: {order['create_time']}"
            )
    else:
        print("未能获取匹配订单数据。")


def handle_create_match_order(context, request):
    # 在这里写处理 /MatchCon/createMatchOrder 请求的逻辑
    print("handle_create_match_order 开始执行")

    lid2 = request.queries.toDict()["lid2"]
    auth_header = get_auth_header(request)
    if not auth_header:
        print("错误: 无法获取授权头，停止后续请求")
        return None

    print(auth_header)

    try:
        body = request.body.payload
        body_json = json.loads(body)
        user_id = str(body_json["users"][0]["id"])
        data = {
            "orderPayload": body,
            "orderId": user_id
            + "|"
            + body_json["id"]
            + "|"
            + body_json["regions"][0]["name"],
            "matchId": body_json["id"],
            "userAgent": request.headers["User-Agent"],
            "referer": request.headers["referer"],
        }
        json_data = json.dumps(data)
        print("发送的订单请求体:" + json_data)
        headers = {"Content-Type": "application/json"}
        url = f"{server_url}/order/createSimpleOrderByReqable/{lid2}"
        try:
            requests.post(url, data=json_data, headers=headers, verify=False)
        except requests.RequestException as e:
            print(f"请求发生错误：{e}")

    except Exception as e:
        print(f"Error processing response body: {e}")
    # return request
    # 请求未支付订单
    # checkout_order_list(lid2, auth_header)
    print("handle_create_match_order 执行完毕")
    # None
    request


def handle_get_match_info(context, request):
    # 在这里写处理 /MiniApp/getMatchInfo 请求的逻辑
    # https://oryjk.cn:82/ticket-monitor/backend/api
    print("handle_get_match_info 开始执行")
    try:
        current_match_info = requests.get(
            f"{server_url}/schedule/current",
            verify=False,
        )
        if current_match_info.status_code == 200:
            match_data = current_match_info.json()
            match_id = match_data.get("matchId")

            if match_id:
                # Process the JSON body of the original request
                request.body.jsonify()
                print("match_id = " + match_id)
                request.body["id"] = match_id
                print(f"设置了比赛的id: {match_id}")
            else:
                print("API响应中没有找到 match id字段")
        else:
            print(f"获取比赛ID失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"获取比赛ID时出错: {str(e)}")

    print("handle_get_match_info 执行完毕")
    pass  # 占位符


def handle_other_requests(context, request):
    # 在这里写处理其他路径请求的逻辑
    print("Executing logic for other requests...")
    pass  # 占位符


# 注意：reqable 脚本可能不支持所有标准的 Python 库或模块。
# urllib.parse 通常是可以使用的。
# 如果需要更复杂的解析或操作，请查阅 Reqable 的脚本开发文档。


# ----- 处理不同路径的响应函数 -----


def handle_login_index_response(context, response):
    # 在这里写处理 /Login/index 响应的逻辑
    print("handle_login_index_response 开始执行")
    response.body.jsonify()
    token = response.body["token"]
    uid = response.body["info"]["id"]
    print("token:" + token)
    print("uid:" + str(uid))
    print("code:" + context.shared)
    mac_id = get_hostname()
    print("mac_id:" + mac_id)
    data = {
        "token": token,
        "userId": uid,
        "loginCode": context.shared,
        "machineId": mac_id,
    }

    json_data = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    url = f"{server_url}/order/createUserInfo"
    try:
        # 发送 POST 请求，将 JSON 数据作为请求体发送
        requests.post(url, data=json_data, headers=headers, verify=False)
        print("handle_login_index_response 执行成功！")
    except requests.RequestException as e:
        print(f"handle_login_index_response 请求发生错误：{e}")
    pass


def handle_get_crews_list_response(context, response):
    print("handle_get_crews_list_response 开始执行")
    try:
        response.body.jsonify()
        data = response.body["data"]
        json_data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        url = f"{server_url}/order/bindUserMember/" + context.shared
        try:
            # 发送 POST 请求，将 JSON 数据作为请求体发送
            requests.post(url, data=json_data, headers=headers, verify=False)
            print("handle_get_crews_list_response 执行成功！")
        except requests.RequestException as e:
            print(f"handle_get_crews_list_response 请求发生错误：{e}")

    except Exception as e:
        print(f"Error processing response body: {e}")
    pass


def handle_create_match_order_response(context, response):
    # 在这里写处理 /MatchCon/createMatchOrder 响应的逻辑
    print("handle_create_match_order_response 开始执行")

    print("handle_create_match_order_response 执行完毕")
    pass


def handle_get_match_info_response(context, response):
    # 在这里写处理 /MiniApp/getMatchInfo 响应的逻辑
    print("handle_get_match_info_response 开始执行")
    if response.code != 200:
        print("handle_get_match_info_response 执行完毕")
        return
    response.body.jsonify()
    if "data" in response.body and "sale" in response.body["data"]:
        # 将 status 字段设置为 1
        response.body["data"]["sale"] = 1
        print("已将 data.status 字段修改为 1")
    else:
        print("未找到 data.status 字段，无法修改")

    print("handle_get_match_info_response 执行完毕")
    pass


def handle_other_responses(context, response):
    # 在这里写处理其他路径响应的逻辑
    print("Executing logic for other responses...")
    pass


def get_hostname():
    """
    获取本机主机名。
    """
    try:
        return socket.gethostname()
    except Exception as e:
        print(f"Error getting hostname: {e}")
        return "unknown_host"


def get_mac_address():
    """
    获取本机的 MAC 地址。

    Returns:
        str: 格式化为 'XX:XX:XX:XX:XX:XX' 的 MAC 地址字符串，
             如果无法获取或获取到无效地址，则可能返回 None 或抛出异常
             (取决于 uuid.getnode 的行为)。
    """
    try:
        # uuid.getnode() 尝试获取机器的 MAC 地址，返回一个整数
        # 注意：在某些系统或虚拟环境中，它可能返回一个固定的值，
        # 或者无法获取真实的物理网卡 MAC 地址。
        # 也可能返回 None 或抛出异常，具体行为取决于 Python 版本和操作系统。
        mac_int = uuid.getnode()

        # uuid.getnode() 返回的是一个 48 位的整数
        # 需要将其转换为十六进制字符串，然后格式化为 MAC 地址的常见形式

        # 检查获取的整数是否是典型的无效值 (如全零)
        # 0x010000000000 是一个常用的无效值，表示无法获取
        if mac_int == 0x010000000000 or mac_int == 0:
            print(
                "Warning: uuid.getnode() returned a potentially invalid MAC address (e.g., all zeros or cannot obtain)."
            )
            # 返回 None 或者抛出异常，根据你的需求决定
            return None

        # 将整数转换为12位的十六进制字符串
        mac_hex = "{:012x}".format(mac_int)

        # 每两个字符插入一个冒号
        mac_address = ":".join(mac_hex[i : i + 2] for i in range(0, 12, 2))

        return mac_address

    except Exception as e:
        print(f"An error occurred while trying to get MAC address: {e}")
        # 捕获可能的异常，例如权限问题或底层库错误
        return None  # 获取失败时返回 None


def get_mac_address_python():
    """
    尝试获取本机的 MAC 地址。
    使用 uuid.getnode()，可能返回 None 或无效地址。
    返回 Result<Option<str>, str> 的等价结构 (用元组表示)。
    (成功获取地址，地址字符串) 或 (成功获取但无地址，None) 或 (失败，错误信息)
    """
    try:
        mac_int = uuid.getnode()

        # 检查获取的整数是否是典型的无效值
        # uuid.getnode() 文档提到 0x010000000000 表示无法获取
        if mac_int == 0x010000000000 or mac_int == 0:
            print(
                "Warning: uuid.getnode() returned a potentially invalid MAC address (e.g., all zeros or cannot obtain)."
            )
            # 等价于 Rust 中的 Ok(None)
            return (True, None)  # 成功获取函数执行完毕，但没找到有效地址

        mac_hex = "{:012x}".format(mac_int)

        # 检查十六进制字符串是否全零 (另一种无效情况)
        if all(c == "0" for c in mac_hex):
            print("Warning: uuid.getnode() returned all zeros in hex format.")
            return (True, None)  # 成功获取函数执行完毕，但没找到有效地址

        mac_address = ":".join(mac_hex[i : i + 2] for i in range(0, 12, 2))

        # 等价于 Rust 中的 Ok(Some(mac_address))
        return (True, mac_address)  # 成功获取函数执行完毕，并找到了有效地址

    except Exception as e:
        print(f"An error occurred while trying to get MAC address: {e}")
        # 等价于 Rust 中的 Err(e.to_string())
        return (False, str(e))  # 函数执行失败，返回错误信息


def get_machine_id_python():
    """
    根据主机名和 MAC 地址生成一个机器标识符。
    等价于 Rust 中的 get_machine_id 方法。
    """
    hostname = get_hostname()
    print(f"Python backend: Hostname: {hostname}")

    # 调用获取 MAC 地址的方法
    mac_addr_result = get_mac_address_python()

    # 处理获取 MAC 地址的结果 (使用元组结构模拟 Result<Option<String>, String>)
    is_success, data = mac_addr_result

    if is_success:
        # 对应 Rust 的 Ok 分支
        if data is not None:
            # 对应 Rust 的 Ok(Some(mac))
            mac = data  # data 现在是 MAC 地址字符串
            mac_string_no_colons = mac.replace(":", "")  # 格式化 MAC 地址 (去除冒号)
            machine_id_str = f"{hostname}-{mac_string_no_colons}"
            print(
                f"Python backend: Generated machine ID: {machine_id_str} (from hostname and MAC)"
            )
            return machine_id_str  # 返回成功结果
        else:
            # 对应 Rust 的 Ok(None)
            print("Python backend: No suitable MAC address found.")
            # Fallback: Use hostname only
            fallback_id = f"{hostname}-NOMAC"
            print(f"Python backend: Generated fallback ID: {fallback_id}")
            return fallback_id  # 返回 fallback 结果
    else:
        # 对应 Rust 的 Err(e)
        error_message = data  # data 现在是错误信息字符串
        print(
            f"Python backend: Failed to get MAC address: {error_message}",
            file=sys.stderr,
        )  # 打印到标准错误
        # Fallback: Use hostname only
        fallback_id = f"{hostname}-MACERROR"
        print(f"Python backend: Generated fallback ID: {fallback_id}")
        return fallback_id  # 返回 fallback 结果
