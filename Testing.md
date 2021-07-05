# Testing notes using curl

## List projects
```bash
$ curl http://127.0.0.1:5000/artstore
```

## Delete project
```bash
$ curl -X DELETE http://127.0.0.1:5000/artstore/config-cpp
```

## Add project
```bash
$ curl -X POST -H "Content-Type: application/json" -d @project.json http://127.0.0.1:5000/artstore/config-cpp
```

## Get project config
```bash
$ curl http://127.0.0.1:5000/artstore/config-cpp
```

## Upload html
```bash
$ curl -F filename=index.html -F upload=@index.html http://127.0.0.1:5000/artstore/serf-cpp/unit
```

## Upload .tgz
```bash
$ curl -F item=@coverage.tar.gz http://127.0.0.1:5000/artstore/serf-cpp/coverage
```

## Upload .zip
```bash
$ curl -F item=@coverage.zip http://127.0.0.1:5000/artstore/serf-cpp/coverage
```

## TODO: Upload collection artifact