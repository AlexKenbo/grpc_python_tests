Generated gRPC server and client from *.proto

```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto
```