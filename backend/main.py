# -*- coding: utf-8 -*-
"""
GetMail v2 后端 API

提供 Exchange 邮件读取和发送功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from exchangelib import (
    Account, Credentials, Configuration, 
    FileAttachment, DELEGATE, Message, Mailbox
)
import re

app = FastAPI(
    title="GetMail v2 API",
    description="Exchange 邮件读取与发送工具 API",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局账户缓存
accounts = {}


# ==================== 请求模型 ====================

class LoginRequest(BaseModel):
    username: str
    credential: str  # 密码或 NTLM Hash
    email: str
    server: Optional[str] = None
    ews_url: Optional[str] = None  # 完整的 EWS 地址，如 https://mail.example.com/EWS/Exchange.asmx
    use_autodiscover: bool = True


class FolderListRequest(BaseModel):
    session_id: str


class MailListRequest(BaseModel):
    session_id: str
    folder: str = "Inbox"
    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None


class MailDetailRequest(BaseModel):
    session_id: str
    mail_id: str


class DownloadAttachmentRequest(BaseModel):
    session_id: str
    mail_id: str
    attachment_name: str


class SendMailRequest(BaseModel):
    session_id: str
    to: List[str]
    cc: Optional[List[str]] = []
    bcc: Optional[List[str]] = []
    subject: str
    body: str
    attachments: Optional[List[str]] = []  # 文件路径列表


# ==================== 工具函数 ====================

def parse_ntlm_hash(credential: str) -> tuple:
    """解析 NTLM Hash"""
    if ':' in credential:
        parts = credential.split(':')
        return parts[1]
    else:
        return credential


def get_account(session_id: str) -> Account:
    """获取账户"""
    if session_id not in accounts:
        raise HTTPException(status_code=401, detail="未登录或会话已过期")
    return accounts[session_id]


# ==================== API 端点 ====================

@app.post("/api/login")
async def login(request: LoginRequest):
    """登录 Exchange"""
    try:
        # 判断是密码还是 NTLM Hash
        if len(request.credential) == 32:
            # NTLM Hash
            nt_hash = parse_ntlm_hash(request.credential)
            print(request.username)
            print("00000000000000000000000000000000:"+nt_hash)
            creds = Credentials(request.username, "00000000000000000000000000000000:"+nt_hash)
        else:
            # 明文密码
            creds = Credentials(username=request.username, password=request.credential)
        
        # 配置
        
        if request.use_autodiscover:
            account = Account(
                primary_smtp_address=request.email,
                credentials=creds,
                autodiscover=True,
                access_type=DELEGATE
            )
        else:
            # 优先使用完整的 EWS URL
            if request.ews_url:
                config = Configuration(
                    service_endpoint=request.ews_url,
                    credentials=creds
                )
            elif request.server:
                config = Configuration(
                    server=request.server,
                    credentials=creds
                )
            else:
                raise HTTPException(status_code=400, detail="未指定邮件服务器地址或 EWS URL")

            account = Account(
                primary_smtp_address=request.email,
                config=config,
                autodiscover=False,
                access_type=DELEGATE
            )
        
        # 生成会话 ID
        import uuid
        session_id = str(uuid.uuid4())
        accounts[session_id] = account
        
        return {
            "success": True,
            "session_id": session_id,
            "email": request.email,
            "message": "登录成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/logout")
async def logout(session_id: str):
    """登出"""
    if session_id in accounts:
        del accounts[session_id]
    return {"success": True, "message": "已登出"}


@app.post("/api/folders")
async def list_folders(request: FolderListRequest):
    """列出所有邮件文件夹"""
    try:
        account = get_account(request.session_id)
        folders = []
        
        for folder in account.root.walk():
            folders.append({
                "name": folder.name,
                "path": folder.absolute,
                "total_count": folder.total_count,
                "unread_count": folder.unread_count,
                "is_distinguished": folder.is_distinguished
            })
        
        return {"success": True, "folders": folders}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/mails")
async def list_mails(request: MailListRequest):
    """列出邮件"""
    try:
        account = get_account(request.session_id)

        # 获取文件夹 - 使用更智能的匹配方式
        folder = None

        # 先尝试通过 distinguished folder 属性获取
        folder_lower = (request.folder or 'inbox').lower()
        distinguished_attrs = {
            'inbox': 'inbox',
            'sent': 'sent',
            'drafts': 'drafts',
            'junk': 'junk',
            'outbox': 'outbox',
            'deleteditems': 'trash',
            'trash': 'trash',
        }

        if folder_lower in distinguished_attrs:
            attr_name = distinguished_attrs[folder_lower]
            folder = getattr(account, attr_name, None)

        # 如果没找到，遍历所有文件夹
        if not folder:
            for f in account.root.walk():
                if f.name == request.folder or (f.absolute and request.folder in f.absolute):
                    folder = f
                    break

        # 默认使用收件箱
        if not folder:
            folder = account.inbox

        # 查询邮件
        query = folder.all()
        
        # 关键字搜索
        if request.keyword:
            query = query.filter(subject__icontains=request.keyword) | \
                    query.filter(body__icontains=request.keyword)
        
        # 分页
        offset = (request.page - 1) * request.page_size
        mails = query.order_by('-datetime_received')[offset:offset + request.page_size]
        
        total = query.count()
        
        result = []
        for mail in mails:
            result.append({
                "id": str(mail.id),
                "subject": mail.subject,
                "sender": str(mail.sender) if mail.sender else "",
                "received": mail.datetime_received.isoformat() if mail.datetime_received else "",
                "is_read": mail.is_read,
                "has_attachments": mail.has_attachments,
                "importance": str(mail.importance)
            })
        
        return {
            "success": True,
            "mails": result,
            "total": total,
            "page": request.page,
            "page_size": request.page_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/mail/detail")
async def get_mail_detail(request: MailDetailRequest):
    """获取邮件详情"""
    try:
        account = get_account(request.session_id)
        
        # 查找邮件
        mail = account.inbox.get(id=request.mail_id)
        if not mail:
            for folder in account.root.walk():
                try:
                    mail = folder.get(id=request.mail_id)
                    if mail:
                        break
                except:
                    continue
        
        if not mail:
            raise HTTPException(status_code=404, detail="邮件不存在")
        
        # 获取附件列表
        attachments = []
        if mail.attachments:
            for att in mail.attachments:
                if isinstance(att, FileAttachment):
                    attachments.append({
                        "name": att.name,
                        "size": att.size,
                        "type": att.content_type
                    })
        
        return {
            "success": True,
            "mail": {
                "id": mail.id,
                "subject": mail.subject,
                "sender": {
                    "name": mail.sender.name if mail.sender else "",
                    "email": mail.sender.email_address if mail.sender else ""
                },
                "to": [{"name": r.name, "email": r.email_address} for r in mail.to_recipients or []],
                "cc": [{"name": r.name, "email": r.email_address} for r in mail.cc_recipients or []],
                "bcc": [{"name": r.name, "email": r.email_address} for r in mail.bcc_recipients or []],
                "received": mail.datetime_received.isoformat() if mail.datetime_received else "",
                "body": mail.body,
                "attachments": attachments
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/attachment/download")
async def download_attachment(request: DownloadAttachmentRequest):
    """下载附件"""
    try:
        account = get_account(request.session_id)
        
        # 查找邮件
        mail = None
        for folder in account.root.walk():
            try:
                mail = folder.get(id=request.mail_id)
                if mail:
                    break
            except:
                continue
        
        if not mail or not mail.attachments:
            raise HTTPException(status_code=404, detail="邮件或附件不存在")
        
        # 查找附件
        for att in mail.attachments:
            if isinstance(att, FileAttachment) and att.name == request.attachment_name:
                # 返回 base64 编码的附件内容
                import base64
                att_data = base64.b64encode(att.content).decode()
                return {
                    "success": True,
                    "name": att.name,
                    "type": att.content_type,
                    "data": att_data
                }
        
        raise HTTPException(status_code=404, detail="附件不存在")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/mail/send")
async def send_mail(request: SendMailRequest):
    """发送邮件"""
    try:
        account = get_account(request.session_id)
        
        # 创建邮件
        message = Message(
            account=account,
            subject=request.subject,
            body=request.body,
            to_recipients=[Mailbox(email_address=email) for email in request.to],
            cc_recipients=[Mailbox(email_address=email) for email in request.cc],
            bcc_recipients=[Mailbox(email_address=email) for email in request.bcc]
        )
        
        # 添加附件
        for file_path in request.attachments:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    attachment = FileAttachment(
                        name=os.path.basename(file_path),
                        content=f.read()
                    )
                    message.attach(attachment)
        
        # 发送
        message.send()
        
        return {"success": True, "message": "邮件发送成功"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="127.0.0.1", port=8001)
