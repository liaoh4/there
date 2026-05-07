import type { RiasecDimension } from "./types"

export interface Question {
  id: string
  dimension: RiasecDimension
  intensity: "低" | "中" | "高"
  text: string
}

// Full 96-question bank: 16 per dimension (4 低, 6 中, 6 高)
export const QUESTION_BANK: Question[] = [
  // ── R 实践型 ──────────────────────────────────────────────────────────────
  { id: "R001", dimension: "R", intensity: "低", text: "我不排斥需要动手操作的任务，比如实验或手工制作" },
  { id: "R002", dimension: "R", intensity: "低", text: "比起只看理论，我更喜欢能亲身体验和操作的学习方式" },
  { id: "R003", dimension: "R", intensity: "低", text: "体育课、实验课或劳技课让我觉得比纯理论课更有意思" },
  { id: "R004", dimension: "R", intensity: "低", text: "看到别人在修东西或搭建结构时，我会觉得有趣并想了解" },
  { id: "R005", dimension: "R", intensity: "中", text: "家里东西坏了，我会先尝试自己研究怎么修，而不是马上找人来修" },
  { id: "R006", dimension: "R", intensity: "中", text: "我喜欢用双手做出一件完整的成品，比如手工艺品、模型或装置" },
  { id: "R007", dimension: "R", intensity: "中", text: "我对机器、电子设备或工具的内部构造感到好奇" },
  { id: "R008", dimension: "R", intensity: "中", text: "我更喜欢在户外或做实际操作，而不是长时间坐着读书写字" },
  { id: "R009", dimension: "R", intensity: "中", text: "做实验时我比单纯听讲更专注投入，更能进入状态" },
  { id: "R010", dimension: "R", intensity: "中", text: "我喜欢户外运动、农业体验或与大自然直接接触的活动" },
  { id: "R011", dimension: "R", intensity: "高", text: "我经常主动拆解或研究身边的设备，想弄清楚它们是怎么运作的" },
  { id: "R012", dimension: "R", intensity: "高", text: "我每周会花几个小时在制作、修理或搭建东西上，乐此不疲" },
  { id: "R013", dimension: "R", intensity: "高", text: "给我一堆材料或零件，我能专注地把它们做成有用的东西并感到满足" },
  { id: "R014", dimension: "R", intensity: "高", text: "我觉得亲手造出一件实物比写一篇文章或做一份报告更有成就感" },
  { id: "R015", dimension: "R", intensity: "高", text: "如果可以自由选择，我宁愿在工坊或实验室工作，而不是坐在办公室" },
  { id: "R016", dimension: "R", intensity: "高", text: "一天不动手做点什么，我就会觉得这天过得有些空虚" },
  // ── I 研究型 ──────────────────────────────────────────────────────────────
  { id: "I001", dimension: "I", intensity: "低", text: "遇到不懂的问题，我会主动去查资料或深入研究直到弄清楚" },
  { id: "I002", dimension: "I", intensity: "低", text: "我喜欢数学、物理或生物这类需要推理和逻辑分析的学科" },
  { id: "I003", dimension: "I", intensity: "低", text: "看到一个有趣的自然现象或社会问题，我会想知道背后的原因" },
  { id: "I004", dimension: "I", intensity: "低", text: "科普文章、纪录片或学术视频对我的吸引力不亚于一般娱乐内容" },
  { id: "I005", dimension: "I", intensity: "中", text: "我享受分析和解决复杂的逻辑或数学难题，即使很费脑也不觉得烦" },
  { id: "I006", dimension: "I", intensity: "中", text: "比起记住结论，我更想理解「为什么」是这样以及背后的原理" },
  { id: "I007", dimension: "I", intensity: "中", text: "我喜欢独立思考问题，不急于问别人答案，享受自己推导的过程" },
  { id: "I008", dimension: "I", intensity: "中", text: "我会对某个主题产生浓厚兴趣，然后花时间深入研究它" },
  { id: "I009", dimension: "I", intensity: "中", text: "解开一道难题带给我的满足感超过其他大多数课内外活动" },
  { id: "I010", dimension: "I", intensity: "中", text: "我会从多个角度分析同一个问题，不轻易满足于表面解释" },
  { id: "I011", dimension: "I", intensity: "高", text: "我曾经自发地对某个科学、数学或社会问题进行长时间的深入探究" },
  { id: "I012", dimension: "I", intensity: "高", text: "我会主动阅读超出课本范围的学术材料、研究报告或专业书籍" },
  { id: "I013", dimension: "I", intensity: "高", text: "我有时会沉浸在一个抽象问题里，反复推敲很长时间而不觉得无聊" },
  { id: "I014", dimension: "I", intensity: "高", text: "如果可以选择，我更想做研究或分析类工作，而不是管理人或销售产品" },
  { id: "I015", dimension: "I", intensity: "高", text: "我能接受一个问题长时间没有明确答案，并持续保持探索的耐心" },
  { id: "I016", dimension: "I", intensity: "高", text: "我对未知领域的好奇心驱使我持续学习，哪怕没有人要求我这样做" },
  // ── A 艺术型 ──────────────────────────────────────────────────────────────
  { id: "A001", dimension: "A", intensity: "低", text: "我喜欢有创意空间、不被固定格式约束的作业或活动" },
  { id: "A002", dimension: "A", intensity: "低", text: "比起追求标准答案，我更享受自己发挥想象力的过程" },
  { id: "A003", dimension: "A", intensity: "低", text: "我对音乐、绘画、电影、文学或设计有一定的兴趣和欣赏能力" },
  { id: "A004", dimension: "A", intensity: "低", text: "我欣赏那些有独特风格、敢于与众不同的人" },
  { id: "A005", dimension: "A", intensity: "中", text: "我经常会产生创意想法，并希望通过某种方式把它们表达出来" },
  { id: "A006", dimension: "A", intensity: "中", text: "我喜欢用写作、画画、音乐、摄影或设计来表达自己的感受和想法" },
  { id: "A007", dimension: "A", intensity: "中", text: "我会注意事物的美感和风格，对视觉或听觉效果比较敏感" },
  { id: "A008", dimension: "A", intensity: "中", text: "我更喜欢灵活开放的工作方式，而不是按部就班地执行固定步骤" },
  { id: "A009", dimension: "A", intensity: "中", text: "在语文、美术或音乐相关的课程上，我比理科课程更有灵感和投入感" },
  { id: "A010", dimension: "A", intensity: "中", text: "我会欣赏并思考艺术作品或创意内容所表达的深层含义" },
  { id: "A011", dimension: "A", intensity: "高", text: "我有一个或多个持续在进行的创作爱好（写作、绘画、音乐、设计等）" },
  { id: "A012", dimension: "A", intensity: "高", text: "即使没有人要求，我也会主动进行艺术或创意类活动" },
  { id: "A013", dimension: "A", intensity: "高", text: "我不喜欢被固定规则限制我的表达方式，创作时希望完全自由发挥" },
  { id: "A014", dimension: "A", intensity: "高", text: "我对原创性和独特性的追求超过对效率和规范的重视" },
  { id: "A015", dimension: "A", intensity: "高", text: "我认为艺术创作或创意表达对我的生活不可缺少，是重要的精神需求" },
  { id: "A016", dimension: "A", intensity: "高", text: "如果可以选择，我更愿意从事需要大量创意和自我表达的工作" },
  // ── S 社会型 ──────────────────────────────────────────────────────────────
  { id: "S001", dimension: "S", intensity: "低", text: "朋友遇到困难或情绪低落时会来找我倾诉，我也愿意倾听" },
  { id: "S002", dimension: "S", intensity: "低", text: "我喜欢和同学合作完成任务，而不是总是单独行动" },
  { id: "S003", dimension: "S", intensity: "低", text: "我会主动关心班上同学的状态，留意是否有人需要帮助" },
  { id: "S004", dimension: "S", intensity: "低", text: "我喜欢倾听别人讲述他们的经历、想法和故事" },
  { id: "S005", dimension: "S", intensity: "中", text: "我愿意花时间帮助学习有困难的同学，不觉得是负担" },
  { id: "S006", dimension: "S", intensity: "中", text: "别人遇到情绪问题时，我能感同身受并给出有效的支持和安慰" },
  { id: "S007", dimension: "S", intensity: "中", text: "我喜欢组织班级活动、参与志愿服务或公益类项目" },
  { id: "S008", dimension: "S", intensity: "中", text: "我享受与不同类型的人交流，了解他们各自的想法和生活" },
  { id: "S009", dimension: "S", intensity: "中", text: "帮助他人成功解决了问题，带给我的满足感超过个人取得好成绩" },
  { id: "S010", dimension: "S", intensity: "中", text: "在团队中，我更愿意协调关系和支持大家，而不是单独冒尖" },
  { id: "S011", dimension: "S", intensity: "高", text: "我经常主动承担照顾、辅导或支持他人的角色，不计回报" },
  { id: "S012", dimension: "S", intensity: "高", text: "我会花大量时间和精力去理解他人的处境、感受和需求" },
  { id: "S013", dimension: "S", intensity: "高", text: "我觉得最有意义的工作是能直接帮助他人成长或改变生活的工作" },
  { id: "S014", dimension: "S", intensity: "高", text: "如果可以选择，我愿意从事教育、心理咨询、社会工作或医疗护理类职业" },
  { id: "S015", dimension: "S", intensity: "高", text: "看到别人在困难中获得帮助并好转，我比得到物质奖励更感到高兴" },
  { id: "S016", dimension: "S", intensity: "高", text: "我认为和谐的人际关系和帮助他人比个人成绩或排名更重要" },
  // ── E 企业型 ──────────────────────────────────────────────────────────────
  { id: "E001", dimension: "E", intensity: "低", text: "在团队活动中，我喜欢提出自己的想法和建议" },
  { id: "E002", dimension: "E", intensity: "低", text: "我不害怕在公众面前发表意见、做演讲或主持活动" },
  { id: "E003", dimension: "E", intensity: "低", text: "当别人遇到决策困难时，我会主动给出建议并推动大家行动" },
  { id: "E004", dimension: "E", intensity: "低", text: "我对商业、创业、投资或营销话题感到好奇和有兴趣" },
  { id: "E005", dimension: "E", intensity: "中", text: "我愿意担任班长、组长、活动负责人等需要协调和领导的角色" },
  { id: "E006", dimension: "E", intensity: "中", text: "我擅长在讨论中说服别人接受我的观点，并推动决策落地" },
  { id: "E007", dimension: "E", intensity: "中", text: "我喜欢设定目标并带领团队一起去实现它，享受看到成果的过程" },
  { id: "E008", dimension: "E", intensity: "中", text: "面对需要快速决策的情况，我敢于在别人犹豫时站出来做决定" },
  { id: "E009", dimension: "E", intensity: "中", text: "在讨论中，我经常自然地成为引导方向和主导节奏的那个人" },
  { id: "E010", dimension: "E", intensity: "中", text: "我对竞争环境感到兴奋，喜欢证明自己的能力超过平均水平" },
  { id: "E011", dimension: "E", intensity: "高", text: "我有强烈的成功欲望，希望在某个领域做到顶尖或有影响力" },
  { id: "E012", dimension: "E", intensity: "高", text: "我曾经自发地发起或主导过某个项目、活动或团队" },
  { id: "E013", dimension: "E", intensity: "高", text: "如果创业，我愿意承担失败的风险去追求更大的回报和影响力" },
  { id: "E014", dimension: "E", intensity: "高", text: "我的目标不只是完成任务，而是成为制定规则和方向的那个人" },
  { id: "E015", dimension: "E", intensity: "高", text: "我认为影响力和资源控制比稳定的薪资和安全感更吸引我" },
  { id: "E016", dimension: "E", intensity: "高", text: "如果可以选择，我更想创办或领导一个组织，而不是在其中执行任务" },
  // ── C 传统型 ──────────────────────────────────────────────────────────────
  { id: "C001", dimension: "C", intensity: "低", text: "我会把笔记或资料整理得比较有条理，方便日后查阅" },
  { id: "C002", dimension: "C", intensity: "低", text: "完成一张待办清单让我感到踏实和满足" },
  { id: "C003", dimension: "C", intensity: "低", text: "我做事倾向于按计划进行，而不是随机应变或临时发挥" },
  { id: "C004", dimension: "C", intensity: "低", text: "我比较喜欢有明确要求和规则的任务，不太喜欢模棱两可的情况" },
  { id: "C005", dimension: "C", intensity: "中", text: "我会提前规划时间，把任务分解成具体步骤再逐一完成" },
  { id: "C006", dimension: "C", intensity: "中", text: "我能长时间专注于需要精确和细心的任务，不觉得枯燥" },
  { id: "C007", dimension: "C", intensity: "中", text: "我会仔细检查自己的作业或工作，确保没有细节上的错误" },
  { id: "C008", dimension: "C", intensity: "中", text: "我对数据、统计、账目或结构化信息处理类任务感兴趣" },
  { id: "C009", dimension: "C", intensity: "中", text: "我在意工作的准确性，无法接受因粗心而导致的错误" },
  { id: "C010", dimension: "C", intensity: "中", text: "在混乱或无序的环境中，我的第一反应是重新整理、建立秩序" },
  { id: "C011", dimension: "C", intensity: "高", text: "我有维护详细记录或系统整理信息的习惯，比如分类文件夹或笔记系统" },
  { id: "C012", dimension: "C", intensity: "高", text: "我会自发建立分类体系来管理文件、知识、物品或日程" },
  { id: "C013", dimension: "C", intensity: "高", text: "如果负责一个项目，我会制定详细的时间表、里程碑和检查节点" },
  { id: "C014", dimension: "C", intensity: "高", text: "我享受处理精确数字、财务账目或结构化数据的工作" },
  { id: "C015", dimension: "C", intensity: "高", text: "我认为规范和流程是保证质量的关键，应当严格遵守而不是随意变通" },
  { id: "C016", dimension: "C", intensity: "高", text: "我倾向于在开始任何新任务前先制定完整的计划，而不是边做边想" },
]

const DIMS: RiasecDimension[] = ["R", "I", "A", "S", "E", "C"]

/**
 * Stratified random sampling: draw 3 questions per dimension (1 低, 1 中, 1 高).
 * Returns 18 questions in shuffled dimension order.
 */
export function drawQuestions(): Question[] {
  const result: Question[] = []

  for (const dim of DIMS) {
    const byDim = QUESTION_BANK.filter((q) => q.dimension === dim)
    const low = byDim.filter((q) => q.intensity === "低")
    const mid = byDim.filter((q) => q.intensity === "中")
    const high = byDim.filter((q) => q.intensity === "高")

    const pick = (arr: Question[], n: number) =>
      [...arr].sort(() => Math.random() - 0.5).slice(0, n)

    result.push(...pick(low, 1), ...pick(mid, 1), ...pick(high, 1))
  }

  // Shuffle so same-dimension questions aren't consecutive
  return result.sort(() => Math.random() - 0.5)
}
