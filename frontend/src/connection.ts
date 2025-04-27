type Connection = {
  id: string
  active: boolean
  source_ip: string
  source_port: number
  destination_ip: string
  destination_port: number
  created_at: string
  ended_at: string
  request: {
    path: string
    method: string
    http_version: string
    headers: Record<string, string>
    raw_body: string
    body: string | Record<string, unknown>
  }
  response: {
    status_code: number
    status_message: string
    headers: Record<string, string>
    raw_body: string
    body: string | Record<string, unknown>
    chunks: {
      start_time: string
      end_time: string
      data: string[]
    }[]
    sse_messages: {
      start_time: string
      end_time: string
      id: string | null
      data: string | Record<string, unknown>
      event: string | null
      retry: number | null
      comments: string[] | null
    }[]
  }
}

export default Connection
