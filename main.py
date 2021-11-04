from flask import Flask,url_for,redirect,render_template,request,send_file
from werkzeug.utils import secure_filename
import subprocess

app=Flask(__name__)
app.config['UPLOAD_DIRECTORY']="uploads/"
app.config['FILE_NAME']=""
app.config['OUTPUT_DIRECTORY']="textresult/"
app.config['EXTENSION']=".txt"

@app.route("/",methods=["POST","GET"])
def to_upload():
    err_msg=""
    if request.method=="POST":
        if request.files['fileupload']:
            f=request.files['fileupload']
            filename=secure_filename(f.filename)
            app.config['FILE_NAME']=filename
            f.save(app.config['UPLOAD_DIRECTORY']+filename)
            return redirect(url_for("process_upload",filename=filename))
        else:
            err_msg="No file selected!"
    return render_template("index.html",error=err_msg)

@app.route("/upload/<filename>",methods=["POST","GET"])
def process_upload(filename):
    f1=open("logs/out.txt","w")
    f2=open("logs/error.txt","w")
    out=subprocess.run([f"tesseract uploads/{filename}"+f" textresult/{filename}"],shell=True,stdout=f1,stderr=f2)
    return redirect(url_for("output_file"))

@app.route("/result/",methods=["GET"])
def output_file():
    return render_template("output.html")

@app.route("/download/")
def download_file():
    file=app.config['OUTPUT_DIRECTORY']+app.config['FILE_NAME']+app.config['EXTENSION']
    return send_file(file,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port="2000",debug=True)
