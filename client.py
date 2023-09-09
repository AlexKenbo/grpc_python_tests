import asyncio
import random
import string
import time
import psutil
import grpc
import service_pb2
import service_pb2_grpc
from tabulate import tabulate


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


async def run_unary_calls(num_clients):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.YourServiceStub(channel)
        tasks = []
        start_time = time.time()

        for i in range(num_clients):
            random_length = random.randint(200, 1500)
            random_data = random_string(random_length)
            task = asyncio.ensure_future(stub.UnaryCall(
                service_pb2.Request(message=random_data)))
            tasks.append(task)

        await asyncio.gather(*tasks)
        end_time = time.time()

    return end_time - start_time


async def run_streaming_calls(num_clients):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.YourServiceStub(channel)
        tasks = []
        for i in range(num_clients):
            task = asyncio.ensure_future(streaming_call(stub))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Вычисляем средние значения
        avg_latencies = [result[0] for result in results]
        avg_throughputs = [result[1] for result in results]

        overall_avg_latency = sum(avg_latencies) / \
            len(avg_latencies) if avg_latencies else 0
        overall_avg_throughput = sum(
            avg_throughputs) / len(avg_throughputs) if avg_throughputs else 0

        # print(f"Average Latency for {num_clients} clients: {overall_avg_latency}")
        # print(f"Average Throughput for {num_clients} clients: {overall_avg_throughput} bytes/sec")

        return overall_avg_latency, overall_avg_throughput


async def streaming_call(stub):
    request_iterator = generate_messages()
    latencies = []
    total_bytes = 0
    start_time = time.time()
    async for response in stub.StreamCall(request_iterator):
        send_time = time.time()
        # здесь ваш код для отправки сообщения
        receive_time = time.time()

        latency = (receive_time - send_time) * 1e9  # Convert to nanoseconds
        latencies.append(latency)

        total_bytes += len(response.message.encode('utf-8'))

    end_time = time.time()

    avg_latency_ns = sum(latencies) / len(latencies) if latencies else 0
    throughput_bytes_per_s = total_bytes / \
        (end_time - start_time) if (end_time - start_time) != 0 else 0

    return avg_latency_ns, throughput_bytes_per_s


async def generate_messages():
    for i in range(10):
        random_length = random.randint(20, 150)
        random_data = random_string(random_length)
        yield service_pb2.Request(message=random_data)


async def main():
    client_counts = [500, 2000, 5000, 10000, 30000]
    unary_results = []
    streaming_results = []

    # Тестирование унарных вызовов
    for count in client_counts:
        unary_time = await run_unary_calls(count)
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory().percent
        unary_results.append([count, unary_time, cpu_percent, memory_info])

    print("Unary Calls:")
    print(tabulate(unary_results, headers=[
          "Clients", "Unary Time(s)", "CPU(%)", "Memory(%)"]))

    # Тестирование стриминговых вызовов
    for count in client_counts:
        avg_latency, throughput = await run_streaming_calls(count)
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory().percent
        streaming_results.append(
            [count, avg_latency, throughput, cpu_percent, memory_info])

    print("Streaming Calls:")
    print(tabulate(streaming_results, headers=[
          "Clients", "Avg Latency(ns)", "Avg Throughput(bytes/ms)", "CPU(%)", "Memory(%)"]))

if __name__ == '__main__':
    asyncio.run(main())
