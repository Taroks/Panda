from Internal.API.ParserAPI import app

if __name__ == "__main__":
    app.debug = True
    app.run(host='192.168.74.105', port=6005)
