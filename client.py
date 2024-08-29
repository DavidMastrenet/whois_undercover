import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = input("请输入服务器IP地址: ")
    server_port = 9999

    client.connect((server_ip, server_port))

    while True:
        message = client.recv(1024).decode()
        if message in ["CIVILIAN_WIN", "UNDERCOVER_WIN"]:
            print(f"游戏结束，{message.replace('_', ' ')}!")
            continue
        elif message.startswith("NO:"):
            print(f"你的编号是: {message.replace('NO:', '')}")
            continue
        elif message == "VOTE":
            # 投票环节
            vote = input("输入你要投票的玩家ID (0-3): ").strip()
            client.send(f"VOTE:{vote}".encode())
            continue
        elif message == "TIE":
            print("平局，继续游戏...")
            continue
        elif message == "EXIT":
            print("游戏结束，服务器已断开连接")
            break
        else:
            print(f"你的词语是: {message}")
            continue

    client.close()

if __name__ == "__main__":
    main()
