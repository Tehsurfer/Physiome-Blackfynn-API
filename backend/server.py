from service.app import app
import ssl

if __name__ == '__main__':
  context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
  context.load_cert_chain('/etc/letsencrypt/live/blackfynnpythonlink.ml/cert.pem', '/etc/letsencrypt/live/blackfynnpythonlink.ml/privkey.pem')
  app.run(host="127.0.0.1",port=82, ssl_context= context)
