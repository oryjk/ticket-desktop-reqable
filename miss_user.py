import random
import re

import requests


def search_shixin_users(page, rows, valCode, iname="王刚", areaid="682"):
    """
    Sends a POST request to search for shixin (失信) users.

    Args:
        page (int): The page number to request.
        rows (int): The number of rows per page.
        valCode (str): The validation code (likely a captcha).
        iname (str, optional): The name to search for. Defaults to "王刚".
        areaid (str, optional): The area ID. Defaults to "682".

    Returns:
        dict or None: The JSON response data if successful, otherwise None.
    """
    url = 'https://www.acfic.org.cn/shixin/new/SearchActionAll'

    # Headers from the curl command
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # IMPORTANT: JSESSIONID might expire or need to be obtained dynamically
        # For this example, we use the one provided. Replace if needed.
        'Cookie': 'JSESSIONID=159EE2686D8432636F444D11CD29F6C0',
        'Origin': 'https://www.acfic.org.cn',
        'Referer': 'https://www.acfic.org.cn/shixin/new/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    # Data payload - Use a dictionary, requests will handle urlencoding
    # _av9e looks like a random float, let's generate one
    data = {
        'iname': iname,
        'code': '',
        'areaid': areaid,
        'valCode': valCode,  # This is one of the variable parameters
        '_av9e': random.random(),  # Generate a random float
        'page': page,  # This is a variable parameter
        'rows': rows  # This is a variable parameter
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=data)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except ValueError as e:
        print(f"解析JSON失败: {e}")
        print(f"响应内容: {response.text if response else 'N/A'}")
        return None


def filter_users_by_age(data, target_age):
    """
    Filters the list of users by age from the response data.

    Args:
        data (dict): The JSON response data containing the 'rows' list.
        target_age (int): The age to filter by.

    Returns:
        list: A list of user dictionaries where the 'age' matches target_age.
    """
    if data is None or 'rows' not in data:
        print("提供的数据无效或不包含'rows'字段。")
        return []

    filtered_users = []
    for user in data.get('rows', []):  # Use .get with default empty list for safety
        # 'age' is a string in the JSON, convert to int for comparison
        try:
            user_age = int(user.get('age', '-1'))  # Use '-1' as default if age is missing or invalid
            cardnum = str(user.get('cardnum', '-1'))  # Use '-1' as default if age is missing or invalid

            if user_age == target_age and cardnum.startswith("513"):
                filtered_users.append(user)
        except (ValueError, TypeError):
            # Handle cases where 'age' is not a valid number string
            print(f"警告: 无法解析年龄字段: {user.get('age')} for user: {user.get('iname', 'N/A')}. 跳过此条目。")
            continue  # Skip this entry if age cannot be converted to int

    return filtered_users


# --- Example Usage ---

# --- IMPORTANT ---
# The `valCode` likely corresponds to a CAPTCHA on the website.
# You will need to find a way to obtain the correct `valCode` dynamically
# before making the request, or manually update it if testing.
# The `JSESSIONID` cookie might also expire and need updating.

# Replace with a valid valCode obtained from the website (e.g., from an image CAPTCHA)
current_val_code = "你的验证码"  # !!! 你需要替换这个为你当前的验证码 !!!
# Note: The original curl had valCode=1227, let's try using that first if you don't know how to get the current one.
# However, it's very likely this changes frequently.
current_val_code = "1227"  # Using the value from the curl example for demonstration

# Define the page number and rows per page you want to fetch
target_page = 1
target_rows = 100000

print(f"正在请求第 {target_page} 页，每页 {target_rows} 条数据...")

# Call the function to make the request
response_data = search_shixin_users(page=target_page, rows=target_rows, valCode=current_val_code)

# Check if the request was successful and data was received
if response_data:
    print(f"成功获取数据。总条数: {response_data.get('total', 'N/A')}")

    # Define the age you want to filter by
    age_to_find = 33
    print(f"\n正在过滤年龄为 {age_to_find} 的用户...")

    # Filter the results
    filtered_users = filter_users_by_age(response_data, age_to_find)

    # Print the filtered results
    if filtered_users:
        print(f"找到 {len(filtered_users)} 位年龄为 {age_to_find} 的用户:")
        for user in filtered_users:
            duty = user.get('duty', 'N/A')
            pattern = r'(\d+(?:\.\d+)?)元'
            amounts = re.findall(pattern, duty)
            print(f"  姓名: {user.get('iname', 'N/A')}, "
                  f"年龄: {user.get('age', 'N/A')}, "
                  f"身份证: {user.get('cardnum', 'N/A')}, "
                  # f"金额: {amounts}, "
                  f"金额: {user.get('duty', 'N/A')}, "
                  f"地区: {user.get('area_name', 'N/A')}, "
                  f"法院: {user.get('court_name', 'N/A')}, "
                  f"案号: {user.get('case_code', 'N/A')}")
    else:
        print(f"在当前页 ({target_page}) 未找到年龄为 {age_to_find} 的用户。")
else:
    print("未能获取数据，无法进行过滤。")

# You can repeat this process for different pages to get more results
# Example for page 2 (assuming captcha is still valid or updated)
# print("\n--- 请求第二页数据 ---")
# response_data_page2 = search_shixin_users(page=2, rows=target_rows, valCode=current_val_code) # Update valCode if needed!
# if response_data_page2:
#      print(f"成功获取数据 (第二页)。总条数: {response_data_page2.get('total', 'N/A')}")
#      filtered_users_page2 = filter_users_by_age(response_data_page2, age_to_find)
#      print(f"\n在第二页找到 {len(filtered_users_page2)} 位年龄为 {age_to_find} 的用户:")
#      for user in filtered_users_page2:
#          print(f"  姓名: {user.get('iname', 'N/A')}, 年龄: {user.get('age', 'N/A')}, ...") # Print details
# else:
#      print("未能获取第二页数据。")
