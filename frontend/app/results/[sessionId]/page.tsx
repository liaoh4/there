import { notFound } from "next/navigation"

import ShareButton from "@/components/results/ShareButton"
import MajorCard from "@/components/results/MajorCard"
import RiasecRadar from "@/components/results/RiasecRadar"
import { getResult } from "@/lib/api"
import { DIMENSION_MAP } from "@/lib/riasec"
import type { RiasecDimension } from "@/lib/types"
import  AIInterpretation from "@/components/results/AIInterpretation"
import Link from "next/link"
// Maps for interest category names
const INTEREST_CATEGORY_NAMES: Record<string, string> = {
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

interface Props {
  params: Promise<{ sessionId: string }>
}

export default async function ResultsPage({ params }: Props) {
  const { sessionId } = await params
  const shareUrl = `${process.env.NEXT_PUBLIC_BASE_URL}/results/${sessionId}`

  let result
  try {
    result = await getResult(sessionId)
  } catch{
    notFound()
  }

  const { riasec_scores, recommendations, interest_scores , ai_interpretation } = result
  const dominant = DIMENSION_MAP[riasec_scores.dominant_type as RiasecDimension]
  const topTwo = riasec_scores.top_two.map((d) => DIMENSION_MAP[d as RiasecDimension])

  // Top 4 interest categories sorted by score
  const topInterests = interest_scores
    ? Object.entries(interest_scores)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 4)
        .map(([code, score]) => ({
          code,
          name: INTEREST_CATEGORY_NAMES[code] ?? code,
          pct: Math.round(score * 100),
        }))
    : []

  const hasConflict = recommendations.some((r) => r.is_conflict)

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-lg mx-auto space-y-8">

        {/* 标题 */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800">你的测评结果</h1>
          <p className="text-gray-400 mt-1 text-sm">
            {interest_scores ? "兴趣匹配 × RIASEC 职业兴趣理论" : "基于 RIASEC 职业兴趣理论"}
          </p>
        </div>

        {/* 主导类型 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm text-center">
          <p className="text-sm text-gray-400 mb-1">你的主导类型</p>
          <h2 className="text-3xl font-bold text-indigo-600">{dominant.name}</h2>
          <p className="text-gray-500 mt-2 text-sm">{dominant.description}</p>
          <div className="flex justify-center gap-2 mt-4">
            {topTwo.map((d) => (
              <span
                key={d.key}
                className="px-3 py-1 rounded-full text-sm font-medium text-white"
                style={{ backgroundColor: d.color }}
              >
                {d.name}
              </span>
            ))}
          </div>
        </div>

        {/* 雷达图 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-700 mb-4">六维分析</h3>
          <RiasecRadar scores={riasec_scores} />
        </div>

        {/* 兴趣画像 */}
        {topInterests.length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-700 mb-4">你的兴趣偏好</h3>
            <div className="space-y-3">
              {topInterests.map(({ code, name, pct }) => (
                <div key={code} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 w-36 shrink-0">{name}</span>
                  <div className="flex-1 bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-indigo-400 h-2 rounded-full transition-all"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400 w-8 text-right">{pct}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 冲突提示 */}
        {hasConflict && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-sm text-amber-700">
            <p className="font-medium mb-1">注意：部分推荐存在兴趣-适配冲突</p>
            <p className="text-amber-600 text-xs">
              标记「兴趣强但适配度偏低」的专业代表你很感兴趣，但 RIASEC
              分析显示适配度相对偏低。选择时可结合个人判断，也可重点关注两项均高的专业。
            </p>
          </div>
        )}

        {/* 专业推荐 */}
        <div>
          <h3 className="font-semibold text-gray-700 mb-3">推荐专业</h3>
          <div className="space-y-3">
            {recommendations.map((rec) => (
              <MajorCard key={rec.rank} recommendation={rec} />
            ))}
          </div>
        </div>

        {/* AI解读 */}
        {ai_interpretation && <AIInterpretation interpretation={ai_interpretation} />}
        
        <div className="flex flex-col gap-3">
          <ShareButton url={shareUrl} />
          <Link href="/assessment" className="flex-1 py-3 text-gray-400 text-center rounded-2xl hover:text-gray-600 transition-colors"

>重新测评</Link>
        </div>

      </div>
    </main>
  )
}
