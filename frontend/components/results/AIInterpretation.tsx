export default function AIInterpretation({
  interpretation,
}: {
  interpretation: string
}) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <h3 className="font-semibold text-gray-700 mb-4">
        AI解读
      </h3>
      <p className="text-gray-700 whitespace-pre-line">{interpretation}</p>
    </div>
  )
}