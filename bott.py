import sys
import json
import time
import statistics
import http.client
import ssl

HOST = "rpc.mainnet.chain.robinhood.com"
PATH = "/"
REQUESTS = 30
INTERVAL = 1.0


def rpc_request(conn):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_blockNumber",
        "params": []
    }

    body = json.dumps(payload)

    start = time.perf_counter()

    try:
        conn.request(
            "POST",
            PATH,
            body=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "latency-test"
            }
        )

        response = conn.getresponse()
        response.read()

        latency = (time.perf_counter() - start) * 1000

        return latency, response.status

    except Exception as e:
        print(f"Request failed: {e}")
        return None, None


def percentile(values, percent):
    values = sorted(values)
    index = int(len(values) * percent / 100)
    index = min(index, len(values) - 1)
    return values[index]


def main():

    if len(sys.argv) < 2:
        print("Usage: python latency_persistent.py <region>")
        print("Example: python latency_persistent.py ohio")
        return

    region = sys.argv[1]

    print(f"Region: {region}")
    print(f"Target: https://{HOST}")
    print(f"Requests: {REQUESTS}")
    print()

    context = ssl.create_default_context()

    conn = http.client.HTTPSConnection(
        HOST,
        timeout=10,
        context=context
    )

    # -------------------------
    # WARM-UP
    # -------------------------

    print("Opening connection...")

    latency, status = rpc_request(conn)

    if latency is None:
        print("Warm-up failed.")
        conn.close()
        return

    print(f"Warm-up: {latency:.2f} ms (HTTP {status})")
    print()

    # -------------------------
    # MEASURE
    # -------------------------

    results = []

    for i in range(REQUESTS):

        latency, status = rpc_request(conn)

        if latency is not None:
            results.append(latency)
            print(
                f"{i + 1:02d}/{REQUESTS}: "
                f"{latency:.2f} ms "
                f"(HTTP {status})"
            )

        time.sleep(INTERVAL)

    conn.close()

    # -------------------------
    # RESULTS
    # -------------------------

    if not results:
        print("No successful requests.")
        return

    print()
    print("========== RESULTS ==========")

    print(f"Successful: {len(results)}/{REQUESTS}")
    print(f"Min:        {min(results):.2f} ms")
    print(f"Average:    {statistics.mean(results):.2f} ms")
    print(f"P50:        {percentile(results, 50):.2f} ms")
    print(f"P95:        {percentile(results, 95):.2f} ms")
    print(f"P99:        {percentile(results, 99):.2f} ms")
    print(f"Max:        {max(results):.2f} ms")


if __name__ == "__main__":
    main()