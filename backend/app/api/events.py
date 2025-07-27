from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import requests
import re
from bs4 import BeautifulSoup
import os
import hashlib
from urllib.parse import urljoin, urlparse

from ..database import get_db, Event as DBEvent, Tag as DBTag, User
from ..core.dependencies import get_current_active_user
from ..models import (
    Event,
    EventCreate,
    EventUpdate,
    TimelineResponse,
    SearchRequest,
    Tag,
)
from ..services.tag_extractor import TagExtractor

router = APIRouter(prefix="/api/events", tags=["events"])
tag_extractor = TagExtractor()


def split_tags(tags_string: str) -> List[str]:
    """分割标签字符串，支持中英文逗号和分号"""
    if not tags_string:
        return []

    # 使用正则表达式分割，支持中英文逗号和分号
    import re

    tags = re.split(r"[,，;；]", tags_string)

    # 清理空白字符并过滤空字符串
    return [tag.strip() for tag in tags if tag.strip()]


@router.post("/", response_model=Event)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建新事件"""

    # 自动提取标签
    full_text = f"{event.title} {event.description or ''}"
    extracted_tags = tag_extractor.extract_tags(full_text)

    # 自动推断分类
    auto_category = tag_extractor.get_category(extracted_tags)

    # 自动评估重要性
    impact_score = tag_extractor.get_importance_score(full_text)

    # 合并用户提供的标签和自动提取的标签
    user_tags = split_tags(event.tags or "")
    all_tags = list(set(user_tags + extracted_tags))

    db_event = DBEvent(
        title=event.title,
        description=event.description,
        event_date=event.event_date or datetime.utcnow(),
        tags=",".join(all_tags),
        category=event.category or auto_category,
        impact_score=impact_score,
        user_id=current_user.id,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # 保存新标签到标签表
    for tag_name in all_tags:
        existing_tag = db.query(DBTag).filter(DBTag.name == tag_name).first()
        if not existing_tag:
            db_tag = DBTag(name=tag_name, category=auto_category)
            db.add(db_tag)

    db.commit()
    return db_event


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取时间线事件"""
    # 临时包含没有user_id的历史数据
    query = db.query(DBEvent).filter(
        (DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None))
    )

    if category:
        query = query.filter(DBEvent.category == category)

    # 按事件日期降序排列
    query = query.order_by(DBEvent.event_date.desc())

    # 分页
    total = query.count()
    events = query.offset((page - 1) * size).limit(size).all()

    return TimelineResponse(events=events, total=total, page=page, size=size)


