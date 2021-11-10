from flask import Flask,url_for,redirect,render_template,request,send_file
from werkzeug.utils import secure_filename
import subprocess
import os

app=Flask(__name__)
app.config['UPLOAD_DIRECTORY']="uploads"
app.config['FILES_LIST']=[]
app.config['OUTPUT_DIRECTORY']="textresult"
# app.config['EXTENSION']=".txt"
app.config['EXTENSION']="txt"

@app.route("/",methods=["POST","GET"])
def to_upload():
    err_msg=""
    files_list=[]
    if request.method=="POST":
        if request.files['fileupload']:
            for f in request.files.getlist("fileupload"):
            # f=request.files['fileupload']
                file_name=secure_filename(f.filename)
                files_list.append(file_name)
                #app.config['FILE_NAME']=filename
                # f.save(app.config['UPLOAD_DIRECTORY']+filename)
                f.save(os.path.join(app.config['UPLOAD_DIRECTORY'],file_name))
            app.config['FILES_LIST']=files_list
            return redirect(url_for("process_upload",files_list=files_list))
        else:
            err_msg="No file selected!"
    return render_template("index.html",error=err_msg)

@app.route("/upload/<files_list>",methods=["POST","GET"])
def process_upload(files_list):
    out_log=open("logs/out.txt","w")
    err_log=open("logs/error.txt","w")
    for f in files_list:
        to_convert=os.path.join(app.config['UPLOAD_DIRECTORY'],f)
        convert2txt=os.path.join(app.config['OUTPUT_DIRECTORY'],f)
        # out=subprocess.run([f"tesseract uploads/{filename}"+f" textresult/{filename}"],shell=True,stdout=f1,stderr=f2)
        if os.name=="nt": # If OS is windows-based-based
            out=subprocess.run(["tesseract",to_convert,convert2txt],shell=True,stdout=out_log,stderr=err_log)
        else: # Else, it might be linux or mac (posix)
            #out=subprocess.run(["tesseract %s %s"%(to_convert,convert2txt)],shell=True,stdout=f1,stderr=f2)
            out=subprocess.run(["tesseract",to_convert,convert2txt],stdout=out_log,stderr=err_log) # Omit 'shell=True' in LINUX/MAC systems
    return redirect(url_for("output_file"))

@app.route("/result/",methods=["GET"])
def output_file():
    return render_template("output.html")

@app.route("/download/")
def download_file():
    # file=app.config['OUTPUT_DIRECTORY']+app.config['FILE_NAME']+app.config['EXTENSION']
    file=os.path.join(app.config['OUTPUT_DIRECTORY'],"%s.%s"%(app.config['FILE_NAME'],app.config['EXTENSION']))
    return send_file(file,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port="2000",debug=True)
