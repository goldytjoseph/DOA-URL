import argparse
import aiohttp
import asyncio
import random
from urllib.parse import urlparse
import queue
import threading

def colored(text, color):
    colors = {"green": "\033[92m", "red": "\033[91m", "reset": "\033[0m"}
    return f"{colors[color]}{text}{colors['reset']}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]

def get_random_user_agent():
    return {"User-Agent": random.choice(USER_AGENTS)}

def save_to_file(file, url):
    if file:
        with open(file, "a") as f:
            f.write(f"{url}\n")

def generate_urls(target):
    target = target.strip()
    if not target:
        return []
    parsed = urlparse(target)
    return [target] if parsed.scheme else [f"http://{target}", f"https://{target}"]

async def check_url(session, url, method, live_file, dead_file):
    headers = get_random_user_agent()
    try:
        async with session.request(method, url, timeout=3, headers=headers) as response:
            result = f"[+] {url} is accessible ({response.status})"
            print(colored(result, "green"))
            save_to_file(live_file, url)
    except Exception as e:
        result = f"[-] {url} is not accessible ({str(e)})"
        print(colored(result, "red"))
        save_to_file(dead_file, url)

async def process_queue(queue, method, live_file, dead_file):
    async with aiohttp.ClientSession() as session:
        while not queue.empty():
            target = queue.get()
            urls = generate_urls(target)
            tasks = [check_url(session, url, method, live_file, dead_file) for url in urls]
            await asyncio.gather(*tasks)
            queue.task_done()

def start_async_processing(targets, method, live_file, dead_file, max_workers):
    url_queue = queue.Queue()
    for target in targets:
        url_queue.put(target)
    
    threads = []
    for _ in range(max_workers):
        thread = threading.Thread(target=lambda: asyncio.run(process_queue(url_queue, method, live_file, dead_file)))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

def main():
    parser = argparse.ArgumentParser(description="Simple HTTP probe tool")
    parser.add_argument("target", nargs="?", help="Single IP/Domain to check")
    parser.add_argument("-f", "--file", help="File containing list of IPs/Domains")
    parser.add_argument("-m", "--method", default="GET", help="Request method, such as GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD")
    parser.add_argument("-l", "--live", help="File to save live domains")
    parser.add_argument("-d", "--dead", help="File to save dead domains")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    
    args = parser.parse_args()
    targets = []
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as file:
                targets = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(colored(f"[-] Error: File not found - {args.file}", "red"))
            return
        except Exception as e:
            print(colored(f"[-] Error reading file: {str(e)}", "red"))
            return
    elif args.target:
        targets.append(args.target)
    
    if not targets:
        print("Usage: python3 DOA.py [target] or python3 DOA.py -f file.txt [-m METHOD] [-t THREADS] [-l live.txt] [-d dead.txt]")
        return
    
    start_async_processing(targets, args.method, args.live, args.dead, args.threads)

if __name__ == "__main__":
    main()
