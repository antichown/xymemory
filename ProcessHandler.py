from ctypes import *
from win32api import *
import psutil

"""WinApi methods"""
K32 = windll.kernel32
ReadProcessMemory = K32.ReadProcessMemory
WriteProcessMemory = K32.WriteProcessMemory
OpenProcess = K32.OpenProcess
GetLastError = K32.GetLastError

"""All access"""
PAA = 0x1F0FFF

class ProcessException(Exception):
    pass

class ProcessHandler(object):

    def __init__(self, process_name=None):
        self.process = self.process_from_name(process_name)
        self.h_process = None

    def list(self):
        processes = []

        for process in psutil.process_iter():
            processes.append(process)

        return  processes

    def process_from_name(self, process_name):
        for process in self.list():
            if process.name() == process_name:
                return  process

        raise ProcessException("Invalid process name.")


    def open(self):
        if self.process is None:
            raise ProcessException("The selected process does not exist")

        self.h_process = OpenProcess(PAA, False, self.process.pid)
        if self.h_process is None:
            raise ProcessException("Cannot open this process. (%08x)", GetLastError())

        return True

    def close(self):
        if self.process is not None:
            CloseHandle(self.process)

    def read_bytes(self, address, bytes=4):
        buffer = create_string_buffer(bytes)
        bytesread = c_ulong(0)
        data = ''
        length = bytes
        _address = address
        _length = length

        while length:
            if not ReadProcessMemory(self.h_process, address, buffer, bytes, byref(bytesread)):
                if bytesread.value:
                    data += buffer.raw[:bytesread.value]
                    length -= bytesread.value
                    address += bytesread.value
                if not len(data):
                    raise ProcessException(
                        'Error %s in ReadProcessMemory(%08x, %d, read=%d)' % (GetLastError(),
                                                                              address,
                                                                              length,
                                                                              bytesread.value))
                return data

            data += buffer.raw[:bytesread.value]
            length -= bytesread.value
            address += bytesread.value

        return data

    def create_string_buffer(init, size=None):
        if isinstance(init, (str, unicode)):
            if size is None:
                size = len(init) + 1

            buftype = c_char * size
            buf = buftype()
            buf.value = init
            return buf

        elif isinstance(init, (int, long)):
            buftype = c_char * init
            buf = buftype()
            return buf

