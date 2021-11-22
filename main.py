from flask import Flask,url_for,redirect,render_template,request,send_file
from werkzeug.utils import secure_filename
import subprocess
import os
import random,string
from zipfile import ZipFile

app=Flask(__name__)
app.config["UPLOAD_DIR"]="uploads"
app.config["FILES_LIST"]=[]
app.config["OUTPUT_DIR"]="textresult"
# app.config['EXTENSION']=".txt"
# app.config["EXTENSION"]="txt"
app.config["TEMP_DIR"]=""
max=5

#Generate random string for temp directory name
def _randomstr(x: int)->str:
    letters=string.ascii_letters
    return "".join(random.choice(letters) for i in range(x))

def _zipoutputs():
    os.chdir(app.config["OUTPUT_DIR"])
    package=os.path.join("./",app.config["TEMP_DIR"])
    with ZipFile(f'{app.config["TEMP_DIR"]}.%s'%("zip"),'w') as zippy:
        for dirpath,dirname,files in os.walk(package):
            for file in files:
                zippy.write(os.path.join(dirpath,file))
        zippy.close()
    # Add this line to go back to project root directory
    os.chdir("../")

@app.route("/",methods=["POST","GET"])
def to_upload():
    err_msg=""
    # files_list=[]
    if request.method=="POST":
        if request.files['fileupload']:
            # Create random name for temp directory
            app.config["TEMP_DIR"]=_randomstr(max)
            # Create temp directory in both uploads and textresult directories in current working directory
            os.makedirs(os.path.join(app.config["UPLOAD_DIR"],app.config["TEMP_DIR"]))
            os.makedirs(os.path.join(app.config["OUTPUT_DIR"],app.config["TEMP_DIR"]))
            for f in request.files.getlist("fileupload"):
                # f=request.files['fileupload']
                file_name=secure_filename(f.filename)
                app.config['FILES_LIST'].append(file_name)
                # Pass globally filename so we know what file is to be downloaded from textresult
                #app.config['FILE_NAME']=filename
                # f.save(app.config['UPLOAD_DIRECTORY']+filename)
                f.save(os.path.join(app.config["UPLOAD_DIR"],app.config["TEMP_DIR"],file_name))
            return redirect(url_for("process_upload"))
        else:
            err_msg="No file/s selected!"
    return render_template("index.html",error=err_msg)

@app.route("/upload/",methods=["GET"])
def process_upload():
    out_log=open("logs/out.txt","w")
    err_log=open("logs/error.txt","w")
    for f in app.config["FILES_LIST"]:
        to_convert=os.path.join(app.config['UPLOAD_DIR'],app.config["TEMP_DIR"],f)
        convert2txt=os.path.join(app.config['OUTPUT_DIR'],app.config["TEMP_DIR"],f)
        #out=subprocess.run([f"tesseract uploads/{filename}"+f" textresult/{filename}"],shell=True,stdout=f1,stderr=f2)
        # If OS is windows-based
        if os.name=="nt": 
            out=subprocess.run(["tesseract",to_convert,convert2txt],shell=True,stdout=out_log,stderr=err_log)
        # Else, it might be linux or mac (posix)
        else: 
            #out=subprocess.run(["tesseract %s %s"%(to_convert,convert2txt)],shell=True,stdout=f1,stderr=f2)
            # Omit 'shell=True' in LINUX/MAC systems
            out=subprocess.run(["tesseract",to_convert,convert2txt],stdout=out_log,stderr=err_log)
    _zipoutputs()
    return redirect(url_for("output_file"))

@app.route("/result/",methods=["GET"])
def output_file():
    return render_template("output.html")

@app.route("/download/")
def download_file():
    # file=app.config['OUTPUT_DIRECTORY']+app.config['FILE_NAME']+app.config['EXTENSION']
    # file=os.path.join(app.config['OUTPUT_DIR'],"%s.%s"%(app.config['FILE_NAME'],app.config['EXTENSION']))
    file=os.path.join(app.config['OUTPUT_DIR'],"%s.%s"%(app.config["TEMP_DIR"],"zip"))
    return send_file(file,as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port="2000",debug=True)
