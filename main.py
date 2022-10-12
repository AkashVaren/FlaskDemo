from flask import Flask, render_template,url_for, request, redirect, send_from_directory, Response
import os,io,PyPDF2, time
from io import BytesIO
from flask_cors import CORS
import linecache
from flask_socketio import SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@socketio.on('connect')
def connect():
   pass

@socketio.event
def disconnect():
   pass

@socketio.event
def readFile(data):
      flag=0
      c=data['c']
      if data['data'].split('.')[1]=="pdf":
         flag=1
      def innerReadPDF():
         global lines
         if(c==0):
            try:
               file=open("/Users/akash-15619/LibraryApplication/static/Uploads/"+data['data'], "rb")
               lines=list()
               pdfreader=PyPDF2.PdfFileReader(file)
               num=pdfreader.getNumPages()
               for i in range(num):
                  pageobj=pdfreader.getPage(i)
                  text=pageobj.extractText()
                  res = bytes(text, 'utf-8')
                  lines=lines+text.split("\n")
               file.close()
            except Exception as e:
               print(e)
               return
         s=""
         p=c+100

         if(p>len(lines) and len(lines)>100 ):
            return "over"
         elif(len(lines)<100 and c<len(lines)) :
            p=len(lines)
         for i in range(c,p):
            if(i<len(lines)):
               s=s+lines[i]+"\n"
         socketio.emit('read_File', {'data': s})
         return s
      def innerReadTXT():
         global lines
         try:
            lines=list()
            for i in range(c,c+100):
               lines.append(linecache.getline("/Users/akash-15619/LibraryApplication/static/Uploads/"+data['data'], i))
         except Exception as e:
            print(e)
            return
         s=""
         for i in range(len(lines)):
            s=s+lines[i]
         if s=="":
            return "over"
         socketio.emit('read_File', {'data': s})
      if(flag==1):
         return Response(innerReadPDF(),mimetype="text/plain")
      else:
         return Response(innerReadTXT(),mimetype="text/plain")

file=""
file1=""
lines=list()
@app.route('/')
def index():
   return render_template("index.html")

app.config["FILE_UPLOADS"]="/Users/akash-15619/LibraryApplication/static/Uploads"
app.config["EXTENSIONS"]=["pdf","txt"]
count=0
dataList=list()
quantity=100
total=0
def extensocketionChecker(filename):
   type=filename.split(".",1)[1]
   if type.lower() in app.config["EXTENSIONS"]:
      return True
   else:
      return False

@app.route('/upload',methods=['GET','POST'])
def upload():
   a=""
   if request.method=="POST":
      if request.files:
         files=request.files["file"]
         if extensocketionChecker(files.filename):
            files.save(os.path.join(app.config["FILE_UPLOADS"],files.filename))
            a="File Uploaded"
            print("File Uploaded")
         else:
            print("extensocketion not supported")
            a="extensocketion not supported"
   return render_template("upload.html",content=a)

@app.route('/delete/<filename>',methods=['GET','POST'])
def deleteFile(filename):
   os.remove(os.path.join("/Users/akash-15619/LibraryApplication/static/Uploads", filename))
   return render_template("delete.html",files=os.listdir("/Users/akash-15619/LibraryApplication/static/Uploads"))

@app.route('/delete',methods=['GET','POST'])
def delete():
   return render_template("delete.html",files=os.listdir("/Users/akash-15619/LibraryApplication/static/Uploads"))

@app.route('/downloadFile/<filename>',methods=['GET','POST'])
def downloadFile(filename):
   print(filename)
   return send_from_directory("/Users/akash-15619/LibraryApplication/static/Uploads", filename,as_attachment=True)

flag1=0
@app.route('/read')
def read():
   return render_template("read.html",files=os.listdir("/Users/akash-15619/LibraryApplication/static/Uploads"))

if __name__ == '__main__':
   port = int(os.environ.get('PORT', 8000))
   socketio.run(app,host='0.0.0.0', port=port)