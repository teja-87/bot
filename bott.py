
import json
import statistics
import time
import urllib.request
import urllib.error

# Robinhood Chain public mainnet RPC
RPC_URL = "https://rpc.mainnet.chain.robinhood.com"

# Number of requests to send
REQUESTS = 50

# Wait between requests, in seconds
INTERVAL = 0.2
def rpc_call():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_blockNumber",
        "params": []
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        RPC_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST"
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()

        return (time.perf_counter() - start) * 1000

    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}")
        print(e.read().decode(errors="ignore"))
        return None

    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    results = []

    print(f"Testing: {RPC_URL}")
    print(f"Requests: {REQUESTS}")
    print()

    for i in range(REQUESTS):
        latency = rpc_call()

        if latency is not None:
            results.append(latency)
            print(f"{i + 1:02d}/{REQUESTS}  {latency:.2f} ms")

        time.sleep(INTERVAL)

    if not results:
        print("No successful requests.")
        return

    results.sort()

    p50 = statistics.median(results)
    p95 = results[int(len(results) * 0.95) - 1]
    p99 = results[int(len(results) * 0.99) - 1]

    print()
    print("========== RESULTS ==========")
    print(f"Successful: {len(results)}/{REQUESTS}")
    print(f"Minimum:    {min(results):.2f} ms")
    print(f"Average:    {statistics.mean(results):.2f} ms")
    print(f"P50:        {p50:.2f} ms")
    print(f"P95:        {p95:.2f} ms")
    print(f"P99:        {p99:.2f} ms")
    print(f"Maximum:    {max(results):.2f} ms")


if __name__ == "__main__":
    main()