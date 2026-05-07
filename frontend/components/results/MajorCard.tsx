import type { RecommendationItem } from "@/lib/types"

interface MajorCardProps {
  recommendation: RecommendationItem
}

export default function MajorCard({ recommendation }: MajorCardProps) {
  const { rank, similarity_score, combined_score, interest_score, is_conflict, major } =
    recommendation

  const mainScore = combined_score ?? similarity_score
  const mainPct = Math.round(mainScore * 100)
  const riasecPct = Math.round(similarity_score * 100)
  const interestPct = interest_score != null ? Math.round(interest_score * 100) : null

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-start gap-4">
        {/* 排名 */}
        <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center shrink-0 mt-0.5">
          <span className="text-indigo-600 font-bold text-sm">{rank}</span>
        </div>

        {/* 专业信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-800">{major.name}</h3>
            {is_conflict && (
              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 border border-amber-200 shrink-0">
                兴趣强但适配度偏低
              </span>
            )}
          </div>
          <p className="text-sm text-gray-400 mt-0.5">
            {major.discipline_category} · {major.major_category}
          </p>
          {major.description && (
            <p className="text-xs text-gray-400 mt-1.5 leading-relaxed line-clamp-2">
              {major.description}
            </p>
          )}

          {/* 分项分数 */}
          {interestPct != null && (
            <div className="flex gap-3 mt-2">
              <span className="text-xs text-gray-400">
                RIASEC 适配{" "}
                <span className="text-gray-600 font-medium">{riasecPct}%</span>
              </span>
              <span className="text-xs text-gray-400">
                兴趣契合{" "}
                <span className="text-indigo-500 font-medium">{interestPct}%</span>
              </span>
            </div>
          )}

          {/* 具体专业类 */}
          {recommendation.sub_majors && recommendation.sub_majors.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {recommendation.sub_majors.map((sm) => (
                <span
                  key={sm.code}
                  className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-500 border border-indigo-100"
                >
                  {sm.name}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 综合匹配度 */}
        <div className="text-right shrink-0">
          <span className="text-indigo-600 font-bold text-lg">{mainPct}%</span>
          <p className="text-xs text-gray-400">{combined_score != null ? "综合匹配" : "匹配度"}</p>
        </div>
      </div>
    </div>
  )
}
