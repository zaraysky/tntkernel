import tarantool
import logging
import socket
import json
from ipykernel.kernelbase import Kernel

from .config import CHUNK_LENGTH, HOST, SOCKET_PORT, CONSOLE_PORT

logging.basicConfig(filename="tarantool_kernel.log", level=logging.INFO)


def parse_response(response: str) -> str:
    response_strings = response.split('\n')[1:-2]
    return '\n'.join(response_strings)

def clear_command(command: str) -> str:
    comment_start = command.find('--')
    if comment_start >= 0:
        return command[:comment_start]
    return command

def send_receive(s: socket, cmd: str) -> str:
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
        self.tnt_socket.connect_ex((HOST, SOCKET_PORT))

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

        logging.info("code completion")
        logging.info(str(code))
        logging.info(str(cursor_pos))
        temp_code = code.split('\n')[-1].split(' ')[-1]
        temp_cursor_pos = len(temp_code)

        tnt = tarantool.connect(HOST, CONSOLE_PORT)

        autocompetion = """
        function jupyter_autocomplete(string, pos1, pos2)
            local json = require('json')
            local yaml = require('yaml')
            local console = require('console')
            local c = console.completion_handler(string, pos1, pos2)
            local res = c or {}
            return json.encode(res)
        end
        """
        _ = tnt.eval(autocompetion)

        cmd = f'return jupyter_autocomplete("{temp_code}",{0},{temp_cursor_pos})'
        matches = json.loads(tnt.eval(cmd)[0])

        default = {'matches': matches, 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}
        return default


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=TNTKernel)
