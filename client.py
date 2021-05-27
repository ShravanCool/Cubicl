import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from NTRU import NTRU
import pickle

HOST = '127.0.0.1'
PORT = 9090

class Client:
    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False

        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')
        
        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()


    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        
        N = 11
        p = 3
        q = 32

        f = [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1]
        g = [-1, 0, 1, 1, 0, 1, 0, 0, -1, 0, 1]

        D = [0] * (N + 1)
        D[0], D[N] = -1, 1

        encryptor = NTRU.NTRU(N, p, q, f, g)
        encryptor.gen_keys()
        pubkey = encryptor.get_pubkey()

        encmsg, l = NTRU.encrypt(message, p, q, D, pubkey)
        d = {1: encmsg, 2: l}
        msg1 = pickle.dumps(d)

        self.sock.send(msg1)
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        
        N = 11
        p = 3
        q = 32

        f = [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1]
        g = [-1, 0, 1, 1, 0, 1, 0, 0, -1, 0, 1]

        D = [0] * (N + 1)
        D[0], D[N] = -1, 1

        decryptor = NTRU.NTRU(N, p, q, f, g)
        decryptor.gen_keys()
        privkey1, privkey2 = decryptor.get_privkeys()

        while self.running:
            try:
                message = pickle.loads(self.sock.recv(1024))
                if message == 'NICK':
                    nickname = pickle.dumps(self.nickname)
                    self.sock.send(nickname)
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        if type(message) == str:
                            plaintext = message
                        else:
                            plaintext = NTRU.decrypt(message[1], privkey1, privkey2, p, q, D, message[2])

                        self.text_area.insert('end', plaintext)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print('Error')
                self.sock.close()
                break

client = Client(HOST, PORT)


