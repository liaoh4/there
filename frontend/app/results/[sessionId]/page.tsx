import { notFound } from "next/navigation"

import MajorCard from "@/components/results/MajorCard"
import RiasecRadar from "@/components/results/RiasecRadar"
import { getResult } from "@/lib/api"
import { DIMENSION_MAP } from "@/lib/riasec"
import type { RiasecDimension } from "@/lib/types"

interface Props {
  params: Promise<{ sessionId: string }>
}

export default async function ResultsPage({ params }: Props) {
  const { sessionId } = await params

  let result
  try {
    result = await getResult(sessionId)
  } catch {
    notFound()
  }

  const { riasec_scores, recommendations } = result
  const dominant = DIMENSION_MAP[riasec_scores.dominant_type as RiasecDimension]
  const topTwo = riasec_scores.top_two.map((d) => DIMENSION_MAP[d as RiasecDimension])

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-lg mx-auto space-y-8">

        {/* 标题 */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800">你的测评结果</h1>
          <p className="text-gray-400 mt-1 text-sm">基于 RIASEC 职业兴趣理论</p>
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

        {/* 专业推荐 */}
        <div>
          <h3 className="font-semibold text-gray-700 mb-3">推荐专业</h3>
          <div className="space-y-3">
            {recommendations.map((rec) => (
              <MajorCard key={rec.rank} recommendation={rec} />
            ))}
          </div>
        </div>

      </div>
    </main>
  )
}
