import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
from md5 import md5
import matplotlib.pyplot as plt

class HashApp:
    def __init__(self, master):
        self.master = master
        master.title("MD5")

        self.message_label = tk.Label(master, text="Message:")
        self.message_label.grid(row=0, column=0, sticky="w")

        self.message_text = tk.Text(master, height=10, width=50)
        self.message_text.grid(row=0, column=1, columnspan=2)

        self.load_button = tk.Button(master, text="Load Message", command=self.load_message)
        self.load_button.grid(row=1, column=0)

        self.hash_button = tk.Button(master, text="Compute Hash", command=self.compute_hash)
        self.hash_button.grid(row=1, column=1)

        self.save_button = tk.Button(master, text="Save Hash", command=self.save_hash)
        self.save_button.grid(row=1, column=2)

        self.hash_label = tk.Label(master, text="Hash Value:")
        self.hash_label.grid(row=2, column=0, sticky="w")

        self.hash_value = tk.Entry(master, width=50, state="readonly")
        self.hash_value.grid(row=2, column=1, columnspan=2)

        self.bit_position_label = tk.Label(master, text="Bit Position:")
        self.bit_position_label.grid(row=3, column=0, sticky="w")

        self.bit_position_entry = tk.Entry(master, width=10)
        self.bit_position_entry.grid(row=3, column=1)

        self.explore_button = tk.Button(master, text="Explore Avalanche Effect", command=self.explore_avalanche)
        self.explore_button.grid(row=3, column=2)

        self.graph_label = tk.Label(master, text="Avalanche Graph:")
        self.graph_label.grid(row=4, column=0, sticky="w")

        self.graph_canvas = tk.Canvas(master, width=500, height=300, bg="white")
        self.graph_canvas.grid(row=5, column=0, columnspan=3)

    def load_message(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as file:
                message = file.read()
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, message)

    def compute_hash(self):
        message = self.message_text.get(1.0, tk.END).translate(dict.fromkeys(range(32))).strip()
        hash_value = hashlib.md5(message.encode()).hexdigest()
        # hash_value = md5(message)
        self.hash_value.config(state="normal")
        self.hash_value.delete(0, tk.END)
        self.hash_value.insert(tk.END, hash_value)
        self.hash_value.config(state="readonly")

    def save_hash(self):
        hash_value = self.hash_value.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as file:
                file.write(hash_value)

    def explore_avalanche(self):
        message = self.message_text.get(1.0, tk.END).translate(dict.fromkeys(range(32))).strip()

        try:
            bit_position = int(self.bit_position_entry.get())
        except:
            messagebox.showerror("Error", "Incorrect bit position entered")
            return

        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        if bit_position < 0 or bit_position >= len(message) * 8:
            messagebox.showerror("Error", "Bit position out of range.")
            return

        modified_message = self.flip_bit(message, bit_position)

        rounds, changed_bits = zip(*md5(message, modified_message))

        plt.figure(figsize=(4, 3))
        plt.plot(rounds, changed_bits)
        plt.xlabel("Round")
        plt.ylabel("Changed Bits")
        plt.title("Avalanche Effect")
        plt.grid(True)
        plt.savefig("avalanche_effect.png")

        self.display_graph("avalanche_effect.png")

    def flip_bit(self, message, bit_pos):
        char_index, bit_index = bit_pos // 7, bit_pos % 7
        binary_message = [format(ord(x), 'b') for x in message]

        modified_char = binary_message[char_index][:bit_index] + str(int(binary_message[char_index][bit_index]) ^ 1) + binary_message[char_index][bit_index + 1:]

        binary_message[char_index] = modified_char

        return ''.join(chr(int(x, base=2)) for x in binary_message)


    def count_changed_bits(self, hash1, hash2):
        count = 0
        for char1, char2 in zip(hash1, hash2):
            byte1 = int(char1, 16)
            byte2 = int(char2, 16)
            xor_result = byte1 ^ byte2
            count += bin(xor_result).count('1')
        return count

    def display_graph(self, filename):
        image = tk.PhotoImage(file=filename)
        self.graph_canvas.create_image(0, 0, anchor="nw", image=image)
        self.graph_canvas.image = image

def main():
    root = tk.Tk()
    app = HashApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