@router.get("/search", response_model=List[Event])
def search_events(
    query: Optional[str] = None,
    tags: Optional[str] = Query(None, description="逗号分隔的标签"),
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    impact_level: Optional[str] = Query(
        None, description="影响力级别: high, medium, low"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """搜索事件"""
    # 临时包含没有user_id的历史数据
    db_query = db.query(DBEvent).filter(
        (DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None))
    )

    if query:
        db_query = db_query.filter(
            (DBEvent.title.contains(query)) | (DBEvent.description.contains(query))
        )

    if tags:
        tag_list = split_tags(tags)
        for tag in tag_list:
            db_query = db_query.filter(DBEvent.tags.contains(tag))

    if category:
        db_query = db_query.filter(DBEvent.category == category)

    if start_date:
        db_query = db_query.filter(DBEvent.event_date >= start_date)

    if end_date:
        db_query = db_query.filter(DBEvent.event_date <= end_date)

    if impact_level:
        if impact_level == "high":
            db_query = db_query.filter(DBEvent.impact_score >= 7)
        elif impact_level == "medium":
            db_query = db_query.filter(
                DBEvent.impact_score >= 4, DBEvent.impact_score < 7
            )
        elif impact_level == "low":
            db_query = db_query.filter(DBEvent.impact_score < 4)

    return db_query.order_by(DBEvent.event_date.desc()).limit(50).all()


@router.get("/{event_id}", response_model=Event)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取单个事件"""
    # 临时包含没有user_id的历史数据
    event = (
        db.query(DBEvent)
        .filter(
            DBEvent.id == event_id,
            (DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None)),
        )
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="事件未找到")
    return event


@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新事件"""
    # 临时包含没有user_id的历史数据
    db_event = (
        db.query(DBEvent)
        .filter(
            DBEvent.id == event_id,
            (DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None)),
        )
        .first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="事件未找到")

    update_data = event.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除事件"""
    # 临时包含没有user_id的历史数据
    db_event = (
        db.query(DBEvent)
        .filter(
            DBEvent.id == event_id,
            (DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None)),
        )
        .first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="事件未找到")

    db.delete(db_event)
    db.commit()
    return {"message": "事件已删除"}


@router.get("/stats/categories")
def get_categories_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """获取分类统计"""
    from sqlalchemy import func

    # 临时包含没有user_id的历史数据
    stats = (
        db.query(DBEvent.category, func.count(DBEvent.id))
        .filter((DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None)))
        .group_by(DBEvent.category)
        .all()
    )
    return [{"category": category, "count": count} for category, count in stats]


@router.get("/stats/timeline")
def get_timeline_stats(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """获取时间线统计"""
    from sqlalchemy import func, extract

    # 按月统计
    monthly_stats = (
        db.query(
            extract("year", DBEvent.event_date).label("year"),
            extract("month", DBEvent.event_date).label("month"),
            func.count(DBEvent.id).label("count"),
        )
        .filter((DBEvent.user_id == current_user.id) | (DBEvent.user_id.is_(None)))
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    return [
        {
            "year": int(year),
            "month": int(month),
            "count": count,
            "date": f"{int(year)}-{int(month):02d}",
        }
        for year, month, count in monthly_stats
    ]


# 微信公众号提取请求模型
class WechatExtractRequest(BaseModel):
    url: str


# 微信公众号提取响应模型
class WechatExtractResponse(BaseModel):
    title: str
    content: str
    images: List[str] = []


@router.post("/extract-wechat", response_model=WechatExtractResponse)
def extract_wechat_content(
    request: WechatExtractRequest, current_user: User = Depends(get_current_active_user)
):
    """从微信公众号链接提取内容"""
    url = request.url

    # 验证URL格式
    if "mp.weixin.qq.com" not in url:
        raise HTTPException(status_code=400, detail="不是有效的微信公众号文章链接")

    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # 发送HTTP请求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 提取标题
        title = ""
        title_selectors = [
            "h1#activity-name",  # 微信公众号文章标题的常见选择器
            "h1.rich_media_title",
            "h2#activity-name",
            "h2.rich_media_title",
            ".rich_media_title",
            "h1",
            "title",
        ]

        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text().strip()
                break

        # 提取正文内容
        content = ""
        content_selectors = [
            "#js_content",  # 微信公众号文章内容的主要选择器
            ".rich_media_content",
            "#img-content",
            ".rich_media_area_primary",
            "article",
            ".content",
        ]

        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # 清理HTML标签，只保留文本
                content = content_element.get_text(separator="\n", strip=True)
                # 清理多余的空白字符
                content = re.sub(r"\n+", "\n", content)
                content = re.sub(r"\s+", " ", content)
                break

        # 提取图片链接
        images = []
        img_elements = soup.find_all("img")
        for img in img_elements:
            img_src = img.get("src") or img.get("data-src")
            if img_src:
                # 确保是完整的URL
                if img_src.startswith("http"):
                    images.append(img_src)
                elif img_src.startswith("//"):
                    images.append("https:" + img_src)

        # 限制图片数量，避免过多
        images = images[:10]

        # 清理提取的内容，去除空白字符
        title = title.strip() if title else ""
        content = content.strip() if content else ""

        # 如果没有提取到有效内容，返回错误
        if not title and not content:
            raise HTTPException(
                status_code=400, detail="无法从该链接提取有效内容，请检查链接是否可访问"
            )

        # 如果只有很少的内容，也认为提取失败
        if len(title) < 5 and len(content) < 20:
            raise HTTPException(
                status_code=400,
                detail="提取到的内容过少，可能是链接已失效或需要登录访问",
            )

        return WechatExtractResponse(
            title=title[:200] if title else "",  # 限制标题长度，不使用占位符
            content=content[:1000] if content else "",  # 限制内容长度，不使用占位符
            images=images,
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"网络请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内容提取失败: {str(e)}")
