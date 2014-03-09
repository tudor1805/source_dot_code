#!/bin/bash

curl -X POST http://127.0.0.1:8000/uploads/compile_code -d '{"lang": "C", "code": "int main() {printf(\"Hello World\\n\");}"}' -H "Content-Type: application/json"
