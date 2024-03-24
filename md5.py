import math

# This list maintains the amount by which to rotate the buffers during processing stage
rotate_by = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
             5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
             4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
             6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

# This list maintains the additive constant to be added in each processing step.
constants = [int(abs(math.sin(i+1)) * 4294967296)
             & 0xFFFFFFFF for i in range(64)]

chunks1 = []
chunks2 = []
plot_data = []

# STEP 1: append padding bits s.t. the length is congruent to 448 modulo 512
# which is equivalent to saying 56 modulo 64.
# padding before adding the length of the original message is conventionally done as:
# pad a one followed by zeros to become congruent to 448 modulo 512(or 56 modulo 64).


def pad(msg):
    msg_len_in_bits = (8*len(msg)) & 0xffffffffffffffff
    msg.append(0x80)

    while len(msg) % 64 != 56:
        msg.append(0)

# STEP 2: append a 64-bit version of the length of the length of the original message
# in the unlikely event that the length of the message is greater than 2^64,
# only the lower order 64 bits of the length are used.

# sys.byteorder -> 'little'
    # little endian convention
    msg += msg_len_in_bits.to_bytes(8, byteorder='little')
    # to_bytes(8...) will return the lower order 64 bits(8 bytes) of the length.

    return msg


# STEP 3: initialise message digest buffer.
# MD buffer is 4 words A, B, C and D each of 32-bits.

init_MDBuffer = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

# UTILITY/HELPER FUNCTION:


def leftRotate(x, amount):
    x &= 0xFFFFFFFF
    return (x << amount | x >> (32-amount)) & 0xFFFFFFFF


# STEP 4: process the message in 16-word blocks
# Message block stored in buffers is processed in the follg general manner:
# A = B + rotate left by some amount<-(A + func(B, C, D) + additive constant + 1 of the 16 32-bit(4 byte) blocks converted to int form)

def processMessage(msg, msg_number):
    # create copy of the buffer init constants to preserve them for when message has multiple 512-bit blocks
    init_temp = init_MDBuffer[:]

    # message length is a multiple of 512bits, but the processing is to be done separately for every 512-bit block.
    for offset in range(0, len(msg), 64):
        A, B, C, D = init_temp  # have to initialise MD Buffer for every block
        block = msg[offset: offset+64]  # create block to be processed
        # msg is processed as chunks of 16-words, hence, 16 such 32-bit chunks
        # 1 pass through the loop processes some 32 bits out of the 512-bit block.
        for i in range(64):
            if i < 16:
                # Round 1
                def func(b, c, d): return (b & c) | (~b & d)
                # if b is true then ans is c, else d.
                def index_func(i): return i

            elif i >= 16 and i < 32:
                # Round 2
                def func(b, c, d): return (d & b) | (~d & c)
                # if d is true then ans is b, else c.
                def index_func(i): return (5*i + 1) % 16

            elif i >= 32 and i < 48:
                # Round 3
                def func(b, c, d): return b ^ c ^ d
                # Parity of b, c, d
                def index_func(i): return (3*i + 5) % 16

            elif i >= 48 and i < 64:
                # Round 4
                def func(b, c, d): return c ^ (b | ~d)
                def index_func(i): return (7*i) % 16

            F = func(B, C, D)  # operate on MD Buffers B, C, D
            # select one of the 32-bit words from the 512-bit block of the original message to operate on.
            G = index_func(i)

            to_rotate = A + F + \
                constants[i] + \
                int.from_bytes(block[4*G: 4*G + 4], byteorder='little')
            newB = (B + leftRotate(to_rotate, rotate_by[i])) & 0xFFFFFFFF

            A, B, C, D = D, newB, B, C
            # rotate the contents of the 4 MD buffers by one every pass through the loop

            if msg_number == 1:
                chunks1.append((A, B, C, D))
            else:
                chunks2.append((A, B, C, D))

        # Add the final output of the above stage to initial buffer states
        for i, val in enumerate([A, B, C, D]):
            init_temp[i] += val
            init_temp[i] &= 0xFFFFFFFF
        # The init_temp list now holds the MD(in the form of the 4 buffers A, B, C, D) of the 512-bit block of the message fed.

    # The same process is to be performed for every 512-bit block to get the final MD(message digest).

    # Construct the final message from the final states of the MD Buffers
    return sum(buffer_content << (32*i) for i, buffer_content in enumerate(init_temp))


def MD_to_hex(digest):
    # takes MD from the processing stage, change its endian-ness and return it as 128-bit hex hash
    raw = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(raw, byteorder='big'))


def md5(msg1, msg2):

    chunks1.clear()
    chunks2.clear()
    plot_data.clear()

    # create a copy of the original message in form of a sequence of integers [0, 256)
    msg1 = bytearray(msg1, 'ascii')
    msg1 = pad(msg1)
    processed_msg1 = processMessage(msg1, 1)
    # processed_msg contains the integer value of the hash
    message_hash1 = MD_to_hex(processed_msg1)
    # print("Message Hash: ", message_hash)

    msg2 = bytearray(msg2, 'ascii')
    msg2 = pad(msg2)
    processed_msg2 = processMessage(msg2, 2)
    message_hash2 = MD_to_hex(processed_msg2)

    for i, j in zip(chunks1, chunks2):
        ones_count = 0
        for k, l in zip(i, j):
            ones_count += bin(k ^ l).count('1')
        plot_data.append(ones_count)

    return list(enumerate(plot_data))


# if __name__ == '__main__':
#     message1 = input("Message 1:")
#     message2 = input("Message 2:")
#     print(md5(message1, message2))
#     # print(plot_data)
