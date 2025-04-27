import Connection from './connection'

const ShowResponseRaw = ({ connection }: { connection: Connection }) => {
  return (
    <div>
      <pre>{connection.response.raw_body}</pre>
    </div>
  )
}

export default ShowResponseRaw
