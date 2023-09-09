import asyncio
import grpc
from service_pb2 import Response
from service_pb2_grpc import YourServiceServicer, add_YourServiceServicer_to_server


class YourServicer(YourServiceServicer):
    async def UnaryCall(self, request, context):
        return Response(message=f"Hello, {request.message}")

    async def StreamCall(self, request, context):
        for i in range(10):  # Отправляем 10 сообщений
            await asyncio.sleep(1)
            yield Response(message=f"Stream {i}")


async def serve():
    server = grpc.aio.server()
    add_YourServiceServicer_to_server(YourServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
