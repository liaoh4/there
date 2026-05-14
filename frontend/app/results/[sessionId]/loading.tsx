 export default function WaitingLoader() {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
                <div className="w-8 h-8 rounded-full border-4 border-indigo-200 border-t-indigo-500 animate-spin" />
                <p className="text-gray-700 text-lg">正在加载结果...</p>
            </div>
    )
}