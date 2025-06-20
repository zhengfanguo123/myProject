import React, { useState } from 'react'

const endpoint = 'http://localhost:8000'

function Tool({ title, action, children }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState('')

  const generate = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${endpoint}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(children(input)),
      })
      const data = await res.json()
      setResult(data.result)
    } catch (err) {
      setResult('Error generating content')
    }
    setLoading(false)
  }

  return (
    <div className="bg-white p-4 rounded shadow mb-4">
      <h2 className="text-xl font-bold mb-2">{title}</h2>
      <input
        className="border p-2 w-full mb-2"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter text"
      />
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        onClick={generate}
        disabled={loading}
      >
        {loading ? 'Loading...' : 'Generate'}
      </button>
      {result && (
        <pre className="mt-2 whitespace-pre-wrap">
{result}
        </pre>
      )}
    </div>
  )
}

export default function App() {
  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <h1 className="text-3xl font-bold mb-4">ContentGen Dashboard</h1>
      <Tool title="Generate Product Descriptions" action="generate-description">
        {(input) => ({ product_name: input })}
      </Tool>
      <Tool title="Generate Blog Posts" action="generate-blog">
        {(input) => ({ keyword: input, length: 500 })}
      </Tool>
      <Tool title="Suggest Hashtags" action="generate-tags">
        {(input) => ({ keyword: input })}
      </Tool>
      <Tool title="Translate Text" action="translate">
        {(input) => ({ text: input, target_language: 'English' })}
      </Tool>
    </div>
  )
}
