import { useState } from "react";

import Connection from './connection'
import ShowHeaders from './ShowHeaders'
import ShowRequestRaw from './ShowRequestRaw'
import ShowResponseRaw from './ShowResponseRaw'
import ShowResponseChunks from './ShowResponseChunks'
import ShowResponseSSE from './ShowResponseSSE'

const TabbedInterface = ({ connection, onClose }: { connection: Connection, onClose: () => void }) => {
  const [activeTab, setActiveTab] = useState("headers");

  const tabs = [
    { id: "headers", label: "Headers" },
    { id: "request-raw", label: "Request (Raw)" },
    { id: "response-raw", label: "Response (Raw)" },
  ];

  if (connection.response.sse_messages && connection.response.sse_messages.length > 0) {
    tabs.push({ id: "response-sse", label: "Response (SSE)" });
  }

  if (connection.response.chunks && connection.response.chunks.length > 0) {
    tabs.push({ id: "response-chunks", label: "Response (Chunks)" });
  }

  return (
    <div className="w-full">
      <div className="flex bg-gray-300">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 text-sm font-medium cursor-pointer ${
              activeTab === tab.id
                ? "bg-gray-500"
                : ""
            }`}
          >
            {tab.label}
          </button>
        ))}
        <button onClick={onClose} className="text-sm flex-1 cursor-pointer">x</button>
      </div>

      <div className="p-4">
        {activeTab === "headers" && <ShowHeaders connection={connection} />}
        {activeTab === "request-raw" && <ShowRequestRaw connection={connection} />}
        {activeTab === "response-raw" && <ShowResponseRaw connection={connection} />}
        {activeTab === "response-sse" && <ShowResponseSSE connection={connection} />}
        {activeTab === "response-chunks" && <ShowResponseChunks connection={connection} />}
      </div>
    </div>
  );
};

export default TabbedInterface;
