### SRCTL

Run the srctl command line tool to get paths between nodes and program linux SRv6 routes.

1. setenv

```
export JALAPENO_API_SERVER=http://api.jalapeno.example.com:8080
```

```
export JALAPENO_API_SERVER=http://198.18.133.102:30800
```

2. get paths

```
srctl get-paths -s igp_node/2_0_0_0000.0001.0000 -d igp_node/2_0_0_0000.0001.0029 --type best-paths --limit 4 -v
```

3. program routes

```
