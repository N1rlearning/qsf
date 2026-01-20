#!/usr/bin/env python3
"""
PDF处理器 - 水印移除、合并、压缩
支持中英文双语水印识别
"""

import os
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
import io

class PDFProcessor:
    """PDF处理器类"""
    
    def __init__(self):
        # 中文水印关键词
        self.zh_keywords = ['全能', '扫描', '创建', '王']
        # 英文水印关键词
        self.en_keywords = ['CamScanner', 'Scanned with', 'Created by', 'scan']
    
    def process(self, file_paths, remove_text=True, remove_qr=True, merge=True, compress=True):
        """
        处理PDF文件
        
        Args:
            file_paths: PDF文件路径列表
            remove_text: 是否移除文字水印
            remove_qr: 是否移除二维码
            merge: 是否合并PDF
            compress: 是否压缩输出
        
        Returns:
            output_path: 输出文件路径
            stats: 处理统计信息
        """
        total_pages = 0
        total_watermarks = 0
        
        # 处理每个PDF
        processed_pdfs = []
        
        for i, filepath in enumerate(file_paths):
            print(f"处理文件 {i+1}/{len(file_paths)}: {os.path.basename(filepath)}")
            
            # 移除水印
            clean_path = self._remove_watermarks(
                filepath,
                remove_text=remove_text,
                remove_qr=remove_qr
            )
            
            # 统计
            doc = fitz.open(clean_path)
            total_pages += len(doc)
            doc.close()
            
            # 如果不合并，直接返回第一个文件
            if not merge and i == 0:
                return clean_path, {
                    'pages': total_pages,
                    'files': len(file_paths),
                    'watermarks': total_watermarks,
                    'size_mb': os.path.getsize(clean_path) / (1024 * 1024)
                }
            
            processed_pdfs.append(clean_path)
        
        # 合并PDF
        if merge and len(processed_pdfs) > 1:
            merged_path = self._merge_pdfs(processed_pdfs)
            
            # 清理临时文件
            for fp in processed_pdfs:
                if os.path.exists(fp) and fp != merged_path:
                    os.remove(fp)
            
            # 压缩
            if compress:
                final_path = self._compress_pdf(merged_path)
                os.remove(merged_path)
            else:
                final_path = merged_path
        else:
            final_path = processed_pdfs[0]
        
        # 计算最终统计
        size_mb = os.path.getsize(final_path) / (1024 * 1024)
        
        return final_path, {
            'pages': total_pages,
            'files': len(file_paths),
            'watermarks': total_watermarks,
            'size_mb': round(size_mb, 2)
        }
    
    def _remove_watermarks(self, input_path, remove_text=True, remove_qr=True):
        """
        移除PDF中的水印
        
        Args:
            input_path: 输入PDF路径
            remove_text: 是否移除文字水印
            remove_qr: 是否移除二维码
        
        Returns:
            输出文件路径
        """
        doc = fitz.open(input_path)
        watermarks_removed = 0
        
        for page_num, page in enumerate(doc):
            page_width = page.rect.width
            page_height = page.rect.height
            
            # 1. 移除文字水印
            if remove_text:
                # 获取页面所有文本
                text = page.get_text("text")
                
                # 检查是否包含水印关键词（中英文）
                has_watermark = any(kw.lower() in text.lower() for kw in self.zh_keywords + self.en_keywords)
                
                if has_watermark:
                    # 在右下角区域绘制白色矩形覆盖水印
                    watermark_rect = fitz.Rect(
                        page_width * 0.45,
                        page_height * 0.88,
                        page_width - 5,
                        page_height - 5
                    )
                    page.draw_rect(watermark_rect, color=(1, 1, 1), fill=(1, 1, 1))
                    watermarks_removed += 1
            
            # 2. 移除二维码
            if remove_qr:
                images = page.get_images()
                
                for img_index, img in enumerate(images):
                    xref = img[0]
                    img_width = img[2]
                    img_height = img[3]
                    
                    rects = page.get_image_rects(xref)
                    
                    for rect in rects:
                        rel_x = rect.x0 / page_width
                        rel_y = rect.y0 / page_height
                        rel_width = rect.width / page_width
                        rel_height = rect.height / page_height
                        area = rect.width * rect.height
                        
                        is_bottom_right = rel_y > 0.7 and rel_x > 0.65
                        is_small = area < 20000
                        is_very_small_height = rel_height < 0.12
                        
                        if is_bottom_right and is_small and is_very_small_height:
                            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                            watermarks_removed += 1
            
            # 额外处理：直接覆盖右下角区域
            if remove_text or remove_qr:
                text_watermark_rect = fitz.Rect(
                    page_width * 0.5,
                    page_height * 0.85,
                    page_width - 2,
                    page_height - 2
                )
                page.draw_rect(text_watermark_rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                qr_rect = fitz.Rect(
                    page_width * 0.75,
                    page_height * 0.85,
                    page_width - 2,
                    page_height - 2
                )
                page.draw_rect(qr_rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # 保存处理后的PDF
        output_path = input_path.replace('.pdf', '_clean.pdf')
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        print(f"  移除水印: {watermarks_removed} 个")
        
        return output_path
    
    def _merge_pdfs(self, file_paths):
        """合并多个PDF文件"""
        pdf_writer = PdfWriter()
        
        for filepath in file_paths:
            if os.path.exists(filepath):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    pdf_writer.add_page(page)
                print(f"  已合并: {os.path.basename(filepath)}")
        
        output_path = file_paths[0].replace('.pdf', '_merged.pdf')
        with open(output_path, 'wb') as f:
            pdf_writer.write(f)
        
        print(f"  合并完成: {len(file_paths)} 个文件")
        
        return output_path
    
    def _compress_pdf(self, input_path):
        """压缩PDF文件"""
        output_path = input_path.replace('.pdf', '_compressed.pdf')
        
        gs_cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/prepress',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]
        
        try:
            import subprocess
            subprocess.run(gs_cmd, check=True)
            print(f"  压缩完成")
            return output_path
        except subprocess.CalledProcessError:
            print(f"  压缩跳过（Ghostscript不可用）")
            return input_path
    
    def scan_pdf(self, input_path):
        """扫描PDF，分析水印情况"""
        doc = fitz.open(input_path)
        result = {
            'pages': len(doc),
            'images': 0,
            'has_text_watermark': False,
            'has_qr_watermark': False,
            'text_details': [],
            'image_details': []
        }
        
        for page_num, page in enumerate(doc):
            page_width = page.rect.width
            page_height = page.rect.height
            
            text = page.get_text("text")
            if any(kw.lower() in text.lower() for kw in self.zh_keywords + self.en_keywords):
                result['has_text_watermark'] = True
            
            images = page.get_images()
            result['images'] += len(images)
            
            for img in images:
                xref = img[0]
                img_width = img[2]
                img_height = img[3]
                
                rects = page.get_image_rects(xref)
                for rect in rects:
                    rel_x = rect.x0 / page_width
                    rel_y = rect.y0 / page_height
                    area = rect.width * rect.height
                    
                    is_bottom_right = rel_y > 0.7 and rel_x > 0.65
                    is_small = area < 20000
                    
                    if is_bottom_right and is_small:
                        result['has_qr_watermark'] = True
                        result['image_details'].append({
                            'page': page_num + 1,
                            'position': f'({rel_x:.2f}, {rel_y:.2f})',
                            'size': f'{rect.width:.0f}x{rect.height:.0f}'
                        })
        
        if doc[0]:
            blocks = doc[0].get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if len(text) < 30 and len(text) > 1:
                                result['text_details'].append({
                                    'text': text,
                                    'size': span.get("size", 0)
                                })
        
        doc.close()
        
        return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_processor.py <pdf文件>")
        sys.exit(1)
    
    processor = PDFProcessor()
    result = processor.scan_pdf(sys.argv[1])
    
    print("\n=== PDF分析结果 ===")
    print(f"页数: {result['pages']}")
    print(f"图像数量: {result['images']}")
    print(f"文字水印: {'是' if result['has_text_watermark'] else '否'}")
    print(f"二维码水印: {'是' if result['has_qr_watermark'] else '否'}")
    
    if result['text_details']:
        print("\n短文本块:")
        for item in result['text_details'][:5]:
            print(f"  - '{item['text']}' (大小: {item['size']})")
    
    if result['image_details']:
        print("\n可疑图像:")
        for item in result['image_details']:
            print(f"  页面 {item['page']}: 位置 {item['position']}, 尺寸 {item['size']}")
