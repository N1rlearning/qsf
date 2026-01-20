#!/usr/bin/env python3
"""
PDF去水印 - FastAPI + TailwindCSS
支持中英文双语水印移除
"""

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from pathlib import Path
from pdf_processor import PDFProcessor

# 创建模板实例
templates = Jinja2Templates(directory="templates")

# 创建 FastAPI 应用
app = FastAPI(
    title="PDF去水印",
    description="免费在线PDF水印移除工具 - 支持中英文双语",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
TEMPLATES_DIR = Path("templates")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# PDF 处理器
processor = PDFProcessor()

# 响应模型
class ProcessResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    error: Optional[str] = None
    stats: Optional[dict] = None

# 多语言文案
I18N = {
    "cn": {
        "title": "PDF去水印",
        "subtitle": "免费在线移除PDF水印",
        "features": "支持移除扫描全能王中英文水印、二维码，合并PDF",
        "upload_text": "点击或拖拽PDF文件到此处",
        "upload_subtext": "支持批量上传，最多50个文件，单个文件最大100MB",
        "btn_process": "开始处理",
        "btn_processing": "处理中...",
        "btn_download": "下载PDF",
        "btn_reset": "重新开始",
        "result_title": "处理完成！",
        "result_success": "成功",
        "pages": "页面数",
        "files": "文件数",
        "watermarks": "移除水印",
        "size": "输出大小",
        "option_text": "移除文字水印",
        "option_text_desc": "如全能扫描王、CamScanner",
        "option_qr": "移除二维码",
        "option_qr_desc": "右下角二维码水印",
        "option_merge": "合并PDF",
        "option_merge_desc": "将所有文件合并为一个",
        "option_compress": "压缩文件",
        "option_compress_desc": "优化减小文件大小",
        "ad_placeholder": "广告位 - Google AdSense",
    },
    "en": {
        "title": "PDF Watermark Remover",
        "subtitle": "Free Online PDF Watermark Removal",
        "features": "Remove CamScanner watermarks (Chinese & English), QR codes, merge PDFs",
        "upload_text": "Click or drag PDF files here",
        "upload_subtext": "Batch upload supported, max 50 files, 100MB per file",
        "btn_process": "Start Processing",
        "btn_processing": "Processing...",
        "btn_download": "Download PDF",
        "btn_reset": "Start Over",
        "result_title": "Processing Complete!",
        "result_success": "Success",
        "pages": "Pages",
        "files": "Files",
        "watermarks": "Watermarks Removed",
        "size": "Output Size",
        "option_text": "Remove Text Watermark",
        "option_text_desc": "e.g. CamScanner, Scanned with",
        "option_qr": "Remove QR Code",
        "option_qr_desc": "QR code watermark at bottom right",
        "option_merge": "Merge PDF",
        "option_merge_desc": "Combine all files into one",
        "option_compress": "Compress File",
        "option_compress_desc": "Optimize and reduce file size",
        "ad_placeholder": "Ad Space - Google AdSense",
    }
}

@app.get("/")
async def root(request: Request, lang: str = "cn"):
    """返回主页"""
    t = I18N.get(lang, I18N["cn"])
    return templates.TemplateResponse("index.html", {"request": request, "lang": lang, "t": t})

@app.get("/cn")
async def root_cn(request: Request):
    """中文主页"""
    return await root(request, "cn")

@app.get("/en")
async def root_en(request: Request):
    """英文主页"""
    return await root(request, "en")

@app.post("/process")
async def process_pdf(
    files: List[UploadFile] = File(...),
    remove_text: str = Form(True),
    remove_qr: str = Form(True),
    merge: str = Form(True),
    compress: str = Form(True),
    lang: str = Form("cn")
):
    """处理PDF文件"""
    try:
        if not files or all(f.filename == '' for f in files):
            raise HTTPException(status_code=400, detail="没有上传文件" if lang == "cn" else "No files uploaded")
        
        # 解析布尔值
        remove_text_bool = remove_text.lower() == 'true'
        remove_qr_bool = remove_qr.lower() == 'true'
        merge_bool = merge.lower() == 'true'
        compress_bool = compress.lower() == 'true'
        
        # 保存上传的文件
        file_paths = []
        task_id = str(uuid.uuid4())
        
        for file in files:
            if file.filename and file.filename.endswith('.pdf'):
                filepath = UPLOAD_DIR / f"{task_id}_{file.filename}"
                content = await file.read()
                with open(filepath, 'wb') as f:
                    f.write(content)
                file_paths.append(str(filepath))
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="没有有效的PDF文件" if lang == "cn" else "No valid PDF files")
        
        # 处理PDF
        output_path, stats = processor.process(
            file_paths,
            remove_text=remove_text_bool,
            remove_qr=remove_qr_bool,
            merge=merge_bool,
            compress=compress_bool
        )
        
        # 重命名输出文件
        output_filename = f"{task_id}_output.pdf"
        final_path = OUTPUT_DIR / output_filename
        os.rename(output_path, final_path)
        
        # 清理临时文件
        for fp in file_paths:
            if os.path.exists(fp):
                os.remove(fp)
        
        return ProcessResponse(
            success=True,
            task_id=task_id,
            stats=stats
        )
        
    except Exception as e:
        return ProcessResponse(success=False, error=str(e))

@app.get("/download/{task_id}")
async def download_file(request: Request, task_id: str):
    """下载处理后的文件"""
    filepath = OUTPUT_DIR / f"{task_id}_output.pdf"
    if filepath.exists():
        return FileResponse(
            filepath,
            media_type="application/pdf",
            filename="processed_pdf.pdf"
        )
    lang = request.headers.get("accept-language", "cn")
    lang = "cn" if "zh" in lang else "en"
    raise HTTPException(status_code=404, detail="文件不存在" if lang == "cn" else "File not found")

@app.get("/api/scan/{filename}")
async def scan_pdf(request: Request, filename: str):
    """扫描PDF，分析水印情况"""
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        lang = request.headers.get("accept-language", "cn")
        lang = "cn" if "zh" in lang else "en"
        raise HTTPException(status_code=404, detail="文件不存在" if lang == "cn" else "File not found")
    
    result = processor.scan_pdf(str(filepath))
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
