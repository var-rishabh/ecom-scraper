import requests


def check_proxy(proxy):
    try:
        response = requests.get(
            "https://www.google.com", proxies={"http": proxy}, timeout=5
        )
        if response.status_code == 200:
            print("🎃 ~ response:", response.url)
            return True
    except Exception as e:
        return False


def main():
    proxies_list = open("../config/proxies_list.txt", "r").read().strip().split("\n")
    working_proxies = [proxy for proxy in proxies_list if check_proxy(proxy)]

    with open("../config/proxies_list.txt", "w") as file:
        file.write("\n".join(working_proxies))


if __name__ == "__main__":
    main()
