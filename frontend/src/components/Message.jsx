import '../styles/Message.css'

function Message({ message }) {
  const isUser = message.type === 'user'

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-content">
        <p className="message-text">{message.text}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <h4>Sources:</h4>
            <ul className="sources-list">
              {message.sources.map((source, index) => (
                <li key={index} className="source-item">
                  <a href={`https://pubmed.ncbi.nlm.nih.gov/${source.pmid}`} target="_blank" rel="noopener noreferrer" className="source-title">
                    {source.title}
                  </a>
                  <div className="source-meta">
                    <span className="pmid">PMID: {source.pmid}</span>
                    <span className="relevance">Relevance: {(source.relevance * 100).toFixed(0)}%</span>
                  </div>
                  <p className="source-excerpt">{source.excerpt}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <span className="message-timestamp">{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
    </div>
  )
}

export default Message
