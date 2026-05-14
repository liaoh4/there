import Link from "next/link"

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50 to-white flex flex-col items-center justify-center px-6">
      <div className="max-w-lg w-full text-center space-y-8">

        {/* 标题 */}
        <div className="space-y-3">
          <h1 className="text-4xl font-bold text-gray-800">我的专业</h1>
          <p className="text-gray-500 text-lg">
            兴趣匹配 × RIASEC 分析
            <br />
            帮你找到最适合的大学专业
          </p>
        </div>

        {/* 说明卡片 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 text-left space-y-4">
          <h2 className="font-semibold text-gray-700">测评说明</h2>
          <ul className="space-y-2 text-sm text-gray-500">
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 mt-0.5">•</span>
              两阶段测评，兴趣+能力分析 (约10分钟)
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 mt-0.5">•</span>
              综合两项结果推荐最匹配的专业,并提供详细的分析报告和AI解读
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-400 mt-0.5">•</span>
              完全匿名，无需注册登录
            </li>
          </ul>
        </div>

        {/* 开始按钮 */}
        <Link
          href="/assessment"
          className="block w-full py-4 bg-indigo-600 text-white text-center rounded-2xl font-semibold text-lg hover:bg-indigo-700 transition-colors"
        >
          开始测评
        </Link>

        <p className="text-xs text-gray-300">Major Compass v2</p>
      </div>
    </main>
  )
}
