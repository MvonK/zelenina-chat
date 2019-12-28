version = "1.4.1"
import socket
import time
import asyncio
import os
import sys
import platform
import urllib.request
import traceback

def main():
	newcode = urllib.request.urlopen("https://raw.githubusercontent.com/MvonK/zelenina-chat/master/client.py").read().decode().replace("\r", "")
	newest_version = newcode.split("\n")[0].split('"')[-2]
	if newest_version != version:
		print("updating")
		with open(__file__, "w") as code:
			code.write(newcode)
		filename = __file__.split("\\")[-1].split("/")[-1]
		os.execl(sys.executable, "python", __file__)

	else:
		read = "READ"
		listen = "LISTEN"
		send_message = "SEND"
		connect="CONNECT"

		
		async def send_sticker(name):
			try:
				with open("stickers/"+name, "r") as f:
					for x in f:
						request = client.requestPrepare({"body":x[:-1], "reqtype": send_message})
						client.sock.send(request)
						await asyncio.sleep(0.1)
			except:
				print("Couldn't open sticker " + name)
				traceback.print_exc()
				

		class Chat:
			def __init__(self):
				self.messages = []
				self.messages.append(Message({"content": "", "sender": "", "time": "", "id": 0}))

			def AddMessage(self, msg):
				if msg.good:
					if msg not in self.messages:
						self.messages.append(msg)
						self.messages.sort(key=lambda x: x.id)
						if platform.system() == "Windows":
							os.system("cls")
						elif platform.system() == "Linux":
							os.system("clear")
					
						self.print()

			def print(self):
				for m in self.messages:
					print(m.time + " " + m.sender + ": " + m.content) 


		class Message:
			def __init__(self, msg):
				self.good = True
				try:
					
					self.content = msg["content"]
					self.sender =  msg["sender"]
					self.time =  msg["time"]
					self.id =  int(msg["id"])
				except:
					print("Message bad!")
					#print(msg)
					self.good = False
					traceback.print_exc()
					

		class Client:
			def __init__(self):
				pass


			def requestPrepare(self, data): 
				datastring = ""
				for key in data:
					datastring += key + "=" + data[key] + "&"
				for key in self.credentials:
					datastring += key + "=" + self.credentials[key] + "&"
				datastring = datastring[:-1] 
				method = "POST HTTP/1.1"
				url = "http://" + self.target_host
				headers = {"Connection": "keep-alive", "Host": self.target_host}
				body = datastring
				return('{}\r\n{}\r\n\r\n{}\r\n\r\n'.format(
					method + ' ' + url,
					'\r\n'.join('{}: {}'.format(k, v) for k, v in headers.items()),
					body,
				).encode())


			def con(self, host = "127.0.0.1", port=42069):
				while True:
					self.target_host = host

					self.target_port = port 
					self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

					# connect the client 
					print("Connecting to " + self.target_host + ":" + str(self.target_port))
					self.sock.connect((self.target_host,self.target_port))  
					print("Connected")
					self.credentials = {"pass": "pas", "user": "use"}
					request = self.requestPrepare({"reqtype": connect})


		
					self.sock.send(request)
					print("Sent login request...")

					self.loop = asyncio.get_event_loop()
					self.loop.create_task(self.mainloop())
					self.loop.run_forever()


			async def chatWriting(self):
				print("Writing ready!")
				while True:
					try:
						text = await self.loop.run_in_executor(None, input)
						if text[0] == ":" and text[-1] == ":":
							await send_sticker(text[1:-1])
						else:
							request = self.requestPrepare({"body":text, "reqtype":send_message})
							self.sock.send(request)
					except:
						traceback.print_exc()
				print("Writing ended!")
	


			async def listenForChat(self):
				self.cet = Chat()
				self.sock.send(self.requestPrepare({"reqtype":listen}))
				print("Listening ready!")
				while True:
					last = b""
					try:
						await asyncio.sleep(0.1)
						response = await self.loop.run_in_executor(None, self.sock.recv, 4096)
						bytemessages = (last + response).split(b"\x03")
						last = bytemessages[-1]
						messages = [b.decode() for b in bytemessages]
						
						for m in messages[1:]:
							m = m[4:]
						messages.pop()

						for m in messages:
							m+="\r\n\r\n"
							msg = Message(self.parse(m))
							if msg.good:
								self.cet.AddMessage(msg)
							else:
								print("Broken message :/")
						last = messages[-1]
					except:
						traceback.print_exc()
						self.sock.close()
						print("Connection timed out. Reconnecting...")
						await asyncio.sleep(2)
						self.loop.stop()
				print("Listening ended!")

			async def mainloop(self):
				try:
					asyncio.gather(self.chatWriting(), self.listenForChat())
				except:
					asyncio.get_event_loop().stop()
		

			def parse(self, response):
				res = response.split("\n")
				body = res[-3].split("&")
				contentDict = {}
				for param in body:
					pos = param.find("=")
					key, val = param[:pos], param[pos+1:]
					contentDict.update({key: val})
				return contentDict




		client = Client()
		
		client.con(host = "trojsten.ddns.net", port=42069)

if __name__ == "__main__":
	main()
