import Connection from './connection'

const ShowRequestRaw = ({ connection }: { connection: Connection }) => {
  return (
    <div>
      <pre>{connection.request.raw_body}</pre>
    </div>
  )
}

export default ShowRequestRaw
