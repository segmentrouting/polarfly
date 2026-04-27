### Polarfly q=7 topology

Post polarfly topology data
```
curl -s -X POST http://localhost:30080/topology   -H 'Content-Type: application/json'   -d @q7/q7-fabric.json | python3 -m json.tool
```