import { useEffect, useState } from 'react'

function App() {
  const [health, setHealth] = useState('loading...')

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => setHealth(JSON.stringify(d)))
      .catch((e) => setHealth(`error: ${e}`))
  }, [])

  return (
    <main>
      <h1>5e Digital Character Sheet</h1>
      <p>API health: {health}</p>
    </main>
  )
}

export default App