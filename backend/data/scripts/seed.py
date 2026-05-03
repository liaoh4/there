"""
Seed script — insert ~20 Chinese university majors with RIASEC profiles.

Run from the backend directory:
    python data/scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# 把 backend/ 加入模块搜索路径，确保 app.* 可以被 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.major import Major

settings = get_settings()

# fmt: off
MAJORS = [
    # (code,  name,              discipline,   category,     description,                          R,    I,    A,    S,    E,    C)
    ("CS001", "计算机科学与技术", "工学",       "计算机类",   "研究计算机系统设计、软件开发与算法",  0.30, 0.90, 0.20, 0.20, 0.35, 0.70),
    ("CS002", "软件工程",        "工学",       "计算机类",   "面向工程实践的软件设计与开发",        0.30, 0.80, 0.25, 0.25, 0.40, 0.75),
    ("CS003", "人工智能",        "工学",       "计算机类",   "机器学习、深度学习与智能系统研究",    0.25, 0.95, 0.30, 0.20, 0.35, 0.60),
    ("EE001", "电气工程",        "工学",       "电气类",     "电力系统、电机与控制工程",            0.80, 0.75, 0.20, 0.20, 0.35, 0.60),
    ("ME001", "机械工程",        "工学",       "机械类",     "机械设计、制造与自动化",              0.85, 0.70, 0.30, 0.20, 0.35, 0.55),
    ("AR001", "建筑学",          "工学",       "建筑类",     "建筑设计、城市规划与空间艺术",        0.55, 0.60, 0.85, 0.30, 0.45, 0.50),
    ("DE001", "视觉传达设计",    "艺术学",     "设计学类",   "平面设计、品牌视觉与用户界面设计",    0.25, 0.45, 0.95, 0.40, 0.50, 0.35),
    ("DE002", "工业设计",        "工学",       "机械类",     "产品外观、人机交互与工程美学",        0.50, 0.60, 0.90, 0.30, 0.45, 0.40),
    ("ME002", "临床医学",        "医学",       "临床医学类", "疾病诊断、治疗与患者护理",            0.30, 0.85, 0.20, 0.75, 0.40, 0.55),
    ("NU001", "护理学",          "医学",       "护理学类",   "患者护理、健康教育与医疗协作",        0.30, 0.60, 0.25, 0.90, 0.35, 0.55),
    ("SW001", "社会工作",        "法学",       "社会学类",   "社会服务、弱势群体支持与社区发展",    0.20, 0.40, 0.35, 0.95, 0.55, 0.40),
    ("PS001", "心理学",          "理学",       "心理学类",   "人类行为、认知与心理健康研究",        0.20, 0.80, 0.40, 0.80, 0.40, 0.45),
    ("ED001", "教育学",          "教育学",     "教育学类",   "教学理论、课程设计与教育管理",        0.20, 0.65, 0.40, 0.85, 0.50, 0.55),
    ("BA001", "工商管理",        "管理学",     "工商管理类", "企业运营、战略管理与商业决策",        0.25, 0.55, 0.35, 0.55, 0.85, 0.70),
    ("BA002", "市场营销",        "管理学",     "工商管理类", "消费者行为、品牌推广与市场策略",      0.20, 0.50, 0.55, 0.65, 0.90, 0.55),
    ("FI001", "金融学",          "经济学",     "金融学类",   "金融市场、投资分析与风险管理",        0.20, 0.75, 0.25, 0.35, 0.80, 0.85),
    ("LA001", "法学",            "法学",       "法学类",     "法律体系、司法程序与权益保障",        0.20, 0.70, 0.30, 0.55, 0.80, 0.65),
    ("CH001", "汉语言文学",      "文学",       "中国语言文学类", "文学理论、语言学与文化研究",      0.15, 0.65, 0.75, 0.55, 0.40, 0.45),
    ("EN001", "英语",            "文学",       "外国语言文学类", "英语语言、跨文化交际与翻译",      0.15, 0.60, 0.65, 0.70, 0.45, 0.50),
    ("BI001", "生物科学",        "理学",       "生物科学类", "生命科学基础研究与生物技术",          0.40, 0.90, 0.30, 0.45, 0.30, 0.50),
]
# fmt: on


async def seed(session: AsyncSession) -> None:
    existing = await session.execute(select(Major))
    if existing.scalars().first():
        print("数据库已有专业数据，跳过 seed。")
        return

    for code, name, discipline, category, desc, r, i, a, s, e, c in MAJORS:
        session.add(Major(
            code=code,
            name=name,
            discipline_category=discipline,
            major_category=category,
            description=desc,
            riasec_r=r,
            riasec_i=i,
            riasec_a=a,
            riasec_s=s,
            riasec_e=e,
            riasec_c=c,
        ))

    await session.flush()
    print(f"成功插入 {len(MAJORS)} 个专业。")


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
