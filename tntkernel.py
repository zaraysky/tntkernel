import logging
import socket
from ipykernel.kernelbase import Kernel

from .config import CHUNK_LENGTH, HOST, PORT

logging.basicConfig(filename="tarantool_kernel.log", level=logging.INFO)


def parse_response(response: str) -> str:
    response_strings = response.split('\n')[1:-2]
    return '\n'.join(response_strings)

def clear_command(command: str) -> str:
    comment_start = command.find('--')
    if comment_start >= 0:
        return command[:comment_start]
    return command

def send_receive(s: socket, cmd: str, tab=False) -> str:
    cmd = ' '.join(list(map(clear_command, cmd.split('\n')))) + '\n'
    s.sendall(cmd.encode())

    _buffer = ''

    while True:
        data = s.recv(CHUNK_LENGTH)
        decoded_data = data.decode()
        _buffer += decoded_data

        if '...' in decoded_data:
            break


    return parse_response(_buffer)


class TNTKernel(Kernel):

    implementation = 'TNTSocket'
    implementation_version = '0.3'
    language = 'lua'
    language_version = '0.1'
    language_info = {'name': 'lua',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-lua',
                     'file_extension': '.lua'}

    banner = "TNT kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tnt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tnt_socket.connect_ex((HOST, PORT))

        # First screen
        logging.info("First screen start")
        while True:
            data = self.tnt_socket.recv(CHUNK_LENGTH)
            if data:
                break
        logging.info(">>>", str(data.decode()), '<<<')
        logging.info("First screen end")

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        logging.info('do_execute')
        logging.info('code:')
        logging.info(code)

        if not silent:
            response = send_receive(self.tnt_socket, code)
            # response = code
            logging.info(response)
            stream_content = {'name': 'stdout', 'text': response}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_complete(self, code, cursor_pos):
        # code = code[:cursor_pos]
        response = send_receive(self.tnt_socket, code, tab=True)
        if response == 'X':
            response = send_receive(self.tnt_socket, code, tab=True)

        matches = response.split(chr(9))
        default = {'matches': matches, 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}
        return default


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=TNTKernel)
