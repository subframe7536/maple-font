import { useState } from 'react'

document.createTextNode('::-webkit-scrollbar { display: none; }')

const App: React.FC = () => {
  const [count, setCount] = useState(0)

  return (
    <div className={styles.app}>
      <img
        src={electron}
        style={{ height: '24vw' }}
        className={styles.appLogo}
        alt='electron'
      />
    </div>
  )
}

export default App
