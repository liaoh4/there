"use client"

import type { InterestOption } from "@/lib/types"

interface CategoryCardProps {
  option: InterestOption
  onSelect: (categoryCode: string) => void
  disabled?: boolean
}

export default function CategoryCard({ option, onSelect, disabled }: CategoryCardProps) {
  return (
    <button
      onClick={() => onSelect(option.category_code)}
      disabled={disabled}
      className="w-full text-left p-4 rounded-2xl border-2 border-gray-100 bg-white hover:border-indigo-300 hover:bg-indigo-50 active:scale-[0.98] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <h3 className="font-semibold text-gray-800 text-sm leading-snug">
        {option.sample.name.replace(/类$/, "")}
      </h3>
      <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
        {option.sample.description}
      </p>
      {option.sample.typical_representatives && (
        <p className="text-[11px] text-gray-400 mt-1.5">
          代表职业：{option.sample.typical_representatives}
        </p>
      )}
    </button>
  )
}
