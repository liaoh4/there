"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"

import CategoryCard from "@/components/interest/CategoryCard"
import QuestionCard from "@/components/assessment/QuestionCard"
import Progress from "@/components/ui/Progress"
import { useAssessment } from "@/hooks/useAssessment"



export default function AssessmentPage() {
  const router = useRouter()
  const {
    phase,
    isProcessing,
    currentRound,
    currentQuestion,
    questionIndex,
    totalQuestions,
    result,
    errorMsg,
    selectCategory,
    answer,
  } = useAssessment()

  useEffect(() => {
    if (phase === "done" && result) {
      router.push(`/results/${result.session_id}`)
    }
  }, [phase, result, router])

  if (phase === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">准备中...</p>
      </div>
    )
  }

  if (phase === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-500">{errorMsg}</p>
      </div>
    )
  }

  if (phase === "submitting") {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <div className="w-8 h-8 rounded-full border-4 border-indigo-200 border-t-indigo-500 animate-spin" />
        <p className="text-gray-700 mt-4">正在提交你的答案...</p>
      </div>
    )
  }

  // Interest selection phase
  if (phase === "interest" && currentRound) {
    return (
      <main className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-6">
            <p className="text-xs text-indigo-400 font-medium mb-1">
              第一阶段：兴趣探索 · 第 {currentRound.round_number} / 8 轮
            </p>
            <h1 className="text-xl font-bold text-gray-800">最感兴趣的专业？</h1>
            <p className="text-sm text-gray-400 mt-1">
              从以下专业中，选择你最感兴趣的一个
            </p>
          </div>

          <div className="flex flex-col gap-2">
            {currentRound.options.map((opt) => (
              <CategoryCard
                key={opt.category_code}
                option={opt}
                onSelect={selectCategory}
                disabled={isProcessing}
              />
            ))}
          </div>

          <p className="text-center text-xs text-gray-300 mt-6">
            选完 8 轮进入第二阶段
          </p>
        </div>
      </main>
    )
  }

  // RIASEC phase
  if (phase === "riasec" && currentQuestion) {
    return (
      <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-start pt-16 p-6">
        <div className="w-full max-w-lg">
          <div className="text-center mb-2">
            <p className="text-xs text-indigo-400 font-medium">第二阶段：性格与能力分析</p>
          </div>
          <Progress current={questionIndex + 1} total={totalQuestions} />
          <div className="mt-10">
            <QuestionCard
              question={currentQuestion}
              index={questionIndex}
              total={totalQuestions}
              onAnswer={answer}
            />
          </div>
        </div>
      </main>
    )
  }

  return null
}
