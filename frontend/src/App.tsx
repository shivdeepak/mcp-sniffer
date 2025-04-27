import { useState } from 'react'
import ConnectionDetails from './ConnectionDetails'
import ConnectionsList from './ConnectionsList'

import Connection from './connection'

function App() {
  const [selectedConnection, setSelectedConnection] =
    useState<Connection | null>(null)
  return (
    <div className="flex flex-row h-screen w-screen">
      <div className="flex-1 h-screen overflow-y-auto">
        <ConnectionsList
          onConnectionSelected={setSelectedConnection}
          selectedConnection={selectedConnection}
        />
      </div>
      <div
        className={`flex-1 h-screen overflow-y-auto ${selectedConnection ? 'block' : 'hidden'}`}
      >
        {selectedConnection && (
          <ConnectionDetails
            connection={selectedConnection}
            onClose={() => setSelectedConnection(null)}
          />
        )}
      </div>
    </div>
  )
}

export default App
