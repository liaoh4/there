from openai import AsyncOpenAI
from app.config import get_settings
settings = get_settings()

client = AsyncOpenAI(
    api_key = settings.DEEPSEEK_API_KEY,
    base_url = "https://api.deepseek.com"
)
RIASEC_DIMENSIONS = {
    "R": "现实型",
    "I": "研究型",
    "A": "艺术型",
    "S": "社会型",
    "E": "企业型",
    "C": "常规型"
}

INTEREST_CATEGORY_NAMES = {
  "02": "艺术与人文",
  "03": "社会科学",
  "04": "商业管理与法律",
  "05": "自然科学与数学",
  "06": "信息与通信技术",
  "07A": "机械·制造·自动化",
  "07B": "电气·能源·核",
  "07C": "土木·水利·测绘",
  "07D": "建筑·规划·景观",
  "07E": "化工·材料·轻工",
  "07F": "交通·物流·安全",
  "07G": "航空·海洋",
  "07H": "环境·资源",
  "07I": "生命工程",
  "07J": "国防安全",
  "08": "农林渔业与兽医",
  "09": "医学与健康",
  "11": "计算机科学",
}

def build_prompt(riasec_scores: dict, recommendations: list, interest_scores: dict) -> str:

    interst_lists = [(a,b) for a,b in interest_scores.items()]
    interst_lists.sort(key=lambda x: x[1], reverse=True)
    top_interests = [f"{INTEREST_CATEGORY_NAMES.get(code, code)}" for code , _ in interst_lists[:3]]
    recommended_majors = [rec['major']['name'] for rec in recommendations]
    riasec_lists = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    top_riasec = [RIASEC_DIMENSIONS.get(dim, dim) for dim, _ in riasec_lists[:2]]


    return f"""用户RIASEC优势维度: {"、".join(top_riasec)}
用户兴趣:{"、".join(top_interests)}
推荐专业:{"、".join(recommended_majors)}
请解释为什么用户应该选择这些专业，分析理由、兴趣联系和就业前景
"""
async def generate_interpretation(riasec_scores: dict, recommendations: list, interest_scores: dict) -> str:
    prompt = build_prompt(riasec_scores, recommendations, interest_scores)
    response = await client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role": "system", "content": "你是张雪峰，著名高考志愿填报专家。风格直接、幽默、接地气。输出不超过400字，不使用任何Markdown格式，直接输出纯文字。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 1000,
        temperature = 0.7,
        top_p = 0.9,
        n = 1,
        stop = None,
        stream = True,
    )
    interpretation = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            interpretation += chunk.choices[0].delta.content
    return interpretation.strip()   

