from openai import AsyncOpenAI
from app.config import get_settings
settings = get_settings()

client = AsyncOpenAI(
    api_key = settings.DEEPSEEK_API_KEY,
    base_url = "https://api.deepseek.com"
)

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
    top_interests = [f"{INTEREST_CATEGORY_NAMES.get(code, code)}: {score:.2f}" for code, score in interst_lists[:3]]
    recommended_majors = [rec['major']['name'] for rec in recommendations]

    return f"""
            用户RIASEC分数:R={riasec_scores['R']}, I={riasec_scores['I']}, A={riasec_scores['A']}, S={riasec_scores['S']}, E={riasec_scores['E']}, C={riasec_scores['C']}
            用户感兴趣的专业为:{top_interests}, 分数越高兴趣越浓
            综合用户的RIASEC分数和兴趣偏好,推荐的专业有:{recommended_majors}
            请根据以上信息生成一份分析报告，包含：
            1. 用户的性格特点分析
            2. 为什么推荐这些专业
            3. 兴趣与推荐是否吻合的分析
            """
async def generate_interpretation(riasec_scores: dict, recommendations: list, interest_scores: dict) -> str:
    prompt = build_prompt(riasec_scores, recommendations, interest_scores)
    response = await client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role": "system", "content": "你是一个职业规划专家，帮助用户分析职业兴趣和推荐的专业。"},
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

