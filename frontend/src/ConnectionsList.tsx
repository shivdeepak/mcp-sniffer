// ConnectionsList.tsx
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import Connection from './connection'

interface ConnectionsResponse {
  source_ip: string
  source_port: number
  destination_ip: string
  destination_port: number
  status: string
  version: string
  connections: Connection[]
}

const fetchConnections = async (): Promise<ConnectionsResponse> => {
  const response = await axios.get('/connections')
  return response.data
}

export default function ConnectionsList({ onConnectionSelected, selectedConnection }: { onConnectionSelected: (connection: Connection) => void, selectedConnection: Connection | null }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['connections'],
    queryFn: fetchConnections,
  })

  if (isLoading) return <div>Loading connections...</div>
  if (error instanceof Error) return <div>Error: {error.message}</div>

  return (
    <>
      {!data?.connections || data.connections.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full">
            <div className="text-xl font-bold">MCP Sniffer {data?.version}</div>
            <div className="text-lg mt-5 text-orange-500">No Connections Yet!</div>
            <div className="text-center mt-5">Configure this Sniffer as a Man-in-the-Middle Proxy for your MCP Server to sniff HTTP traffic.</div>

            <div className="text-center mt-5 font-bold">Setup Instructions:</div>
            <div className="text-center mt-2">
                1. Run your MCP Server to listen for connections on <a className="text-blue-500" href={`http://${data?.destination_ip}:${data?.destination_port}`}>http://{data?.destination_ip}:{data?.destination_port}</a>
            </div>
            <div className="text-center mt-2">
                2. Configure your MCP Client to connect to this MCP Sniffer on <a className="text-blue-500" href={`http://${data?.source_ip}:${data?.source_port}`}>http://{data?.source_ip}:{data?.source_port}</a>
            </div>
        </div>
      ) : (
        <div>
          <div className="font-bold p-2">MCP Sniffer {data?.version}</div>
          <table className="w-full table-auto border-collapse text-sm">
              <thead className="bg-gray-300">
                  <tr>
                      <th className="text-left p-2">Method</th>
                      <th className="text-left p-2">Status</th>
                      <th className="text-left p-2">Timestamp</th>
                      <th className="text-left p-2">Active</th>
                      <th className="text-left p-2">Path</th>
                  </tr>
              </thead>
              <tbody>
                  {data.connections.map((conn) => (
                  <tr key={conn.created_at}
                      className={`cursor-pointer select-none hover:bg-gray-300 ${selectedConnection?.created_at === conn.created_at ? 'bg-gray-100' : ''}`}
                      onClick={() => onConnectionSelected(conn)}>
                      <td className="text-left p-2">{conn.request.method}</td>
                      <td className="text-left p-2 flex flex-row">
                          <div className="flex flex-row items-center">
                              <div className={`w-2 h-2 m-1.5 rounded-full ${
                                  conn.response.status_code >= 500 ? 'bg-red-500' :
                                  conn.response.status_code >= 400 ? 'bg-orange-500' :
                                  conn.response.status_code >= 300 ? 'bg-blue-500' :
                                  'bg-green-500'
                              }`}></div>
                              <div className="mx-0.5">{conn.response.status_code}</div>
                              <div className="mx-0.5">{conn.response.status_message}</div>
                          </div>
                      </td>
                      <td className="text-left p-2">{conn.created_at}</td>
                      <td className="text-left p-2">
                          <div className="flex flex-row items-center">
                              <div className={`w-2 h-2 m-1.5 rounded-full ${
                                  conn.active == true ? 'bg-green-500' : 'bg-red-500'
                              }`}></div>
                              <div className="mx-0.5">{conn.active == true ? 'Connected' : 'Closed'}</div>
                          </div>
                      </td>
                      <td className="text-left p-2">{conn.request.path}</td>
                  </tr>
                  ))}
              </tbody>
          </table>
        </div>
      )}
    </>
  )
}

