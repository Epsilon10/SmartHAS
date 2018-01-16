import asycio
import serial_asyncio

class Output(asyncio.Protocol):
	def connection_made(self, transport):
		self.transport = transport
		print(f'Port opened: {transport}')
		transport.serial.rts = False
		transport.write(b'Connection made!\n')

	def data_recieved(self, data):
		print(f'Data Recieved: {repr(data)}')
		if b'\n' in data:
			self.transport.close()

	def connection_lost(self, exc):
		print('Port Closed')
		self.transport.loop.stop()

	def pause_writing(self):
		print('Pause writing')
		print(self.transport.get_buffer_size())

	def resume_writing(self):
		print('Resume writing')
		print(self.transport.get_buffer_size())