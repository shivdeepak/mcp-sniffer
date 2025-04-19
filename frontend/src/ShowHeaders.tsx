import Connection from './connection'

const ShowHeaders = ({ connection }: { connection: Connection }) => {
    return <div>
        <p><b>General</b></p>
        <table className="w-full table-auto border-collapse text-sm">
            <tbody>
                <tr>
                    <td className="px-2">HTTP Version:</td>
                    <td className="px-2">{connection.request.http_version}</td>
                </tr>
                <tr>
                    <td className="px-2">Request Method:</td>
                    <td className="px-2">{connection.request.method}</td>
                </tr>
                <tr>
                    <td className="px-2">Status Code:</td>
                    <td className="px-2 flex flex-row items-center">
                        <div className={`w-2 h-2 m-1.5 rounded-full ${
                                connection.response.status_code >= 500 ? 'bg-red-500' :
                                connection.response.status_code >= 400 ? 'bg-orange-500' :
                                connection.response.status_code >= 300 ? 'bg-blue-500' :
                                'bg-green-500'
                            }`}></div>
                        <div className="text-sm pl-2">{connection.response.status_code}</div>
                        <div className="text-sm pl-2">{connection.response.status_message}</div>
                    </td>
                </tr>
                <tr>
                    <td className="px-2">Remote Address:</td>
                    <td className="px-2">{connection.destination_ip}:{connection.destination_port}</td>
                </tr>
            </tbody>
        </table>
        <p><b>Request Headers</b></p>
        <table className="w-full table-auto border-collapse text-sm">
            <tbody>
                {Object.entries(connection.request.headers).map(([key, value]) => (
                    <tr key={key}>
                        <td className="px-2">{key}</td>
                        <td className="px-2">{value}</td>
                    </tr>
                ))}
            </tbody>
        </table>
        <p><b>Response Headers</b></p>
        <table className="w-full table-auto border-collapse text-sm">
            <tbody>
                {Object.entries(connection.response.headers).map(([key, value]) => (
                    <tr key={key}>
                        <td className="px-2">{key}</td>
                        <td className="px-2">{value}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
}

export default ShowHeaders
