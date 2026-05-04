import type { RecommendationItem } from "@/lib/types"

interface MajorCardProps {
  recommendation: RecommendationItem
}

export default function MajorCard({ recommendation }: MajorCardProps) {
  const { rank, similarity_score, major } = recommendation
  const percentage = Math.round(similarity_score * 100)

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex items-center gap-4">
      {/* 排名 */}
      <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">
        <span className="text-indigo-600 font-bold text-sm">{rank}</span>
      </div>

      {/* 专业信息 */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-800 truncate">{major.name}</h3>
        <p className="text-sm text-gray-400 mt-0.5">
          {major.discipline_category} · {major.major_category}
        </p>
      </div>

      {/* 匹配度 */}
      <div className="text-right shrink-0">
        <span className="text-indigo-600 font-bold">{percentage}%</span>
        <p className="text-xs text-gray-400">匹配度</p>
      </div>
    </div>
  )
}
