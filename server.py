import socket
import threading
import random

MAX_CLIENTS = 4
ROUNDS = 3

# 词语
words = [
    ("苹果", "香蕉"),
    ("猫", "狗"),
    ("篮球", "足球"),
    ("春天", "夏天")
]

def handle_client(client_socket, address, player_id, votes, lock):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message.startswith("VOTE:"):
                voted_player = int(message.split(":")[1])
                with lock:
                    votes[voted_player] += 1
            elif message == "EXIT":
                print(f"玩家 {player_id} 与服务器断开连接")
                break
    except Exception as e:
        print(f"与 {address} 的连接断开: {e}")
    finally:
        client_socket.close()

def send_words_to_clients(clients, words):
    word_pair = random.choice(words)
    different_word = random.choice([0, 1])
    same_word = 1 - different_word

    for i, (client_socket, addr) in enumerate(clients):
        if i == 0:
            word = word_pair[different_word]
        else:
            word = word_pair[same_word]
        client_socket.send(word.encode())

def count_votes(votes):
    max_votes = max(votes)
    most_voted_players = [i for i, v in enumerate(votes) if v == max_votes]
    if len(most_voted_players) == 1:
        return most_voted_players[0]  # 唯一最高票数者
    return None  # 平局

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(MAX_CLIENTS)
    print("服务器启动，等待客户端连接...")

    clients = []
    votes = [0] * MAX_CLIENTS
    lock = threading.Lock()

    for i in range(MAX_CLIENTS):
        client_socket, addr = server.accept()
        print(f"客户端连接自: {addr}")
        clients.append((client_socket, addr))

        # 告知客户端自己的编号
        client_socket.send(f"NO:{str(i)}".encode())

        # 每个客户端启动一个线程
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, i, votes, lock))
        client_thread.start()

    for round_num in range(1, ROUNDS + 1):
        print(f"开始第 {round_num} 局游戏")
        send_words_to_clients(clients, words)

        # 投票环节
        while True:
            print("开始投票...")
            for client_socket, addr in clients:
                client_socket.send("VOTE".encode())

            # 等待投票
            input("请等待所有玩家投票，按任意键继续...")

            # 统计投票结果
            with lock:
                voted_player = count_votes(votes)

            if voted_player is not None:
                if voted_player == 0:
                    # 卧底被发现，平民胜利
                    print(f"玩家 {voted_player} 被选出，平民胜利！")
                    for client_socket, addr in clients:
                        client_socket.send("CIVILIAN_WIN".encode())
                else:
                    # 平民被误选，卧底胜利
                    print(f"玩家 {voted_player} 被选出，卧底胜利！")
                    for client_socket, addr in clients:
                        client_socket.send("UNDERCOVER_WIN".encode())
                break
            else:
                print("投票结果为平局，进入下一轮...")
                for client_socket, addr in clients:
                    client_socket.send("TIE".encode())

            with lock:
                votes = [0] * MAX_CLIENTS

    print("游戏结束，断开所有客户端连接")

    for client_socket, addr in clients:
        client_socket.send("EXIT".encode())
        client_socket.close()

if __name__ == "__main__":
    main()
