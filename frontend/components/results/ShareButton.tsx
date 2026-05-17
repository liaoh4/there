'use client'

import { useState } from "react"


export default function ShareButton({url}:{url: string} ) {
    const [copied, setCopied  ] = useState(false)

    return (
        <button
            onClick={async () => {
                if(navigator.share){
                    await navigator.share({
                        title: '我的专业测评结果',
                        url: url
                    })
                }else{
                    navigator.clipboard.writeText(url)
                    setCopied(true)
                    setTimeout(() => setCopied(false), 2000)

                }     
               
            }}
            className="flex-1 py-3 bg-indigo-600 text-white text-center rounded-2xl font-semibold hover:bg-indigo-700 transition-colors"

        >
            {copied ? "已复制！" : "分享结果"}
        </button>
    )

}