from concurrent.futures import ThreadPoolExecutor
import requests
import time


def check_proxy(proxy):
    try:
        response = requests.get(
            "https://www.google.com", proxies={"http": proxy}
        )
        if response.status_code == 200:
            print(f"🟢 ~ Working: {response.status_code} | {proxy}")
            return proxy
        else:
            print(f"🔴 ~ Not Working: {response.status_code} | {proxy}")
            return
    except Exception as e:
        return False


def main():
    proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=20) as executor:
        working_proxies = list(executor.map(check_proxy, proxies_list))
        # working_proxies = [proxy for proxy in proxies_list if check_proxy(proxy)]

    stop = time.perf_counter()
    
    print(f"Finished in {round(stop - start, 2)} second(s)")

    with open("config/proxies_list.txt", "w") as file:
        file.write("\n".join(working_proxies))


if __name__ == "__main__":
    main()
