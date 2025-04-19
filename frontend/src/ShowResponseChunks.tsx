import Connection from './connection';


const ShowResponseChunks = ({ connection }: { connection: Connection }) => {
  return <div>
    {connection.response.chunks && connection.response.chunks.length > 0 ? (
      <>
        <p>Total Chunks: {connection.response.chunks.length}</p>
        <table>
            <thead>
                <tr>
                    <th>Start</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
                {connection.response.chunks.map((chunk) => (
                    <tr key={chunk.start_time}>
                        <td>{chunk.start_time}</td>
                        <td>
                          {chunk.data.map((data) => (
                            <pre key={data}>{data}</pre>
                          ))}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
      </>
    ) : (
        <pre>No chunks</pre>
    )}
  </div>
}

export default ShowResponseChunks;

