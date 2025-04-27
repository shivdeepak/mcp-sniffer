import Connection from './connection'

const ShowResponseSSE = ({ connection }: { connection: Connection }) => {
  return (
    <div>
      {connection.response.sse_messages &&
      connection.response.sse_messages.length > 0 ? (
        <>
          <p>Total Events: {connection.response.sse_messages.length}</p>
          <table>
            <thead>
              <tr>
                <th>Start</th>
                <th>Payload</th>
              </tr>
            </thead>
            <tbody>
              {connection.response.sse_messages.map((message) => (
                <tr key={message.start_time}>
                  <td>{message.start_time}</td>
                  <td>
                    {message.id != undefined && <pre>id: {message.id}</pre>}
                    {message.data != undefined && (
                      <pre>
                        data:{' '}
                        {typeof message.data === 'string'
                          ? message.data
                          : JSON.stringify(message.data, null, 2)}
                      </pre>
                    )}
                    {message.event != undefined && (
                      <pre>event: {message.event}</pre>
                    )}
                    {message.retry != undefined && (
                      <pre>retry: {message.retry}</pre>
                    )}
                    {message.comments != undefined && (
                      <pre>comments: {JSON.stringify(message.comments)}</pre>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <div>No SSE messages</div>
      )}
    </div>
  )
}

export default ShowResponseSSE
