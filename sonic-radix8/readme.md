### quick install

1. Install docker
2. install containerlab
```
bash -c "$(curl -sL https://get.containerlab.dev)"
```

3. get sonic-vpp image:
```
https://drive.google.com/file/d/1lgLaQ0nrEN5DKgHEcmyPZR9uhKMQQdXg/view?usp=drive_link
```

4. docker load image
```
docker load -i vrnetlab/sonic_sonic-vs:vpp20250422
```

5. deploy containerlab topology
```
sudo clab deploy -t topology.yml
```
