from service.app import app
import ssl

if __name__ == '__main__':
  context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
  context.load_cert_chain('/etc/letsencrypt/live/blackfynnpythonlink.ml/fullchain.pem', '/etc/letsencrypt/live/blackfynnpythonlink.ml/privkey.pem')
  app.run(host='0.0.0.0', port=80, threaded=True, ssl_context=context)
