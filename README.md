NOTE- Under developement

# system-design-prototypes
Some fun prototypes while learning system design

## Multi Threading

## BlockingQueues

## WebSockets
### Using Client/Server
### Send a request to websocket over TCP connection from powershell

```
$tcpClient = New-Object System.Net.Sockets.TcpClient("localhost", 3000)
$networkStream = $tcpClient.GetStream()
```

Send headers directly

```
$headers = [System.Text.Encoding]::ASCII.GetBytes(@"
GET / HTTP/1.1
Host: localhost:3000
Upgrade: websocket
Connection: Upgrade
WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
WebSocket-Version: 13
"@)

$networkStream.Write($headers, 0, $headers.Length)
$networkStream.Flush()
```


## RealTimeChats

