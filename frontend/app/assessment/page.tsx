"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"

import QuestionCard from "@/components/assessment/QuestionCard"
import Progress from "@/components/ui/Progress"
import { useAssessment } from "@/hooks/useAssessment"

export default function AssessmentPage() {
  const router = useRouter()
  const {
    phase,
    currentIndex,
    currentQuestion,
    totalQuestions,
    result,
    errorMsg,
    answer,
  } = useAssessment()

  // 测评完成后跳转到结果页
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
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">正在计算结果...</p>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-lg">
        <Progress current={currentIndex + 1} total={totalQuestions} />
        <div className="mt-10">
          <QuestionCard
            question={currentQuestion}
            index={currentIndex}
            total={totalQuestions}
            onAnswer={answer}
          />
        </div>
      </div>
    </main>
  )
}
